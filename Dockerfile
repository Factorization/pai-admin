FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade wheel setuptools
RUN pip install --no-cache-dir --no-deps -r requirements.txt
RUN pip install gunicorn cryptography

COPY app app
COPY migrations migrations
COPY manage.py run_flask.py config.py start.sh ./
RUN chmod a+x start.sh

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV FLASK_APP run_flask.py

EXPOSE 3000
ENTRYPOINT [ "./start.sh" ]
