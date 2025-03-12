# Disco-Machina - AI-powered Development Team Terminal Client
# Created by Yavuz Topsever (https://github.com/yavuztopsever)
#
# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make sure the package is installed in development mode
RUN pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Note: OPENAI_API_KEY should be provided at runtime or via environment variables

# Expose port for the API server
EXPOSE 8000

# Set entrypoint for running the server by default
ENTRYPOINT ["python", "-m", "src.dev_team.main"]

# Default command is to run the server
CMD ["server"]