FROM python:3.12.2-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY assistant.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "assistant.py"]
