FROM alpine:3.10

RUN apk add python3

ENV APP_DIR="/opt/stage_1"
ENV ENTRY_SCRIPT="demo_stage_1.py"
RUN mkdir ${APP_DIR}

COPY common.py ${ENTRY_SCRIPT} ${APP_DIR}/

ENTRYPOINT "${APP_DIR}/${ENTRY_SCRIPT}"
