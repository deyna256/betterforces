"""Codeforces API domain models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from sources.domain.models.base import BaseDomainModel


class SubmissionStatus(str, Enum):
    """Submission status enumeration."""

    OK = "OK"  # Accepted
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    IDLENESS_LIMIT_EXCEEDED = "IDLENESS_LIMIT_EXCEEDED"


@dataclass
class Problem(BaseDomainModel):
    """Codeforces problem model."""

    contest_id: int
    index: str
    name: str
    rating: Optional[int] = None
    tags: List[str] = field(default_factory=list)

    @property
    def problem_key(self) -> str:
        """Unique identifier for a problem."""
        return f"{self.contest_id}{self.index}"


@dataclass
class Submission(BaseDomainModel):
    """Codeforces submission model."""

    id: int
    contest_id: int
    creation_time_seconds: int
    problem: Problem
    verdict: SubmissionStatus
    programming_language: str

    @property
    def is_solved(self) -> bool:
        """Check if the submission was accepted."""
        return self.verdict == SubmissionStatus.OK
