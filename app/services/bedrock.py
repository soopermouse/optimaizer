"""
bedrock.py

What it does: Provides AWS Bedrock integration for AI-powered content generation.
             Handles authentication, retries, and fallbacks.

Dependencies: boto3, json, tenacity
"""

import json
import boto3
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import config


class BedrockService:
    """Service for interacting with AWS Bedrock models."""

    def __init__(self):
        self.client = None
        self.is_available = False
        self._initialize()

    def _initialize(self):
        """Initialize Bedrock client if credentials are available."""
        if not config.AWS_ACCESS_KEY_ID or not config.AWS_SECRET_ACCESS_KEY:
            print("⚠️ AWS credentials not found")
            return

        try:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )
            # Test connection
            self.client.list_foundation_models()
            self.is_available = True
            print("✅ AWS Bedrock initialized")
        except Exception as e:
            print(f"❌ AWS Bedrock initialization failed: {e}")
            self.is_available = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ClientError)
    )
    def _invoke_model(self, prompt: str, max_tokens: int = 2000,
                      temperature: float = 0.7) -> Optional[str]:
        """Invoke Bedrock model with retry logic."""
        if not self.is_available:
            return None

        try:
            response = self.client.invoke_model(
                modelId=config.BEDROCK_MODEL,
                contentType='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )

            result = json.loads(response['body'].read())
            return result['content'][0]['text']

        except Exception as e:
            print(f"Bedrock invocation error: {e}")
            raise

    def generate_artifact(self, phase: str, artifact_name: str,
                          context: Dict[str, Any]) -> Optional[str]:
        """Generate an architecture artifact."""
        prompt = self._build_artifact_prompt(phase, artifact_name, context)
        return self._invoke_model(prompt)

    def analyze_process(self, process_description: str,
                        steps: List[Dict]) -> Optional[str]:
        """Analyze a business process."""
        prompt = self._build_analysis_prompt(process_description, steps)
        return self._invoke_model(prompt, max_tokens=2500)

    def _build_artifact_prompt(self, phase: str, artifact_name: str,
                               context: Dict) -> str:
        """Build prompt for artifact generation."""
        return f"""You are an expert enterprise architect following TOGAF methodology.
Generate a professional {artifact_name} for the {phase} phase.

Context:
{json.dumps(context, indent=2)}

The artifact should include:
1. Header with project name and date
2. Executive summary
3. Key findings and decisions
4. Detailed analysis
5. Recommendations
6. Next steps

Format in Markdown with clear sections."""

    def _build_analysis_prompt(self, description: str, steps: List[Dict]) -> str:
        """Build prompt for process analysis."""
        steps_text = "\n".join([f"{s['step_number']}. {s['description']}" for s in steps])
        return f"""You are an expert in business process automation.
Analyze this process and identify automation opportunities.

Process: {description}

Steps:
{steps_text}

Identify:
1. Which steps can be fully automated (RPA)
2. Which steps need AI augmentation
3. What AI agents could be built
4. Automation score (0-100)
5. Estimated ROI

Return as JSON."""