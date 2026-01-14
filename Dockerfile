FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git wget zip unzip curl \
    autoconf libtool pkg-config \
    zlib1g-dev libffi-dev libssl-dev \
    libncurses5-dev libsqlite3-dev \
    && apt-get clean

# Устанавливаем Buildozer
RUN pip3 install buildozer cython

# Устанавливаем Android SDK
RUN mkdir -p /opt/android-sdk
RUN cd /opt/android-sdk && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mv cmdline-tools tools

# Устанавливаем переменные окружения
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH="${PATH}:${ANDROID_HOME}/tools/bin:${ANDROID_HOME}/platform-tools"

# Принимаем лицензии и устанавливаем необходимые пакеты
RUN yes | ${ANDROID_HOME}/tools/bin/sdkmanager --licenses
RUN ${ANDROID_HOME}/tools/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"

# Создаем пользователя
RUN useradd -m -u 1001 -s /bin/bash builder
USER builder

WORKDIR /app