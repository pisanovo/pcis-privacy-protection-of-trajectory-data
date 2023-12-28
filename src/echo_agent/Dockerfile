# syntax=docker/dockerfile:1
FROM python:3.7-bookworm
RUN pip3 install --upgrade pip
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["flask", "--debug", "run"]
