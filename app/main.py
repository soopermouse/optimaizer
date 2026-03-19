#main.py

#What it does: FastAPI application entry point.Sets up routes, initializes services, and handles web UI rendering.

#Dependencies: fastapi, jinja2, all
#other
#modules
"""

import os
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from .config import config
from .models.phase import ADMPhase, PhaseRegistry
from .services.database import DatabaseService
from .services.bedrock import BedrockService
from .services.storage import StorageService
from .core.togaf_engine import TOGAFEngine
from .core.process_analyzer import ProcessAnalyzer

# Initialize FastAPI
app = FastAPI(title="TOGAF AI Orchestrator", version="0.1.0")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize services
db = DatabaseService()
bedrock = BedrockService()
storage = StorageService()

# Initialize core engines
togaf = TOGAFEngine(bedrock, storage)
analyzer = ProcessAnalyzer(bedrock)

# Store in app state for routes
app.state.db = db
app.state.togaf = togaf
app.state.analyzer = analyzer
app.state.bedrock = bedrock
app.state.storage = storage

# ============================================================================
# Web Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
#Main dashboard.
"""
    projects = db.get_all_projects()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": [p.to_dict() for p in projects],
            "phases": [p.value for p in ADMPhase],
            "phase_forms": {p.value: togaf.get_phase_form(p) for p in ADMPhase}
        }
    )

@app.get("/project/{project_id}", response_class=HTMLResponse)
async def project_dashboard(project_id: str, request: Request):
    """
#Project dashboard.
"""
    project = db.get_project(project_id)
    if not project:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    next_phases = [p.value for p in togaf.get_next_phases(project.completed_phases)]

    return templates.TemplateResponse(
        "project/dashboard.html",
        {
            "request": request,
            "project": project.to_dict(),
            "project_id": project_id,
            "completed_phases": project.completed_phases,
            "next_phases": next_phases,
            "all_phases": [p.value for p in ADMPhase]
        }
    )

@app.get("/project/{project_id}/phase/{phase}", response_class=HTMLResponse)
async def phase_page(project_id: str, phase: str, request: Request):
    """
Phase
input
page.
"""
    project = db.get_project(project_id)
    if not project:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    try:
        phase_enum = ADMPhase(phase)
    except ValueError:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    form = togaf.get_phase_form(phase_enum)
    can_proceed = togaf.validate_phase_input(
        project_id, phase_enum, project.completed_phases
    )

    return templates.TemplateResponse(
        "project/phase.html",
        {
            "request": request,
            "project": project.to_dict(),
            "phase": phase,
            "form": form,
            "can_proceed": can_proceed
        }
    )

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """
Process
analysis
page.
"""
    projects = db.get_all_projects()
    return templates.TemplateResponse(
        "analysis/index.html",
        {
            "request": request,
            "projects": [p.to_dict() for p in projects]
        }
    )

@app.get("/analysis/{analysis_id}", response_class=HTMLResponse)
async def analysis_results(analysis_id: str, request: Request):
    """
Analysis
results
page.
"""
    analysis = analyzer.get_analysis(analysis_id)
    if not analysis:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    return templates.TemplateResponse(
        "analysis/results.html",
        {
            "request": request,
            "analysis": analysis.to_dict()
        }
    )

# ============================================================================
# API Routes
# ============================================================================

@app.post("/api/projects")
async def create_project(request: Request):
    """
Create
a
new
project.
"""
    data = await request.json()

    project = Project(
        name=data.get('name'),
        sponsor=data.get('sponsor'),
        description=data.get('description')
    )

    db.save_project(project)
    return project.to_dict()

@app.get("/api/projects")
async def list_projects():
    """
List
all
projects.
"""
    projects = db.get_all_projects()
    return [p.to_dict() for p in projects]

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """
Get
project
details.
"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()

@app.post("/api/projects/{project_id}/phase/{phase}")
async def submit_phase(project_id: str, phase: str, request: Request):
    """
Submit
phase
data and generate
artifacts.
"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        phase_enum = ADMPhase(phase)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid phase: {phase}")

    data = await request.json()

    # Validate dependencies
    if not togaf.validate_phase_input(project_id, phase_enum, project.completed_phases):
        raise HTTPException(status_code=400, detail="Phase dependencies not met")

    # Save phase data
    togaf.save_phase_data(project_id, phase_enum, data)

    # Generate artifacts
    artifacts = []
    phase_def = PhaseRegistry.get(phase_enum)
    if phase_def:
        for artifact_name in phase_def.artifacts:
            artifact = togaf.generate_artifact(
                project_id, phase_enum, artifact_name, data
            )
            db.save_artifact(artifact)
            artifacts.append(artifact.to_dict())

    # Mark phase complete
    project.complete_phase(phase)
    db.save_project(project)

    return {
        'status': 'success',
        'artifacts': artifacts,
        'next_phases': [p.value for p in togaf.get_next_phases(project.completed_phases)]
    }

@app.get("/api/projects/{project_id}/artifacts")
async def list_artifacts(project_id: str):
    """
List
artifacts
for a project."""
    artifacts = db.list_project_artifacts(project_id)
    return [a.to_dict(include_content=False) for a in artifacts]

@app.get("/api/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get artifact by ID."""
    artifact = db.get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact.to_dict()

@app.post("/api/analyze")
async def analyze_process(request: Request):
    """Analyze a business process."""
    data = await request.json()

    analysis = analyzer.analyze(
        project_id=data['project_id'],
        process_name=data['process_name'],
        process_description=data['process_description']
    )

    # Save to database
    db.save_analysis(analysis)

    return {
        'analysis_id': analysis.id,
        'redirect': f'/analysis/{analysis.id}'
    }

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results."""
    analysis = analyzer.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis.to_dict()

@app.get("/api/analysis/project/{project_id}")
async def get_project_analyses(project_id: str):
    """Get all analyses for a project."""
    analyses = analyzer.get_project_analyses(project_id)
    return [a.to_dict() for a in analyses]

@app.get("/api/status")
async def get_status():
    """Get system status."""
    return {
        'status': 'running',
        'version': '0.1.0',
        'environment': config.ENVIRONMENT,
        'projects': len(db.get_all_projects()),
        'artifacts': len(db.list_project_artifacts('*')),  # Simplified
        'bedrock_available': bedrock.is_available if bedrock else False,
        'storage': 's3' if storage.use_s3 else 'local'
    }