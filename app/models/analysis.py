"""
analysis.py

What it does: Defines models for process analysis results and agent blueprints.

Dependencies: datetime, uuid (standard library)
"""

from datetime import datetime
import uuid
from typing import List, Dict, Optional, Any


class AgentBlueprint:
    """Blueprint for an AI agent to be created from process analysis."""

    def __init__(self, name: str, purpose: str,
                 input_data: List[str], output_actions: List[str],
                 decision_logic: str, integration_points: List[str],
                 automation_score: float, estimated_roi: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.purpose = purpose
        self.input_data = input_data
        self.output_actions = output_actions
        self.decision_logic = decision_logic
        self.integration_points = integration_points
        self.automation_score = automation_score
        self.estimated_roi = estimated_roi
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict:
        """Convert blueprint to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'purpose': self.purpose,
            'input_data': self.input_data.copy(),
            'output_actions': self.output_actions.copy(),
            'decision_logic': self.decision_logic,
            'integration_points': self.integration_points.copy(),
            'automation_score': self.automation_score,
            'estimated_roi': self.estimated_roi
        }


class ProcessAnalysis:
    """Results of analyzing a business process."""

    def __init__(self, project_id: str, process_name: str,
                 process_description: str):
        self.id = str(uuid.uuid4())
        self.project_id = project_id
        self.process_name = process_name
        self.process_description = process_description
        self.created_at = datetime.utcnow()
        self.steps: List[Dict] = []
        self.opportunities: List[Dict] = []
        self.blueprints: List[AgentBlueprint] = []
        self.metadata: Dict[str, Any] = {}

    def add_blueprint(self, blueprint: AgentBlueprint):
        """Add an agent blueprint to this analysis."""
        self.blueprints.append(blueprint)

    def to_dict(self) -> Dict:
        """Convert analysis to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'process_name': self.process_name,
            'created_at': self.created_at.isoformat(),
            'steps': self.steps.copy(),
            'opportunities': self.opportunities.copy(),
            'blueprints': [b.to_dict() for b in self.blueprints],
            'metadata': self.metadata.copy()
        }