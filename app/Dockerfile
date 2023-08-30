FROM python:3.11.5
WORKDIR /app
COPY . /app/

# stripe
RUN curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | tee /usr/share/keyrings/stripe.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" | tee -a /etc/apt/sources.list.d/stripe.list
RUN apt-get update && apt-get install -y stripe

# python, flask
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install uwsgi
ENV FLASK_APP=app
ENV FLASK_DEBUG=1
EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
