"""Task status API routes."""

import json

from litestar import Controller, get
from litestar.response import Response
from redis.asyncio import Redis

from backend.api.deps import redis_dependency, task_queue_dependency
from backend.infrastructure.task_queue import TaskQueue


class TaskController(Controller):
    """Controller for task status endpoints."""

    path = "/tasks"
    tags = ["Tasks"]

    @get(
        path="/{task_id:str}",
        dependencies={
            "task_queue": task_queue_dependency,
            "redis": redis_dependency,
        },
    )
    async def get_task_status(
        self,
        task_id: str,
        task_queue: TaskQueue,
        redis: Redis,
    ) -> Response:
        """
        Get status of an async task.

        This endpoint allows clients to poll for task completion. It returns:
        - 200 OK with data if task is completed
        - 202 Accepted if task is still processing
        - 404 Not Found if task doesn't exist or expired
        - 500 Internal Server Error if task failed

        Args:
            task_id: UUID of the task to check

        Returns:
            Task status and result/error data
        """
        # Get task info
        task_info = await task_queue.get_task_info(task_id)

        if not task_info:
            return Response(
                content={"error": "Task not found or expired"},
                status_code=404,
            )

        handle = task_info.get("handle")
        status = task_info.get("status")

        # Completed
        if status == "completed":
            result = await redis.get(f"task:{task_id}:result")
            return Response(
                content=json.loads(result) if result else {"status": "completed"},
                status_code=200,
            )

        # Failed
        if status == "failed":
            error = await redis.get(f"task:{task_id}:error")
            return Response(
                content={"error": error.decode() if error else "Unknown error"},
                status_code=500,
            )

        # Still processing - check if cache was updated by another task
        if handle:
            cached = await redis.get(f"submissions:{handle}")
            if cached:
                ttl = await redis.ttl(f"submissions:{handle}")
                if ttl > 0:
                    age = 86400 - ttl

                    if age < 14400:  # Fresh data available!
                        # Mark task as completed
                        await redis.setex(f"task:{task_id}:status", 300, "completed")
                        await redis.setex(
                            f"task:{task_id}:result",
                            300,
                            json.dumps(
                                {
                                    "handle": handle,
                                    "status": "completed_by_another_task",
                                }
                            ),
                        )
                        return Response(
                            content={
                                "status": "completed",
                                "message": "Data updated by concurrent request",
                            },
                            status_code=200,
                        )

        # Still processing
        return Response(
            content={"status": "processing"},
            status_code=202,
            headers={"Retry-After": "2"},
        )
