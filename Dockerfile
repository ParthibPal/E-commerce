# Use Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for web traffic
EXPOSE 8000

# Start the app using gunicorn
CMD ["gunicorn", "app:app"]
