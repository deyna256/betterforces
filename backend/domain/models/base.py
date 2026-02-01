from dataclasses import asdict, dataclass


@dataclass
class BaseDomainModel:
    """Base class for all domain models."""

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return asdict(self)
