# Dockerfile for OnCORSeq Bot based on CentOS:7.4.1708
FROM ipm-dc-dtr.weill.cornell.edu/ipm/centos@sha256:e293d7f780711627202b9d764e05d5116209cccf98e6d2610755973f77b74fe9
#===============================#
# Docker Image Configuration	#
#===============================#
LABEL Description="OnCORSeq Bot" \
    Vendor="Englander Institute for Precision Medicine" \
    maintainer="sir2013@med.cornell.edu" \
    base_image="ipm-dc-dtr.weill.cornell.edu/ipm/centos" \
    base_image_version="7.6.1810.patched20190401" \
    base_image_SHA256="sha256:e293d7f780711627202b9d764e05d5116209cccf98e6d2610755973f77b74fe9"

ENV APP_NAME='oncorseq-bot' \
	TZ='US/Eastern' \
	PROGRAMS="opt"
#===========================#
# CentOS Preparation        #
#===========================#
RUN yum groupinstall -y "Development Tools" && yum install -y \
        wget \
        tar \
        gcc \
        gcc-c++ \
        openssl-devel \
        zip \
        unzip \
        make \
        cmake \
        which \
        readline-devel \
        libX11-devel \
        libXt-devel \
        cairo-devel \
        libjpeg-devel \
        pango-devel \
        dejavu* \
        iptables-services \
        systemctl \
        && yum -y clean all
#===========================#
# Pipeline Configuration    #
#===========================#
WORKDIR /${PROGRAMS}

RUN mkdir -p /${APP_NAME}/scripts \
    && mkdir -p /${APP_NAME}/tmp_dir \
    && mkdir -p /${APP_NAME}/docker_bash_scripts

COPY scripts /${APP_NAME}/scripts/
COPY opt /${PROGRAMS}/

#===========================#
# Install Python 2.7.13     #
#===========================#
ENV PYTHON_VERSION 2.7.13
RUN tar xzf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure \
    && make \
    && make install \
    && python /${PROGRAMS}/get-pip.py

RUN pip install requests==2.20.1

WORKDIR /${APP_NAME}/scripts/

RUN mkdir -p /${APP_NAME}/tmp_dir \
    && mkdir -p /${APP_NAME}/docker_bash_scripts

#===================================#
# Startup                           #
#===================================#
CMD ./OnCORSeq-bot.sh