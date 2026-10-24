FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt greenlet==3.1.1
COPY . .
RUN chmod -R g=u /app && chmod +x /app/entrypoint.sh
EXPOSE 8000
USER 1001
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

