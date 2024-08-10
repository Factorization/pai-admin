FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn cryptography

COPY app app
COPY migrations migrations
COPY run_flask.py config.py start.sh ./
RUN chmod a+x start.sh

ENV FLASK_APP run_flask.py

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
