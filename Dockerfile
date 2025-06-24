FROM python:3.9-slim

# Install system dependencies
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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install pipenv and dependencies
RUN pip install pipenv
RUN pipenv install --deploy --system

# Install Playwright and browsers
RUN pipenv run playwright install chromium
RUN pipenv run playwright install-deps

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]