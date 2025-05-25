FROM python:3.13-alpine

WORKDIR /app

COPY src/enroll_api/requirements.txt .

RUN pip install -r requirements.txt

COPY src/enroll_api .

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
