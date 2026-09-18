# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    STREAMLIT_SERVER_HEADLESS=true

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set work directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY pyproject.toml README.md run.py demo.py ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY examples/ ./examples/

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port that Streamlit uses
EXPOSE 8501

# Command to run the application (Streamlit UI)
CMD ["streamlit", "run", "src/ai_test_generator/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
