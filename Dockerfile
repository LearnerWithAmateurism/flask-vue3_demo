FROM alpine:latest
COPY ./Flask/ requirement.txt /Flask_Demo/
RUN apk update && \
    apk add --no-cache python3 py-pip && \
    pip -U -r requirements.txt
WORKDIR /Flask_Demo
EXPOSE 50002
ENTRYPOINT gunicorn -p 50002 -w 2 -t 2 Flask/main:flaskInstance
