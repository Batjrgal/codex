FROM python:3.10-slim

WORKDIR /app

# ffmpeg суулгах
RUN apt-get update && apt-get install -y ffmpeg

# Python хамаарлууд суулгах
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "server.py"]
