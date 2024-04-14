FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5001
ENV FLASK_APP=app.py
CMD gunicorn \
    --bind 0.0.0.0:5001 \
    --timeout 100 \
    -k gevent \
    -w 1 \
    --threads 1 \
    app:app