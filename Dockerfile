# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy and enable the startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose BOTH ports (API and UI)
EXPOSE 8000
EXPOSE 8501

# Run the startup script
CMD ["./start.sh"]