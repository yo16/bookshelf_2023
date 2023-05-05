FROM python:3.11.3
WORKDIR /app
COPY . /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install uwsgi
ENV FLASK_APP=app
ENV FLASK_DEBUG=1
EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
