FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install --no-deps -r requirements.txt
RUN pip install gunicorn cryptography

COPY app app
COPY migrations migrations
COPY create_user.py run_flask.py config.py start.sh ./
RUN chmod a+x start.sh

ENV FLASK_APP run_flask.py

EXPOSE 3000
ENTRYPOINT [ "./start.sh" ]
