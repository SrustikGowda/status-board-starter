FROM python:3.12-slim
WORKDIR /app
RUN pip install flask==3.1.2
COPY . .
CMD ["python", "app.py"]
