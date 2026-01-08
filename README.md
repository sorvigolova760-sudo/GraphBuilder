# Hello Kivy

Простое приложение "Hello, World!" на Python с Kivy.

## Установка

1. Создайте виртуальное окружение и активируйте его:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Обновите pip и установите зависимости:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

> На Linux может потребоваться установить системные зависимости (SDL2, GStreamer и др.). Если `pip install kivy` падает, установите через пакетный менеджер:

- Debian/Ubuntu (пример):
  ```bash
  sudo apt install python3-dev build-essential libgl1-mesa-dev libgles2-mesa-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  ```

## Запуск

```bash
python main.py
```

Если нужно — помогу настроить окружение или собрать Kivy из исходников.