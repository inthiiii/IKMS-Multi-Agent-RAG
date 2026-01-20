#!/bin/bash

# 1. Start the Backend API in the background (&)
python -m uvicorn src.app.api:app --host 0.0.0.0 --port 8000 &

# 2. Start the Frontend UI in the foreground
streamlit run src/app/ui.py --server.port 8501 --server.address 0.0.0.0