FROM ubuntu:22.04

# Устанавливаем таймзону (чтобы не спрашивала при установке)
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем все зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    automake \
    cmake \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    sudo \
    curl \
    ccache \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Buildozer и Cython
RUN pip3 install --upgrade pip setuptools wheel \
    && pip3 install buildozer cython virtualenv

# Создаем пользователя без пароля для безопасности
RUN useradd -m -u 1000 -s /bin/bash builder \
    && echo "builder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Рабочая директория
WORKDIR /app

# Копируем все файлы проекта
COPY . /app/

# Меняем владельца на builder
RUN chown -R builder:builder /app

# Переключаемся на пользователя builder
USER builder

# Команда по умолчанию
CMD ["bash"]