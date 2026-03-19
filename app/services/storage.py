"""
storage.py

What it does: Provides S3 storage for large artifacts. Falls back to local storage
             in development or when AWS is unavailable.

Dependencies: boto3, os, pathlib
"""

import os
import boto3
from pathlib import Path
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError

from ..config import config


class StorageService:
    """Service for storing and retrieving artifacts."""

    def __init__(self):
        self.s3 = None
        self.use_s3 = False
        self.local_path = Path("./data/artifacts")
        self._initialize()

    def _initialize(self):
        """Initialize storage backend."""
        # Always create local storage
        self.local_path.mkdir(parents=True, exist_ok=True)

        # Try to initialize S3 if credentials exist
        if config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY:
            try:
                self.s3 = boto3.client(
                    's3',
                    region_name=config.AWS_REGION,
                    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
                )
                # Test bucket access
                self.s3.head_bucket(Bucket=config.ARTIFACT_BUCKET)
                self.use_s3 = True
                print(f"✅ S3 storage initialized (bucket: {config.ARTIFACT_BUCKET})")
            except Exception as e:
                print(f"⚠️ S3 not available, using local storage: {e}")
                self.use_s3 = False

    def save_artifact(self, artifact_id: str, content: str,
                      content_type: str = "text/markdown") -> Optional[str]:
        """Save an artifact, return the storage location."""
        if self.use_s3:
            return self._save_to_s3(artifact_id, content, content_type)
        else:
            return self._save_to_local(artifact_id, content)

    def get_artifact(self, artifact_id: str) -> Optional[str]:
        """Retrieve an artifact by ID."""
        if self.use_s3:
            return self._get_from_s3(artifact_id)
        else:
            return self._get_from_local(artifact_id)

    def _save_to_s3(self, artifact_id: str, content: str,
                    content_type: str) -> str:
        """Save artifact to S3."""
        key = f"artifacts/{artifact_id}.md"
        self.s3.put_object(
            Bucket=config.ARTIFACT_BUCKET,
            Key=key,
            Body=content.encode('utf-8'),
            ContentType=content_type
        )
        return f"s3://{config.ARTIFACT_BUCKET}/{key}"

    def _get_from_s3(self, artifact_id: str) -> Optional[str]:
        """Retrieve artifact from S3."""
        key = f"artifacts/{artifact_id}.md"
        try:
            response = self.s3.get_object(
                Bucket=config.ARTIFACT_BUCKET,
                Key=key
            )
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise

    def _save_to_local(self, artifact_id: str, content: str) -> str:
        """Save artifact locally."""
        file_path = self.local_path / f"{artifact_id}.md"
        file_path.write_text(content, encoding='utf-8')
        return str(file_path)

    def _get_from_local(self, artifact_id: str) -> Optional[str]:
        """Retrieve artifact from local storage."""
        file_path = self.local_path / f"{artifact_id}.md"
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        return None