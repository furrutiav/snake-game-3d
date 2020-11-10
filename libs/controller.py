"""
-----------> CONTROLLER <-----------
"""

from libs.models import *
import glfw
from typing import Union


class Controller(object):
    snake: Union['Snake', None]

    def __init__(self):
        self.snake = None
        self.game = None
        self.dirs = {
            glfw.KEY_A: (-1, 0),
            glfw.KEY_D: (1, 0),
            glfw.KEY_W: (0, -1),
            glfw.KEY_S: (0, 1),

            glfw.KEY_LEFT: (-1, 0),
            glfw.KEY_RIGHT: (1, 0),
            glfw.KEY_UP: (0, -1),
            glfw.KEY_DOWN: (0, 1),
        }

    def set_snake(self, s):
        self.snake = s

    def set_game(self, g):
        self.game = g

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS) or (action == glfw.RELEASE):
            return

        if self.game.pause:
            if key == glfw.KEY_SPACE:
                self.game.update()
                self.game.time_pause = 0

        elif self.game.dead:
            if key == glfw.KEY_SPACE:
                self.game.update()
                self.game.time_pause = 0
            elif key == glfw.KEY_H:
                self.game.dead = False
                self.game.speed = True
                self.game.time_pause = 0

        elif self.game.speed:
            if key == glfw.KEY_1:
                self.game.set_speed(2)
                self.game.update()
                self.game.time_pause = 0

            elif key == glfw.KEY_2:
                self.game.set_speed(1)
                self.game.update()
                self.game.time_pause = 0

            elif key == glfw.KEY_3:
                self.game.set_speed(0.5)
                self.game.update()
                self.game.time_pause = 0

        elif self.game.win:
            if key == glfw.KEY_SPACE:
                self.snake.dead()
                self.game.update()
                self.game.time_pause = 0
        else:
            if not self.game.lock:
                if key == glfw.KEY_LEFT or key == glfw.KEY_A:
                    self.snake.set_key(self.dirs[key])

                elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
                    self.snake.set_key(self.dirs[key])

                elif key == glfw.KEY_UP or key == glfw.KEY_W:
                    self.snake.set_key(self.dirs[key])

                elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
                    self.snake.set_key(self.dirs[key])

            else:
                if key == glfw.KEY_ESCAPE:
                    self.game.pause = True
