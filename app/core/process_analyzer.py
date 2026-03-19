"""
process_analyzer.py

What it does: Analyzes business processes to identify automation opportunities
             and generate AI agent blueprints.

Dependencies: typing, models.analysis
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime

from ..models.analysis import ProcessAnalysis, AgentBlueprint
from ..services.bedrock import BedrockService


class ProcessAnalyzer:
    """Analyzes business processes for automation opportunities."""

    def __init__(self, bedrock: Optional[BedrockService] = None):
        self.bedrock = bedrock
        self.analyses: Dict[str, ProcessAnalysis] = {}

    def analyze(self, project_id: str, process_name: str,
                process_description: str) -> ProcessAnalysis:
        """Analyze a business process."""
        analysis = ProcessAnalysis(project_id, process_name, process_description)

        # Parse steps
        steps = self._parse_steps(process_description)
        analysis.steps = steps

        # Try Bedrock first
        if self.bedrock and self.bedrock.is_available:
            bedrock_result = self.bedrock.analyze_process(process_description, steps)
            if bedrock_result:
                try:
                    result_json = json.loads(bedrock_result)
                    self._process_bedrock_result(analysis, result_json)
                    self.analyses[analysis.id] = analysis
                    return analysis
                except:
                    pass

        # Fallback to rule-based analysis
        self._rule_based_analysis(analysis)
        self.analyses[analysis.id] = analysis
        return analysis

    def _parse_steps(self, description: str) -> List[Dict]:
        """Parse process description into steps."""
        lines = [l.strip() for l in description.split('\n') if l.strip()]
        steps = []

        for i, line in enumerate(lines):
            if line and not line.startswith('#'):
                steps.append({
                    'step_number': i + 1,
                    'description': line,
                    'type': self._classify_step(line)
                })
        return steps

    def _classify_step(self, step: str) -> str:
        """Classify a step based on keywords."""
        step_lower = step.lower()

        if any(w in step_lower for w in ['if', 'check', 'verify', 'approve']):
            return 'decision'
        if any(w in step_lower for w in ['enter', 'copy', 'paste', 'move']):
            return 'repetitive'
        if any(w in step_lower for w in ['data', 'record', 'log', 'store']):
            return 'data'
        return 'manual'

    def _rule_based_analysis(self, analysis: ProcessAnalysis):
        """Fallback rule-based analysis when Bedrock unavailable."""
        steps = analysis.steps
        opportunities = []

        # Group by type
        repetitive = [s for s in steps if s['type'] == 'repetitive']
        decisions = [s for s in steps if s['type'] == 'decision']
        data_steps = [s for s in steps if s['type'] == 'data']

        if repetitive:
            blueprint = AgentBlueprint(
                name="Data Entry Automation",
                purpose="Automate repetitive data entry tasks",
                input_data=["Form data", "Source documents"],
                output_actions=["Completed entries", "Processing confirmations"],
                decision_logic="Rule-based RPA",
                integration_points=["UI Automation", "Database"],
                automation_score=min(len(repetitive) * 15, 95),
                estimated_roi="High"
            )
            analysis.add_blueprint(blueprint)
            opportunities.append({
                'type': 'automation',
                'steps': [s['step_number'] for s in repetitive],
                'blueprint_id': blueprint.id
            })

        if decisions:
            blueprint = AgentBlueprint(
                name="Decision Support Agent",
                purpose="Augment complex decision-making with AI",
                input_data=["Request data", "Approval criteria"],
                output_actions=["Recommendations", "Decision summaries"],
                decision_logic="ML classification with rules",
                integration_points=["API Gateway", "Message Queue"],
                automation_score=min(len(decisions) * 10, 90),
                estimated_roi="Medium"
            )
            analysis.add_blueprint(blueprint)
            opportunities.append({
                'type': 'ai_agent',
                'steps': [s['step_number'] for s in decisions],
                'blueprint_id': blueprint.id
            })

        if data_steps:
            blueprint = AgentBlueprint(
                name="Data Integration Agent",
                purpose="Automate data movement and transformation",
                input_data=["Source data", "Transform rules"],
                output_actions=["Transformed data", "Integration status"],
                decision_logic="Deterministic ETL",
                integration_points=["ETL Pipeline", "Data Lake"],
                automation_score=min(len(data_steps) * 12, 85),
                estimated_roi="Medium"
            )
            analysis.add_blueprint(blueprint)
            opportunities.append({
                'type': 'integration',
                'steps': [s['step_number'] for s in data_steps],
                'blueprint_id': blueprint.id
            })

        analysis.opportunities = opportunities

    def _process_bedrock_result(self, analysis: ProcessAnalysis, result: Dict):
        """Process JSON result from Bedrock."""
        # Extract opportunities and blueprints from Bedrock response
        opportunities = result.get('opportunities', [])
        agents = result.get('agents', [])

        for agent_data in agents:
            blueprint = AgentBlueprint(
                name=agent_data.get('name', 'AI Agent'),
                purpose=agent_data.get('purpose', 'Process automation'),
                input_data=agent_data.get('inputs', []),
                output_actions=agent_data.get('outputs', []),
                decision_logic=agent_data.get('logic', 'AI-powered'),
                integration_points=agent_data.get('integrations', []),
                automation_score=agent_data.get('score', 80),
                estimated_roi=agent_data.get('roi', 'Medium')
            )
            analysis.add_blueprint(blueprint)

        analysis.opportunities = opportunities
        analysis.metadata['bedrock_used'] = True

    def get_analysis(self, analysis_id: str) -> Optional[ProcessAnalysis]:
        """Get analysis by ID."""
        return self.analyses.get(analysis_id)

    def get_project_analyses(self, project_id: str) -> List[ProcessAnalysis]:
        """Get all analyses for a project."""
        return [a for a in self.analyses.values() if a.project_id == project_id]