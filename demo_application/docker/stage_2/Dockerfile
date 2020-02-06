FROM alpine:3.10

RUN apk add python3 py3-pip bash

ENV APP_DIR="/opt/stage_2"
ENV ENTRY_SCRIPT="stage_2.py"
RUN mkdir ${APP_DIR}

COPY common.py ${ENTRY_SCRIPT} common_requirements.txt stage_2_requirements.txt ${APP_DIR}/

RUN pip3 install -r ${APP_DIR}/stage_2_requirements.txt

ENTRYPOINT "${APP_DIR}/${ENTRY_SCRIPT}"
