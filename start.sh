#!/bin/bash
cd backend
export PYTHONPATH=/app/backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT