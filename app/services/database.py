"""
database.py

What it does: Provides database connection and CRUD operations for all models.
             Handles both SQLite (dev) and PostgreSQL (prod) with simple interface.

Dependencies: sqlalchemy, os, models.*
"""

import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ..config import config
from ..models.project import Project
from ..models.artifact import Artifact
from ..models.analysis import ProcessAnalysis, AgentBlueprint

# SQLAlchemy setup
Base = declarative_base()


class ProjectDB(Base):
    """SQLAlchemy model for projects table."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    sponsor = Column(String)
    description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(String)
    completed_phases = Column(JSON)  # List of phase names
    metadata_json = Column(JSON)  # Additional metadata


class ArtifactDB(Base):
    """SQLAlchemy model for artifacts table."""
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True)
    project_id = Column(String, index=True)
    phase = Column(String)
    name = Column(String)
    artifact_type = Column(String)
    content = Column(Text)
    version = Column(Integer)
    created_at = Column(DateTime)
    s3_key = Column(String, nullable=True)
    metadata_json = Column(JSON)


class AnalysisDB(Base):
    """SQLAlchemy model for process analyses table."""
    __tablename__ = "process_analyses"

    id = Column(String, primary_key=True)
    project_id = Column(String, index=True)
    process_name = Column(String)
    process_description = Column(Text)
    steps = Column(JSON)
    opportunities = Column(JSON)
    blueprints = Column(JSON)
    created_at = Column(DateTime)
    metadata_json = Column(JSON)


class DatabaseService:
    """Service for database operations."""

    def __init__(self):
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()

    def _create_engine(self):
        """Create database engine based on environment."""
        if config.is_production:
            return create_engine(
                config.DATABASE_URL,
                pool_size=5,
                max_overflow=10
            )
        else:
            # SQLite for development
            return create_engine(
                config.DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )

    def _create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self):
        """Get a database session."""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # Project operations
    def save_project(self, project: Project):
        """Save or update a project."""
        with self.session() as db:
            project_db = ProjectDB(
                id=project.id,
                name=project.name,
                sponsor=project.sponsor,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
                status=project.status,
                completed_phases=project.completed_phases,
                metadata_json=project.metadata
            )
            db.merge(project_db)

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        with self.session() as db:
            project_db = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
            if not project_db:
                return None

            project = Project(
                name=project_db.name,
                sponsor=project_db.sponsor,
                description=project_db.description
            )
            project.id = project_db.id
            project.created_at = project_db.created_at
            project.updated_at = project_db.updated_at
            project.status = project_db.status
            project.completed_phases = project_db.completed_phases or []
            project.metadata = project_db.metadata_json or {}
            return project

    def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        with self.session() as db:
            project_dbs = db.query(ProjectDB).all()
            projects = []
            for p in project_dbs:
                project = Project(p.name, p.sponsor, p.description)
                project.id = p.id
                project.created_at = p.created_at
                project.updated_at = p.updated_at
                project.status = p.status
                project.completed_phases = p.completed_phases or []
                project.metadata = p.metadata_json or {}
                projects.append(project)
            return projects

    # Artifact operations
    def save_artifact(self, artifact: Artifact):
        """Save an artifact."""
        with self.session() as db:
            artifact_db = ArtifactDB(
                id=artifact.id,
                project_id=artifact.project_id,
                phase=artifact.phase,
                name=artifact.name,
                artifact_type=artifact.artifact_type,
                content=artifact.content,
                version=artifact.version,
                created_at=artifact.created_at,
                s3_key=artifact.s3_key,
                metadata_json=artifact.metadata
            )
            db.add(artifact_db)

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID."""
        with self.session() as db:
            artifact_db = db.query(ArtifactDB).filter(ArtifactDB.id == artifact_id).first()
            if not artifact_db:
                return None

            artifact = Artifact(
                project_id=artifact_db.project_id,
                phase=artifact_db.phase,
                name=artifact_db.name,
                content=artifact_db.content,
                artifact_type=artifact_db.artifact_type
            )
            artifact.id = artifact_db.id
            artifact.version = artifact_db.version
            artifact.created_at = artifact_db.created_at
            artifact.s3_key = artifact_db.s3_key
            artifact.metadata = artifact_db.metadata_json or {}
            return artifact

    def list_project_artifacts(self, project_id: str) -> List[Artifact]:
        """List all artifacts for a project."""
        with self.session() as db:
            artifact_dbs = db.query(ArtifactDB).filter(
                ArtifactDB.project_id == project_id
            ).all()

            artifacts = []
            for a in artifact_dbs:
                artifact = Artifact(
                    project_id=a.project_id,
                    phase=a.phase,
                    name=a.name,
                    content=a.content,
                    artifact_type=a.artifact_type
                )
                artifact.id = a.id
                artifact.version = a.version
                artifact.created_at = a.created_at
                artifact.s3_key = a.s3_key
                artifact.metadata = a.metadata_json or {}
                artifacts.append(artifact)
            return artifacts

    # Analysis operations
    def save_analysis(self, analysis: ProcessAnalysis):
        """Save a process analysis."""
        with self.session() as db:
            analysis_db = AnalysisDB(
                id=analysis.id,
                project_id=analysis.project_id,
                process_name=analysis.process_name,
                process_description=analysis.process_description,
                steps=analysis.steps,
                opportunities=analysis.opportunities,
                blueprints=[b.to_dict() for b in analysis.blueprints],
                created_at=analysis.created_at,
                metadata_json=analysis.metadata
            )
            db.add(analysis_db)

    def get_analysis(self, analysis_id: str) -> Optional[ProcessAnalysis]:
        """Get an analysis by ID."""
        with self.session() as db:
            analysis_db = db.query(AnalysisDB).filter(AnalysisDB.id == analysis_id).first()
            if not analysis_db:
                return None

            analysis = ProcessAnalysis(
                project_id=analysis_db.project_id,
                process_name=analysis_db.process_name,
                process_description=analysis_db.process_description
            )
            analysis.id = analysis_db.id
            analysis.created_at = analysis_db.created_at
            analysis.steps = analysis_db.steps or []
            analysis.opportunities = analysis_db.opportunities or []
            analysis.metadata = analysis_db.metadata_json or {}

            # Convert blueprints back to objects
            for b in analysis_db.blueprints or []:
                blueprint = AgentBlueprint(
                    name=b['name'],
                    purpose=b['purpose'],
                    input_data=b['input_data'],
                    output_actions=b['output_actions'],
                    decision_logic=b['decision_logic'],
                    integration_points=b['integration_points'],
                    automation_score=b['automation_score'],
                    estimated_roi=b['estimated_roi']
                )
                blueprint.id = b['id']
                analysis.blueprints.append(blueprint)

            return analysis

    def list_project_analyses(self, project_id: str) -> List[ProcessAnalysis]:
        """List all analyses for a project."""
        with self.session() as db:
            analysis_dbs = db.query(AnalysisDB).filter(
                AnalysisDB.project_id == project_id
            ).all()

            analyses = []
            for a in analysis_dbs:
                analysis = ProcessAnalysis(
                    project_id=a.project_id,
                    process_name=a.process_name,
                    process_description=a.process_description
                )
                analysis.id = a.id
                analysis.created_at = a.created_at
                analysis.steps = a.steps or []
                analysis.opportunities = a.opportunities or []
                analysis.metadata = a.metadata_json or {}
                analyses.append(analysis)
            return analyses