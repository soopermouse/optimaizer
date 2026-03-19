"""
phase.py

What it does: Defines phase constants and state management for TOGAF ADM phases.
             Handles phase dependencies and form definitions.

Dependencies: enum (standard library)
"""

from enum import Enum
from typing import Dict, List, Optional


class ADMPhase(str, Enum):
    """TOGAF Architecture Development Method phases."""
    PRELIMINARY = "preliminary"
    PHASE_A = "architecture_vision"
    PHASE_B = "business_architecture"
    PHASE_C = "information_systems_architecture"
    PHASE_D = "technology_architecture"
    PHASE_E = "opportunities_and_solutions"
    PHASE_F = "migration_planning"
    PHASE_G = "implementation_governance"
    PHASE_H = "architecture_change"
    REQUIREMENTS = "requirements_management"


class PhaseDefinition:
    """Definition of a single ADM phase with its dependencies and artifacts."""

    def __init__(self, name: ADMPhase, display_name: str,
                 dependencies: List[ADMPhase], artifacts: List[str],
                 form_fields: Dict[str, str]):
        self.name = name
        self.display_name = display_name
        self.dependencies = dependencies
        self.artifacts = artifacts
        self.form_fields = form_fields  # field_name -> field_type


class PhaseRegistry:
    """Registry of all TOGAF phases with their definitions."""

    _phases: Dict[ADMPhase, PhaseDefinition] = {}

    @classmethod
    def register(cls, phase_def: PhaseDefinition):
        """Register a phase definition."""
        cls._phases[phase_def.name] = phase_def

    @classmethod
    def get(cls, phase: ADMPhase) -> Optional[PhaseDefinition]:
        """Get phase definition by enum."""
        return cls._phases.get(phase)

    @classmethod
    def all(cls) -> List[PhaseDefinition]:
        """Get all registered phase definitions."""
        return list(cls._phases.values())

    @classmethod
    def get_dependencies(cls, phase: ADMPhase) -> List[ADMPhase]:
        """Get dependencies for a phase."""
        phase_def = cls.get(phase)
        return phase_def.dependencies if phase_def else []

    @classmethod
    def get_artifacts(cls, phase: ADMPhase) -> List[str]:
        """Get artifacts for a phase."""
        phase_def = cls.get(phase)
        return phase_def.artifacts if phase_def else []


# Register all phases with their definitions
PhaseRegistry.register(PhaseDefinition(
    name=ADMPhase.PRELIMINARY,
    display_name="Preliminary Phase",
    dependencies=[],
    artifacts=["Architecture Principles", "Architecture Repository", "Architecture Capability"],
    form_fields={
        "project_name": "text",
        "project_sponsor": "text",
        "business_drivers": "textarea",
        "architecture_principles": "textarea"
    }
))

PhaseRegistry.register(PhaseDefinition(
    name=ADMPhase.PHASE_A,
    display_name="Phase A: Architecture Vision",
    dependencies=[ADMPhase.PRELIMINARY],
    artifacts=["Statement of Architecture Work", "Architecture Vision", "Stakeholder Map"],
    form_fields={
        "vision_statement": "textarea",
        "stakeholders": "textarea",
        "scope": "textarea",
        "key_requirements": "textarea"
    }
))

# Continue for all phases...