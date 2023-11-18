FROM python:3.11.0

WORKDIR /app
COPY . /app

RUN python3 -m pip install -r requirements.txt

# CMD ["python3", "main.py"]
