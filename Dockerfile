FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ..

ENV TOKEN=${TOKEN}
ENV CHANNEL_ID=${CHANNEL_ID}
ENV CAPTIONS_FILE=${CAPTIONS_FILE}

CMD ["python", "bot.py"]