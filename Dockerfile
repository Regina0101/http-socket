FROM python:3.12.1-slim

WORKDIR .

COPY . .

CMD ["python", "main.py"]