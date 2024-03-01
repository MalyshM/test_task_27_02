FROM python:3.10

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /
COPY . /
RUN pip install --no-cache-dir -r requirements.txt