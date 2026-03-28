FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Expose port for deployment
EXPOSE 10000

# Start the Flask API
CMD ["gunicorn", "server.app:app", "--bind", "0.0.0.0:10000"]
