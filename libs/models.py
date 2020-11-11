"""
-----------> MODELS <-----------
"""

from libs import basic_shapes as bs, transformations as tr, easy_shaders as es, scene_graph as sg
import numpy as np
from OpenGL.GL import *
import random as rd
from typing import Union


class Game(object):
    def __init__(self, n):
        self.size = n
        self.grid = 1 / n
        self.center = tuple(int(n / 2) for _ in range(2))
        self.time = 1 / np.log(n) * [2, 10, 5][0]
        self.resize = n / (n + 2)
        self.count_food = 0
        self.empty = set()
        for i in range(0, self.size):
            for j in range(0, self.size):
                self.empty.add((i, j))
        self.empty -= {self.center}
        self.win = False
        self.dead = False
        self.pause = True
        self.speed = False
        self.time_pause = 0
        self.notFood = False
        # module: game-time
        self.t = 0
        self.dt = 0
        self.count = 0
        # key-lock
        self.lock = False
        # cam
        self.cam_angle = 0

    def set_speed(self, s):
        self.time = s * 1 / np.log(self.size)

    def post_time(self, t0):
        self.dt = [0.005, (self.dt + t0 - self.t + 0.005) / 3][0]
        self.t = t0

    def check_time(self):
        if self.count * self.dt > self.time:
            self.count = 0
            return True
        else:
            return False

    def count_time(self):
        self.count += 1

    def update(self):
        self.pause = False
        self.win = False
        self.dead = False
        self.speed = False
        self.notFood = False


class Snake(object):
    game: Union['Game', None]
    food: Union['Food', None]

    def __init__(self, game, food):
        self.food = food
        self.game = game
        self.pos = game.center
        self.current_pos = get_pos(game.grid, game.size, self.pos)
        self.view_pos = self.current_pos
        self.dir = 0, 0
        self.key = 0, 0
        self.next = tuple(sum(t) for t in zip(self.pos, self.dir))
        self.tail = []
        self.angle = {
            (0, 0): np.pi / 2,
            (-1, 0): np.pi / 2,
            (1, 0): 3*np.pi / 2,
            (0, -1): 0,
            (0, 1): np.pi
        }
        # angle
        self.theta = 0
        self.new_theta = self.theta
        # time
        self.t0 = 0

        gpu_head_quad = es.toGPUShape(bs.createColorCube(0, 1, 0))

        head = sg.SceneGraphNode('head')
        head.transform = tr.uniformScale(1.8 * game.grid)   # 1.8
        head.childs += [gpu_head_quad]

        head_tr = sg.SceneGraphNode('head_tr')
        head_tr.transform = tr.identity()
        head_tr.childs += [head]

        body = sg.SceneGraphNode('body')
        body.transform = tr.identity()
        body.childs += [head_tr]

        body_tr = sg.SceneGraphNode('body_tr')
        body_tr.transform = tr.identity()
        body_tr.childs += [body]

        self.body = body
        self.model = body_tr
        self.head = head_tr
        self.bodySnake = bodySnake(self)

        self.g_resize = self.game.resize
        self.g_grid = self.game.grid
        self.g_size = self.game.size
        self.g_center = self.game.center

    def draw(self, pipeline, projection, view):
        view_pos = get_pos(self.g_grid, self.g_size, self.pos, self.next,
                           self.current_pos, i=self.game.count, m=self.game.time / self.game.dt)
        theta = get_theta(self.theta, self.new_theta, i=self.game.count - self.t0,
                          m=self.game.time / self.game.dt - self.t0)
        self.view_pos = view_pos
        self.game.cam_angle = theta
        self.model.transform = tr.uniformScale(self.g_resize)
        self.head.transform = tr.matmul([
            tr.translate(
                tx=view_pos[0],
                ty=view_pos[1],
                tz=1.8*self.game.grid / 2
            ),
            tr.rotationZ(theta)
        ])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(self.model, pipeline)

    def update(self):
        if not self.game.pause:
            self.game.lock = False
            self.tail.append(self.pos)
            self.tail.pop(0)
            self.dir = self.key
            self.pos = self.next
            self.next = tuple(sum(t) for t in zip(self.pos, self.dir))
            self.theta = self.new_theta
            self.current_pos = get_pos(self.g_grid, self.g_size, self.pos)
            self.bodySnake.update(self.tail)
        if self.game.notFood:
            self.game.win = True

    def set_key(self, k):
        if self.is_new_dir(k):
            self.key = k
            self.theta = self.new_theta
            self.new_theta = self.angle[k]
            self.t0 = self.game.count
            self.game.lock = True

    def collide(self):
        if not (self.game.win or self.game.pause):
            if not self.pos[0] in set(range(0, self.g_size)) or \
                    not self.pos[1] in set(range(0, self.g_size)) \
                    or (self.pos in self.tail):
                self.dead()
            if self.pos == self.food.pos:
                self.eat()

    def eat(self):
        self.tail = [None] + self.tail
        self.food.update(self)
        self.game.count_food += 1
        self.bodySnake.new(self.pos)

    def dead(self):
        self.pos = self.g_center
        self.current_pos = get_pos(self.g_grid, self.g_size, self.pos)
        self.view_pos = self.current_pos
        self.dir = 0, 0
        self.key = 0, 0
        self.next = tuple(sum(t) for t in zip(self.pos, self.dir))
        self.game.count_food = 0
        self.tail = []
        self.body.childs = [self.head]
        self.bodySnake.death()
        self.food.update(self)
        if not (self.game.notFood or self.game.pause):
            self.game.dead = True

    def is_new_dir(self, k):
        return sum([self.dir[i] * k[i] for i in range(2)]) == 0


