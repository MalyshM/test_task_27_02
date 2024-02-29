FROM python:3.10

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /test_task_27_02
COPY . /test_task_27_02
RUN pip install --no-cache-dir -r requirements.txt