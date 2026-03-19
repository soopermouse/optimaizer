"""
project.py

What it does: Defines the Project model representing an architecture project.
             Handles project state, metadata, and phase completion tracking.

Dependencies: datetime, uuid (standard library only)
"""

from datetime import datetime
import uuid
from typing import Dict, List, Optional, Any


class Project:
    """Represents an enterprise architecture project."""

    def __init__(self, name: str, sponsor: str, description: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.sponsor = sponsor
        self.description = description or ""
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = "active"
        self.completed_phases: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict:
        """Convert project to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'sponsor': self.sponsor,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'completed_phases': self.completed_phases.copy()
        }

    def complete_phase(self, phase: str):
        """Mark a phase as completed."""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
            self.updated_at = datetime.utcnow()

    def is_phase_completed(self, phase: str) -> bool:
        """Check if a phase is completed."""
        return phase in self.completed_phases