FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV INTEGRATION_HOST=0.0.0.0
ENV PORT=7860

WORKDIR /app

COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

COPY backend-integration ./backend-integration
COPY backend-module ./backend-module
COPY frontend-prototype ./frontend-prototype

EXPOSE 7860

CMD ["python", "backend-integration/server.py"]
