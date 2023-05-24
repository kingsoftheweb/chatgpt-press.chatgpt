FROM python:3.10

COPY requirements.txt .

WORKDIR .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
