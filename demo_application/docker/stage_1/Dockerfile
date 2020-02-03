FROM alpine:3.10

RUN apk add python3 py3-pip

ENV APP_DIR="/opt/stage_1"
ENV ENTRY_SCRIPT="stage_1.py"
RUN mkdir ${APP_DIR}

COPY common.py ${ENTRY_SCRIPT} common_requirements.txt stage_1_requirements.txt ${APP_DIR}/

RUN pip3 install -r ${APP_DIR}/stage_1_requirements.txt

ENTRYPOINT "${APP_DIR}/${ENTRY_SCRIPT}"
