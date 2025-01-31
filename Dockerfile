# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install PyJWT==2.8.0 python-jose

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 5007

# Health check
HEALTHCHECK --interval=10s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5007/api/payment/health || exit 1

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5007", "--reload"]