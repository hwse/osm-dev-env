FROM alpine:3.10

RUN apk add python3

ENV APP_DIR="/opt/load_balancer"
ENV ENTRY_SCRIPT="load_balancer.py"
RUN mkdir ${APP_DIR}

COPY common.py ${ENTRY_SCRIPT} ${APP_DIR}/

ENTRYPOINT "${APP_DIR}/${ENTRY_SCRIPT}
