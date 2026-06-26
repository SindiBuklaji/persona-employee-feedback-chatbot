FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8501

# Create .streamlit config directory and add production config
RUN mkdir -p ~/.streamlit && \
    echo "[client]" > ~/.streamlit/config.toml && \
    echo "showErrorDetails = false" >> ~/.streamlit/config.toml && \
    echo "[server]" >> ~/.streamlit/config.toml && \
    echo "headless = true" >> ~/.streamlit/config.toml && \
    echo "enableXsrfProtection = true" >> ~/.streamlit/config.toml

# Run streamlit in production mode
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--client.toolbarMode=minimal"]
