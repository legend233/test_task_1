FROM python:alpine3.17
LABEL authors="Yuriy Choba"
RUN apk update && apk upgrade && apk add git && apk add bash
RUN pip install --upgrade pip
RUN ["mkdir", "./db"]
WORKDIR /app
COPY ./main.py .
COPY ./models.py .
COPY ./schemas.py .
COPY ./requirements.txt .
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app --reload"]