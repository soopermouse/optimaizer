"""
config.py

What it does: Loads and validates environment variables, provides configuration
             settings for the entire application. Centralizes all configuration
             so other files don't need to access env vars directly.

Dependencies: os, dotenv
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


class Config:
    """Application configuration settings."""

    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = ENVIRONMENT == 'development'

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./togaf.db')

    # AWS
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    BEDROCK_MODEL = os.getenv('BEDROCK_MODEL', 'anthropic.claude-3-sonnet-20240229')

    # Storage
    ARTIFACT_BUCKET = os.getenv('ARTIFACT_BUCKET', 'togaf-artifacts')

    # App
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == 'production'

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == 'development'


# Global config instance
config = Config()