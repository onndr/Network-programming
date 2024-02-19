FROM alpine

COPY . /project
WORKDIR /project/
RUN apk update;\
    apk add python3;\
    apk add openssl;\
    openssl genrsa -out server.key 2048;\
    openssl req -new -x509 -key server.key -out server.crt -days 365 -subj /CN=localhost
