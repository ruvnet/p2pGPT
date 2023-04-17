#!/bin/bash

# Run the FastAPI app in the background
uvicorn main:app --host 0.0.0.0 --port 8080 &

# Run the CLI script in /scripts/main.py in the foreground
# python -m autogpt --continuous
# python autogpt --use-memory pinecone

# Wait for all background processes to complete
wait