FROM python:alpine3.17
LABEL authors="Yuriy Choba"
RUN apk update && apk upgrade && apk add git && apk add bash
RUN pip install --upgrade pip
WORKDIR /app
RUN ["mkdir", "./db"]
COPY ./main.py .
COPY ./models.py .
COPY ./schemas.py .
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]