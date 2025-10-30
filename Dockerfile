FROM python:3.10-slim

# ажлын хавтас
WORKDIR /app

# файлуудыг хуулах
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# port нээх
EXPOSE 8080

# сервер ажиллуулах
CMD ["python", "server.py"]
