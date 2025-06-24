# Use official Python image
FROM python:3.9-slim

# Install system dependencies for Playwright and other requirements
RUN apt-get update && \
    apt-get install -y \
    wget \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-noto \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Pipfiles first to leverage Docker cache
COPY Pipfile Pipfile.lock ./

# Install pipenv and project dependencies
RUN pip install pipenv && \
    pipenv install --system --deploy

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps

# Copy the rest of the application
COPY . .

# Expose the port Uvicorn will run on
EXPOSE 10000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]