FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (layer caching — only reinstalls if requirements change)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project into container
COPY . .

# Tell container to listen on port 5000
EXPOSE 5000

# Run with gunicorn — 4 workers, binds to all interfaces on port 5000
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "main:app"]