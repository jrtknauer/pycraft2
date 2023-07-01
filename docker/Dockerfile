ARG PYTHON_VERSION=3.10

FROM alpine:latest AS install-starcraft2
LABEL MAINTAINER="jrtknauer@proton.me"

WORKDIR /root/

RUN apk update
RUN apk upgrade
RUN apk add \
    unzip \
    wget

ARG SC2_VERSION=4.10

# Download and installing the headless StarCraft II Linux package.
RUN wget -q --show-progress --progress=bar:force https://blzdistsc2-a.akamaihd.net/Linux/SC2.${SC2_VERSION}.zip
RUN unzip -q -P iagreetotheeula SC2.${SC2_VERSION}.zip
RUN rm SC2.${SC2_VERSION}.zip
RUN rm -rf \
    StarCraftII/Battle.net \
    StarCraftII/Versions/Shaders*

FROM python:${PYTHON_VERSION}-slim AS pycraft2

COPY --from=install-starcraft2 /root/StarCraftII /root/StarCraftII

COPY . /root/pycraft2/

WORKDIR /root/pycraft2/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --editable .
RUN python3 -m pip install -r requirements/test.txt
