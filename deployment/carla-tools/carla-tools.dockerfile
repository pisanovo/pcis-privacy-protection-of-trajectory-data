# Dockerfile for the setup containers
# Expected context: ./ (root of the repository)
FROM python:3.8-bookworm
WORKDIR /code
ENV PYTHONPATH=/code/src
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["bash"]
