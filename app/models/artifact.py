"""
artifact.py

What it does: Defines the Artifact model for storing generated architecture documents.

Dependencies: datetime, uuid (standard library)
"""

from datetime import datetime
import uuid
from typing import Optional, Dict, Any


class Artifact:
    """Represents a generated architecture artifact."""

    def __init__(self, project_id: str, phase: str, name: str,
                 content: str, artifact_type: str = "document"):
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.phase = phase
        self.name = name
        self.content = content
        self.artifact_type = artifact_type
        self.version = 1
        self.created_at = datetime.utcnow()
        self.s3_key: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def to_dict(self, include_content: bool = True) -> Dict:
        """Convert artifact to dictionary for API responses."""
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'phase': self.phase,
            'name': self.name,
            'artifact_type': self.artifact_type,
            'version': self.version,
            'created_at': self.created_at.isoformat()
        }
        if include_content:
            result['content'] = self.content
        if self.s3_key:
            result['s3_key'] = self.s3_key
        return result

    def increment_version(self):
        """Increment artifact version."""
        self.version += 1