FROM ubuntu:16.04

RUN apt-get update && apt-get -y install curl python3 python3-pip software-properties-common apt-transport-https git

# Add the osm repository
RUN curl "https://osm-download.etsi.org/repository/osm/debian/ReleaseSIX/OSM%20ETSI%20Release%20Key.gpg" | apt-key add - && \
    add-apt-repository -y "deb [arch=amd64] https://osm-download.etsi.org/repository/osm/debian/ReleaseSIX stable IM osmclient devops"
RUN apt-get update && apt-get -y install python3-osm-im

RUN pip3 install pyangbind pyyaml

ENV WORK_DIR=/work
ENV USER_NAME=builder
#ARG USER_UID
#RUN useradd --create-home --uid ${USER_UID} --shell /bin/bash ${USER_NAME}
RUN mkdir ${WORK_DIR}
# && chown ${USER_NAME} ${WORK_DIR}
# USER ${USER_NAME}

# install osm devops tools
RUN cd ~ && git clone https://osm.etsi.org/gerrit/osm/devops
ENV PATH="${PATH}:~/devops/descriptor-packages/tools"

WORKDIR ${WORK_DIR}
VOLUME ${WORK_DIR}
