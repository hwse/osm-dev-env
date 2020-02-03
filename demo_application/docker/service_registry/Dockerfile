FROM alpine:3.10

RUN apk add python3 py3-pip

ENV APP_DIR="/opt/service_registry"
ENV ENTRY_SCRIPT="service_registry.py"
RUN mkdir ${APP_DIR}

COPY ${ENTRY_SCRIPT} service_registry_requirements.txt ${APP_DIR}/

RUN pip3 install -r ${APP_DIR}/service_registry_requirements.txt

ENTRYPOINT "${APP_DIR}/${ENTRY_SCRIPT}"
