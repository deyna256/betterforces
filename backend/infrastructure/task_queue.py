"""Task queue service for asynchronous job processing."""

import json
import time
import uuid
from typing import Optional

from redis.asyncio import Redis


class TaskQueue:
    """
    Manages task queue for fetching Codeforces submissions asynchronously.

    Provides atomic deduplication using SETNX to prevent duplicate tasks
    for the same handle, with support for task status tracking.
    """

    def __init__(self, redis: Redis):
        """
        Initialize task queue.

        Args:
            redis: Async Redis client instance
        """
        self.redis = redis
        self.queue_key = "fetch_queue"

    async def enqueue(self, handle: str) -> str:
        """
        Enqueue task with atomic deduplication using SETNX.

        This method atomically checks if a task already exists for the given
        handle and creates a new one only if none exists. This prevents race
        conditions when multiple clients request the same handle simultaneously.

        Args:
            handle: Codeforces user handle

        Returns:
            task_id: UUID of the task (new or existing)

        Flow:
            1. Quick check for existing pending task
            2. Generate new task_id
            3. Atomically try to claim handle using SETNX
            4. If successful, create task in queue
            5. If failed (race condition), return existing task_id
        """
        # Step 1: Quick check for existing pending task
        existing_task_id = await self.redis.get(f"pending_task:{handle}")
        if existing_task_id:
            return existing_task_id.decode()

        # Step 2: Generate new task_id
        task_id = str(uuid.uuid4())

        # Step 3: Atomically try to "claim" the handle (SETNX)
        was_set = await self.redis.set(
            f"pending_task:{handle}",
            task_id,
            ex=60,  # Expire after 60 seconds
            nx=True,  # Set only if Not eXists (atomic!)
        )

        # Step 4: Check if we won the race
        if not was_set:
            # Race condition: someone else created task between step 1 and 3
            existing_task_id = await self.redis.get(f"pending_task:{handle}")
            return existing_task_id.decode() if existing_task_id else task_id

        # Step 5: We successfully claimed handle - create the task
        task_data = {"task_id": task_id, "handle": handle, "timestamp": time.time()}

        # Add to queue
        await self.redis.rpush(self.queue_key, json.dumps(task_data))

        # Set initial status
        await self.redis.setex(f"task:{task_id}:status", 300, "processing")

        # Store handle for reverse lookup (task_id → handle)
        await self.redis.setex(f"task:{task_id}:handle", 300, handle)

        return task_id

    async def get_task_info(self, task_id: str) -> Optional[dict]:
        """
        Get task information including handle for deduplication checks.

        Args:
            task_id: UUID of the task

        Returns:
            Dictionary with task_id, status, and handle, or None if not found
        """
        status = await self.redis.get(f"task:{task_id}:status")
        if not status:
            return None

        handle = await self.redis.get(f"task:{task_id}:handle")

        return {
            "task_id": task_id,
            "status": status.decode(),
            "handle": handle.decode() if handle else None,
        }

    async def get_task_status(self, task_id: str) -> dict:
        """
        Get task status and result.

        Args:
            task_id: UUID of the task

        Returns:
            Dictionary with status and optional result/error data
        """
        status = await self.redis.get(f"task:{task_id}:status")
        if not status:
            return {"status": "not_found"}

        status = status.decode()

        if status == "completed":
            result = await self.redis.get(f"task:{task_id}:result")
            return {"status": "completed", "result": json.loads(result) if result else None}
        elif status == "failed":
            error = await self.redis.get(f"task:{task_id}:error")
            return {"status": "failed", "error": error.decode() if error else "Unknown error"}
        else:
            return {"status": "processing"}
