An AI-powered enterprise architecture tool that guides users through the TOGAF ADM process and analyzes business processes for automation opportunities.

## Features

- 📋 Complete TOGAF ADM phase management
- 🤖 AI-powered artifact generation (AWS Bedrock)
- 🔍 Process analysis with automation recommendations
- 💾 PostgreSQL (prod) / SQLite (dev) persistence
- ☁️ S3 storage for artifacts (optional)
- 🐳 Docker support

## Quick Start

### Local Development

```bash
# Clone the repository
git clone <your-repo>
cd togaf-orchestrator

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

# Open http://localhost:8000