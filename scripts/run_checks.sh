#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=backend .venv/bin/python -m compileall backend/app
(cd frontend && npm run build)
