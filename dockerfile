FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cache directories (so model downloads persist across restarts on Spaces)
ENV HF_HOME=/data/.cache/huggingface
ENV TRANSFORMERS_CACHE=/data/.cache/huggingface
ENV TORCH_HOME=/data/.cache/torch

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

COPY backend/ /app/

# Hugging Face Spaces routes traffic to this port for Docker apps
EXPOSE 7860

# Run the Flask app via gunicorn on port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--workers", "1", "--timeout", "600", "app:app"]
