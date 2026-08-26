# ============================================
# PPR IRELAND - DOCKER CONTAINER
# ============================================
# Builds a container with the FastAPI app
# and XGBoost model ready to serve predictions
# ============================================

# Start from a lightweight Python 3.9 image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first
# Docker caches this layer so rebuilds are faster
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the api folder containing the model and app
COPY api/ ./api/

# Expose port 8000 so the outside world can reach the API
EXPOSE 8000

# Command to run when the container starts
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]