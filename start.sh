#!/usr/bin/env bash
# Start script for Smart Event Planner

echo "Starting Smart Event Planner..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 