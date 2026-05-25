## Trademark Notice

"Optimaizer" and associated branding, naming, logos, and platform identity are claimed as trademarks and may not be used commercially without explicit written permission from the project owner.

Trademark rights are asserted by the project author and maintained under applicable intellectual property laws.

---

## Copyright

Copyright (c) 2026 AI Business Services SRL, Romania
AIBUSINESSSERVICES.EU

All rights reserved unless otherwise specified.
developed and maintained by Simona Diana Thrussell PhD
sdthrussell.nl, NXDTech.com

---

## License

Source code licensing terms are defined separately within this repository.

No rights are granted to use the project name, branding, visual identity, or associated trademarks outside the scope of the applicable software license.

---

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
