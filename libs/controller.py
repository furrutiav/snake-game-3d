"""
-----------> CONTROLLER <-----------
"""

from libs.models import *
import glfw
from typing import Union
import sys


class Controller(object):
    snake: Union['Snake', None]
    game: Union['Game', None]
    cam: Union['Cam', None]

    def __init__(self):
        self.snake = None
        self.game = None
        self.cam = None
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
        self.clock = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}
        self.count = 0

    def set_snake(self, s):
        self.snake = s

    def set_game(self, g):
        self.game = g

    def set_cam(self, c):
        self.cam = c

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS):
            return

        if self.game.pause:
            if key == glfw.KEY_SPACE:
                self.game.update()
                self.game.time_pause = 0
            elif key == glfw.KEY_ESCAPE:
                glfw.terminate()
                sys.exit()

        elif self.game.dead:
            if key == glfw.KEY_SPACE:
                self.game.update()
                self.game.time_pause = 0
            elif key == glfw.KEY_ESCAPE:
                glfw.terminate()
                sys.exit()

        elif self.game.win:
            if key == glfw.KEY_SPACE:
                self.snake.dead()
                self.game.update()
                self.game.time_pause = 0
            elif key == glfw.KEY_ESCAPE:
                glfw.terminate()
                sys.exit()

        else:
            if not self.game.lock:
                if self.cam.status == 'R':
                    if key == glfw.KEY_LEFT or key == glfw.KEY_A:
                        self.count = (4 + self.count - 1) % 4
                        self.snake.set_key(self.clock[self.count])

                    elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
                        self.count = (self.count + 1) % 4
                        self.snake.set_key(self.clock[self.count])
                else:
                    if key == glfw.KEY_LEFT or key == glfw.KEY_A:
                        self.snake.set_key(self.dirs[key])

                    elif key == glfw.KEY_RIGHT or key == glfw.KEY_D:
                        self.snake.set_key(self.dirs[key])

                    elif key == glfw.KEY_UP or key == glfw.KEY_W:
                        self.snake.set_key(self.dirs[key])

                    elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
                        self.snake.set_key(self.dirs[key])

            if key == glfw.KEY_R and self.cam.status != 'R':
                snake_key = self.snake.key
                if self.snake.key == (0, 0):
                    snake_key = (0, -1)
                self.count = dict(zip(self.clock.values(), self.clock.keys()))[snake_key]
                self.cam.status = 'R'

            elif key == glfw.KEY_E and self.cam.status != 'E':
                self.cam.status = 'E'

            elif key == glfw.KEY_T and self.cam.status != 'T':
                self.cam.status = 'T'

            elif key == glfw.KEY_ESCAPE:
                self.game.pause = True