class bodyCreator(object):
    game: Union['Game', None]

    def __init__(self, game, body, pos):
        self.game = game
        view_pos = get_pos(game.grid, game.size, pos)

        gpu_body_quad = es.toGPUShape(bs.createColorCube(0, 0.8, 0))

        body_sh = sg.SceneGraphNode('body_sh')
        body_sh.transform = tr.uniformScale(1.7 * game.grid)
        body_sh.childs += [gpu_body_quad]

        body_sh_tr = sg.SceneGraphNode(f'body_sh_tr_{game.count_food}')
        body_sh_tr.transform = tr.translate(
            tx=view_pos[0],
            ty=view_pos[1],
            tz=1.7*self.game.grid / 2
        )
        body_sh_tr.childs += [body_sh]
        body.childs = [body_sh_tr] + body.childs

        self.model = body_sh_tr
        self.g_grid = self.game.grid
        self.g_size = self.game.size

    def update(self, pos):
        view_pos = get_pos(self.g_grid, self.g_size, pos)
        self.model.transform = tr.translate(
            tx=view_pos[0],
            ty=view_pos[1],
            tz=1.7*self.game.grid / 2)


class bodySnake(object):
    game: Union['Game', None]
    snake: Union['Snake', None]

    def __init__(self, snake):
        self.snake = snake
        self.game = snake.game
        self.body = snake.body
        self.list = []

    def new(self, pos):
        self.list.append(bodyCreator(self.game, self.body, pos))

    def update(self, tail):
        for i in range(self.game.count_food):
            self.list[i].update(tail[i])

    def death(self):
        self.list = []


class Food(object):
    snake: Union['Snake', None]

    def __init__(self, game):
        self.game = game
        self.pos = tuple(rd.randint(0, game.size - 1) for _ in range(2))
        self.view_pos = get_pos(game.grid, game.size, self.pos)

        gpu_food_quad = es.toGPUShape(bs.createColorCube(1, 0, 0))

        food = sg.SceneGraphNode('food')
        food.transform = tr.uniformScale(1 * game.grid)
        food.childs += [gpu_food_quad]

        food_tr = sg.SceneGraphNode('food_tr')
        food_tr.transform = tr.translate(
                tx=self.view_pos[0],
                ty=self.view_pos[1],
                tz=0)
        food_tr.childs += [food]

        self.model = food_tr
        self.g_resize = self.game.resize
        self.g_grid = self.game.grid
        self.g_size = self.game.size

    def draw(self, pipeline, projection, view, theta):
        self.model.transform = tr.matmul([
            tr.uniformScale(self.g_resize),
            tr.translate(
                tx=self.view_pos[0],
                ty=self.view_pos[1],
                tz=self.game.grid / 2),
            tr.rotationZ(theta)
        ])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(self.model, pipeline)

    def update(self, snake):
        choice = self.game.empty - set(snake.tail) - {snake.pos}
        if choice != set():
            self.pos = rd.choice(list(choice))
            self.view_pos = get_pos(self.g_grid, self.g_size, self.pos)
        else:
            self.game.notFood = True


class Background(object):
    def __init__(self, game, image):
        self.game = game

        gpu_BG_quad = es.toGPUShape(bs.createTextureQuad(image, game.size, game.size), GL_REPEAT, GL_LINEAR)

        BG = sg.SceneGraphNode('BG')
        BG.transform = tr.uniformScale(2)
        BG.childs += [gpu_BG_quad]

        BG_tr = sg.SceneGraphNode('BG_tr')
        BG_tr.childs += [BG]

        self.model = BG_tr
        self.g_resize = self.game.resize

    def draw(self, pipeline, projection, view):
        self.model.transform = tr.uniformScale(self.g_resize)
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(self.model, pipeline)


