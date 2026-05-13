FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m telemetry_user
USER telemetry_user

COPY telemetry_cleaning.py .
COPY data .

CMD ["python", "telemetry_cleaning.py"]