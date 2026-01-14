FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем ВСЕ зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    zip \
    unzip \
    curl \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    libncurses5-dev \
    libsqlite3-dev \
    && apt-get clean

# Устанавливаем Buildozer
RUN pip3 install buildozer cython

# Создаем пользователя
RUN useradd -m -u 1001 -s /bin/bash builder
USER builder

WORKDIR /app