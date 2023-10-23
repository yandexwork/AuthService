FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
COPY ./src ./src

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "--reload", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]