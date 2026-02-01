"""Worker process for fetching Codeforces submissions with rate limiting."""

import asyncio
import json
import logging
import signal
import sys
import time
from typing import Optional

from redis.asyncio import Redis

from backend.infrastructure.codeforces_client import CodeforcesClient, UserNotFoundError
from backend.infrastructure.redis_client import create_redis_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter.

    Allows max 5 requests per second to Codeforces API.
    """

    def __init__(self, max_requests: int = 5, time_window: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire a token, blocking if necessary.

        This method will block until a token is available.
        """
        async with self.lock:
            while True:
                now = time.time()
                elapsed = now - self.last_update

                # Refill tokens based on elapsed time
                self.tokens = min(
                    self.max_requests,
                    self.tokens + (elapsed * self.max_requests / self.time_window),
                )
                self.last_update = now

                if self.tokens >= 1:
                    self.tokens -= 1
                    logger.debug(f"Token acquired. Remaining tokens: {self.tokens:.2f}")
                    return

                # Wait for next token
                wait_time = (1 - self.tokens) * self.time_window / self.max_requests
                logger.debug(f"Rate limit reached. Waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)


class Worker:
    """
    Worker process for fetching Codeforces submissions.

    Processes tasks from Redis queue with rate limiting.
    """

    def __init__(self):
        """Initialize worker."""
        self.redis: Optional[Redis] = None
        self.cf_client: Optional[CodeforcesClient] = None
        self.rate_limiter: Optional[RateLimiter] = None
        self.queue_key = "fetch_queue"
        self.running = True

    async def setup(self) -> None:
        """Initialize Redis client, CF client, and rate limiter."""
        logger.info("Setting up worker...")
        self.redis = await create_redis_client()
        self.cf_client = CodeforcesClient()
        self.rate_limiter = RateLimiter(max_requests=5, time_window=1.0)
        logger.info("Worker setup complete")

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Cleaning up worker...")
        if self.cf_client:
            await self.cf_client.close()
        if self.redis:
            await self.redis.close()
        logger.info("Worker cleanup complete")

    async def process_task(self, task_data: dict) -> None:
        """
        Process a single task.

        Args:
            task_data: Task data from queue
        """
        assert self.redis is not None, "Redis client not initialized"
        assert self.cf_client is not None, "Codeforces client not initialized"
        assert self.rate_limiter is not None, "Rate limiter not initialized"

        task_id = task_data.get("task_id")
        handle = task_data.get("handle")

        if not task_id or not handle:
            logger.error(f"Invalid task data: {task_data}")
            return

        logger.info(f"Processing task {task_id} for handle: {handle}")

        try:
            # Rate limiting
            await self.rate_limiter.acquire()

            # Fetch from CF API
            logger.info(f"Fetching submissions for {handle}")
            submissions = await self.cf_client.get_user_submissions(handle)
            logger.info(f"Fetched {len(submissions)} submissions for {handle}")

            # Store in cache (24h TTL)
            submissions_json = json.dumps([s.to_dict() for s in submissions])
            await self.redis.setex(f"submissions:{handle}", 86400, submissions_json)
            logger.info(f"Cached submissions for {handle} (24h TTL)")

            # Update THIS task
            await self.redis.setex(f"task:{task_id}:status", 300, "completed")
            await self.redis.setex(
                f"task:{task_id}:result",
                300,
                json.dumps({"handle": handle, "submission_count": len(submissions)}),
            )
            logger.info(f"Task {task_id} marked as completed")

            # Check for other pending tasks (deduplication level 3)
            current_pending = await self.redis.get(f"pending_task:{handle}")
            if current_pending and current_pending.decode() != task_id:
                # Update related task
                other_task_id = current_pending.decode()
                await self.redis.setex(f"task:{other_task_id}:status", 300, "completed")
                await self.redis.setex(
                    f"task:{other_task_id}:result",
                    300,
                    json.dumps(
                        {
                            "handle": handle,
                            "submission_count": len(submissions),
                            "completed_by": task_id,
                        }
                    ),
                )
                logger.info(f"Related task {other_task_id} marked as completed")

            # Remove pending_task lock
            await self.redis.delete(f"pending_task:{handle}")
            logger.info(f"Removed pending_task lock for {handle}")

        except UserNotFoundError:
            logger.warning(f"User not found: {handle}")
            await self.redis.setex(f"task:{task_id}:status", 300, "failed")
            await self.redis.setex(
                f"task:{task_id}:error", 300, f"User '{handle}' not found on Codeforces"
            )
            await self.redis.delete(f"pending_task:{handle}")

        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}", exc_info=True)
            await self.redis.setex(f"task:{task_id}:status", 300, "failed")
            await self.redis.setex(f"task:{task_id}:error", 300, str(e))
            await self.redis.delete(f"pending_task:{handle}")

    async def run(self) -> None:
        """
        Main worker loop.

        Continuously polls Redis queue for tasks.
        """
        assert self.redis is not None, "Redis client not initialized"

        logger.info("Worker started. Waiting for tasks...")

        while self.running:
            try:
                # BLPOP: blocking left pop with timeout
                result = await self.redis.blpop([self.queue_key], timeout=5)  # type: ignore[misc]

                if result:
                    _, task_json = result
                    task_data = json.loads(task_json)
                    await self.process_task(task_data)
                else:
                    # Timeout - continue loop
                    logger.debug("No tasks in queue, waiting...")

            except asyncio.CancelledError:
                logger.info("Worker cancelled")
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Avoid tight loop on errors

        logger.info("Worker stopped")

    def stop(self) -> None:
        """Signal worker to stop."""
        logger.info("Stop signal received")
        self.running = False


async def main() -> None:
    """Main entry point for worker."""
    worker = Worker()

    # Setup signal handlers
    loop = asyncio.get_running_loop()

    def signal_handler(sig):
        logger.info(f"Received signal {sig}")
        worker.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler, sig)

    try:
        await worker.setup()
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await worker.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
