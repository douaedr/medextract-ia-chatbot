FROM python:3.11-slim
WORKDIR /app

# Dependances systeme pour PaddleOCR + pdf2image (poppler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils libgl1 libglib2.0-0 libgomp1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
ENV PIP_DEFAULT_TIMEOUT=300 PIP_RETRIES=15
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --timeout 300 --retries 15 -r requirements.txt
COPY app ./app
RUN mkdir -p /app/uploads
EXPOSE 8083
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"]
