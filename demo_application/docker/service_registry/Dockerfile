FROM alpine:3.10

RUN apk add python3 py3-pip

ENV APP_DIR="/opt/load_balancer"
ENV ENTRY_SCRIPT="load_balancer.py"
RUN mkdir ${APP_DIR}

COPY ${ENTRY_SCRIPT} load_balancer_requirements.txt ${APP_DIR}/

RUN pip3 install -r ${APP_DIR}/load_balancer_requirements.txt

ENTRYPOINT "${APP_DIR}/${ENTRY_SCRIPT}"