class interactiveWindow(object):
    def __init__(self):
        gpu_deadW_quad = es.toGPUShape(bs.createTextureQuad("libs/fig/dead.png"), GL_REPEAT,
                                       GL_NEAREST)
        gpu_pauseW_quad = es.toGPUShape(bs.createTextureQuad("libs/fig/pause.png"), GL_REPEAT,
                                        GL_NEAREST)
        gpu_winW_quad = es.toGPUShape(bs.createTextureQuad("libs/fig/win.png"), GL_REPEAT,
                                      GL_NEAREST)
        gpu_speedW_quad = es.toGPUShape(bs.createTextureQuad("libs/fig/speed.png"), GL_REPEAT,
                                        GL_NEAREST)

        deadW = sg.SceneGraphNode('deadW')
        deadW.transform = tr.uniformScale(1)
        deadW.childs += [gpu_deadW_quad]

        deadW_tr = sg.SceneGraphNode('deadW_tr')
        deadW_tr.transform = tr.identity()
        deadW_tr.childs += [deadW]

        pauseW = sg.SceneGraphNode('pauseW')
        pauseW.transform = tr.uniformScale(1)
        pauseW.childs += [gpu_pauseW_quad]

        pauseW_tr = sg.SceneGraphNode('pauseW_tr')
        pauseW_tr.transform = tr.identity()
        pauseW_tr.childs += [pauseW]

        winW = sg.SceneGraphNode('deadW')
        winW.transform = tr.uniformScale(1)
        winW.childs += [gpu_winW_quad]

        winW_tr = sg.SceneGraphNode('deadW_tr')
        winW_tr.transform = tr.identity()
        winW_tr.childs += [winW]

        speedW = sg.SceneGraphNode('speedW')
        speedW.transform = tr.uniformScale(1)
        speedW.childs += [gpu_speedW_quad]

        speedW_tr = sg.SceneGraphNode('speedW_tr')
        speedW_tr.transform = tr.identity()
        speedW_tr.childs += [speedW]

        self.models = {'dead': deadW_tr, 'pause': pauseW_tr, 'win': winW_tr, 'speed': speedW_tr}

    def draw(self, pipeline, theta, mod):
        model = self.models[mod]
        model.transform = tr.matmul([
            tr.uniformScale(theta / np.pi),
            tr.translate(
                tx=0,
                ty=0,
                tz=0),
            tr.rotationZ(theta)
        ])
        sg.drawSceneGraphNode(model, pipeline, 'transform')


class Axis(object):
    def __init__(self, ln):
        self.model = es.toGPUShape(bs.createAxis(ln))

    def draw(self, pipeline, projection, view):
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(self.model, GL_LINES)


class Cam(object):
    game: Union['Game', None]
    snake: Union['Snake', None]

    def __init__(self, s, g):
        self.snake = s
        self.game = g
        self.status = 'R'
        ratio = 16/9
        self.projection = [
            tr.ortho(-1 * ratio, 1 * ratio, -1, 1, 0.1, 1000),
            tr.perspective(2 * np.pi, ratio, 0.1, 1000),
            tr.perspective(1.5 * np.pi, ratio, 0.1, 1000)
        ]
        self.view = [
            tr.lookAt(
                np.array([10, -10, 10]),
                np.array([0, 0, 0]),
                np.array([0, 0, 1])),
            tr.lookAt(
                np.array([0, 0, 10]),
                np.array([0, 0, 0]),
                np.array([0, 1, 0])),
            tr.lookAt(
                np.array([0, -10, 10]),
                np.array([0, 0, 0]),
                np.array([0, 0, 1]))
        ]
        self.view_gta = None

    def get_cam_gta(self):
        self.view_gta = tr.lookAt(
                np.array([10*np.sin(self.game.cam_angle) + self.snake.view_pos[0],
                          -10*np.cos(self.game.cam_angle) + self.snake.view_pos[1], 5]),
                np.array([self.snake.view_pos[i] for i in range(2)]+[1.8*self.game.grid / 2]),
                np.array([0, 0, 1]))
        return self.projection[2], self.view_gta

    def get_cam(self):
        if self.status == 'R':  # gta
            return self.get_cam_gta()

        elif self.status == 'T':    # perspective
            return self.projection[1], self.view[2]

        elif self.status == 'E':    # map
            return self.projection[0], self.view[1]


def get_pos(grid, size, pos, next_pos = None, current = None, i = 0, m = 1):
    if current is None:
        return tuple(
            grid * ((size - 1) * (-1) ** (t + 1)
                    + 2 * pos[t] * (-1) ** t)
            for t in range(2))
    else:
        next_pos = tuple(
            grid * ((size - 1) * (-1) ** (t + 1)
                    + 2 * next_pos[t] * (-1) ** t)
            for t in range(2))
        return tuple(
            next_pos[t] * (i / m) + current[t] * (1 - i / m)
            for t in range(2))


def get_theta(theta_1, theta_2, i = 0, m = 1):
    if theta_1 == 0 and theta_2 == 3 * np.pi / 2:
        return (i / m) * (-np.pi / 2) + (1 - i / m) * theta_1
    elif theta_2 == 0 and theta_1 == 3 * np.pi / 2:
        return (i / m) * (2 * np.pi) + (1 - i / m) * theta_1
    else:
        return (i / m) * theta_2 + (1 - i / m) * theta_1
