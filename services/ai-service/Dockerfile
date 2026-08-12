FROM python:3.11-slim
WORKDIR /app
# Mode de base (regex) : pas besoin de libs systeme lourdes.
COPY requirements.txt requirements-ml.txt ./
ENV PIP_DEFAULT_TIMEOUT=300 PIP_RETRIES=15
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --timeout 300 --retries 15 -r requirements.txt
COPY app ./app
COPY training ./training
RUN mkdir -p /app/model /app/uploads
EXPOSE 8084
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8084"]
