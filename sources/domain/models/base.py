from dataclasses import asdict, dataclass


@dataclass
class BaseDomainModel:
    """Base class for all domain models."""

    def to_dict(self):
        """Convert the domain model to a dictionary."""
        return asdict(self)
