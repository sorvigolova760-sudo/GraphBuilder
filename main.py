"""
Точка входа в приложение GraphBuilder
"""
import os
from core.app import GraphFunctionApp


# Настройки Kivy
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_WINDOW'] = 'sdl2'
from kivy.config import Config
Config.set('graphics', 'multisamples', '16')
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')


if __name__ == '__main__':
    GraphFunctionApp().run()
