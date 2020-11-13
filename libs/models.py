"""
-----------> MODELS <-----------
"""

from libs import basic_shapes as bs, transformations as tr, easy_shaders as es, scene_graph as sg, lighting_shaders as ls
import numpy as np
from OpenGL.GL import *
import random as rd
from typing import Union


class Game(object):
    def __init__(self, n):
        self.size = n
        self.grid = 1 / n
        self.center = tuple(int(n / 2) for _ in range(2))
        self.time = 1 / np.log(n) * [2, 10, 5, 1, 0.6][4]
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
        self.view_cam = None
        # set
        self.numb = 0
        self.cursor = 0, 0
        # shaders
        self.view_pos = None
        self.view_food = None

    def set_speed(self, s):
        self.time *= s

    def post_time(self, t0):
        self.dt = [0.005, (self.dt + t0 - self.t + 0.005) / 3, (self.dt + t0 - self.t) / 2][0]
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
        game.view_pos = self.current_pos
        self.dir = 0, 0
        self.key = 0, 0
        self.next = tuple(sum(t) for t in zip(self.pos, self.dir))
        self.tail = []
        self.angle = {
            (0, 0): np.pi / 2,
            (-1, 0): np.pi / 2,
            (1, 0): 3 * np.pi / 2,
            (0, -1): 0,
            (0, 1): np.pi
        }
        # angle
        self.theta = 0
        self.new_theta = self.theta
        # time
        self.t0 = 0

        gpu_head_quad = es.toGPUShape(bs.readOBJ('libs/obj/head.obj', (0.4, 1, 0.4), status=False))
        gpu_eyes_quad = es.toGPUShape(bs.readOBJ('libs/obj/eyes.obj', (1, 0.2, 0.2), status=False))
        gpu_teeth_quad = es.toGPUShape(bs.readOBJ('libs/obj/teeth.obj', (0.8, .8, .8), status=False))

        head = sg.SceneGraphNode('head')
        head.transform = tr.matmul([
            tr.uniformScale(0.9),
            tr.rotationZ(np.pi / 2),
            tr.rotationX(np.pi / 2),
            tr.uniformScale(0.01),
            tr.translate(0, 0, 0)])
        head.childs += [gpu_head_quad]

        eyes = sg.SceneGraphNode('eyes')
        eyes.transform = tr.matmul([
            tr.uniformScale(0.9),
            tr.rotationZ(np.pi / 2),
            tr.rotationX(np.pi / 2),
            tr.uniformScale(0.01),
            tr.translate(0, 0, 0)])
        eyes.childs += [gpu_eyes_quad]

        teeth = sg.SceneGraphNode('teeth')
        teeth.transform = tr.matmul([
            tr.uniformScale(0.9),
            tr.rotationZ(np.pi / 2),
            tr.rotationX(np.pi / 2),
            tr.uniformScale(0.01),
            tr.translate(0, 0, 0)])
        teeth.childs += [gpu_teeth_quad]

        head_tr = sg.SceneGraphNode('head_tr')
        head_tr.transform = tr.identity()
        head_tr.childs += [head, eyes, teeth]

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

        self.g_grid = self.game.grid
        self.g_size = self.game.size
        self.g_center = self.game.center

    def draw(self, pipeline, projection, view, size):
        view_pos = get_pos(self.g_grid, self.g_size, self.pos, self.next,
                           self.current_pos, i=self.game.count, m=self.game.time / self.game.dt)
        theta = get_theta(self.theta, self.new_theta, i=self.game.count - self.t0,
                          m=self.game.time / self.game.dt - self.t0)
        self.game.view_pos = view_pos
        self.game.cam_angle = theta
        self.head.transform = tr.matmul([
            tr.translate(
                tx=view_pos[0],
                ty=view_pos[1],
                tz=0
            ),
            tr.rotationZ(theta)
        ])
        glUseProgram(pipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La1"), 0.8, 0.2, 0.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld1"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls1"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La2"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld2"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls2"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La3"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld3"), 1, 0.01, 0.01)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls3"), 1.0, 0.3, 0.3)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka1"), 0.008, 0.008, 0.008)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd1"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks1"), 0, 0, 0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka2"), 0, 0, 0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd2"), 0.7, 1.0, 0.7)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks2"), 0.5, 0.5, 0.5)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka3"), -0.04, -0.04, -0.04)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd3"), 1.0, 0.7, 0.7)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks3"), 0.36, 0.36, 0.36)

        # TO DO: Explore different parameter combinations to understand their effect!

        viewPos = self.game.view_cam
        snakePos = self.game.view_pos
        foodPos = self.game.view_food
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition1"), 0, 0, 1.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition2"), snakePos[0], snakePos[1], 0.24)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition3"), foodPos[0], foodPos[1], 0.1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                    viewPos[2])

        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess1"), -1)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess2"), 100)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess3"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation1"), -1.93)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation1"), 2.04)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation1"), 1.78)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation2"), 0.78)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation2"), 3.3)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation2"), 0)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation3"), 0.78)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation3"), 3.3)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation3"), 0)

        lamps = {1: (1, 1), 2: (-1, 1), 3: (1, -1), 4: (-1, -1)}
        for j in range(1, size+1):
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"La{3 + j}"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ld{3 + j}"), 1, 1, 1)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ls{3 + j}"), 1.0, 1.0, 1.0)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ka{3 + j}"), -0.04, -0.04, -0.04)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Kd{3 + j}"), 0.95, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ks{3 + j}"), 1, 1, 1)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"lightPosition{3 + j}"),
                        0.9 * lamps[j][0], 0.9 * lamps[j][1], 0.14)

            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, f"shininess{3 + j}"), 100)

            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, f"constantAttenuation{3 + j}"), 0.63)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, f"linearAttenuation{3 + j}"), 0.59)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, f"quadraticAttenuation{3 + j}"), 4)

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
        self.game.view_pos = self.current_pos
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

        gpu_body_quad = es.toGPUShape(bs.readOBJ('libs/obj/body.obj', (0.4, 1, 0.4), status=False))

        body_sh = sg.SceneGraphNode('body_sh')
        body_sh.transform = tr.matmul([
            tr.uniformScale(0.8),
            tr.rotationZ(np.pi / 2),
            tr.rotationX(np.pi / 2),
            tr.uniformScale(0.01),
            tr.translate(0, 0, 0)])
        body_sh.childs += [gpu_body_quad]

        body_sh_tr = sg.SceneGraphNode(f'body_sh_tr_{game.count_food}')
        body_sh_tr.transform = tr.translate(
            tx=view_pos[0],
            ty=view_pos[1],
            tz=0
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
            tz=0)


class bodySnake(object):
    game: Union['Game', None]
    snake: Union['Snake', None]

    def __init__(self, snake):
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
    game: Union['Game', None]

    def __init__(self, game):
        self.game = game
        self.pos = tuple(rd.randint(0, game.size - 1) for _ in range(2))
        self.view_pos = get_pos(game.grid, game.size, self.pos)
        game.view_food = self.view_pos

        gpu_food_obj = es.toGPUShape(bs.readOBJ('libs/obj/lightBulb.obj', (1, 0.1, 0.1)))

        food = sg.SceneGraphNode('food')
        food.transform = tr.matmul([
            tr.uniformScale(0.8 * game.grid),
            tr.rotationX(np.pi / 2),
            tr.uniformScale(0.00015),
            tr.translate(15700, -4900, 200)])
        food.childs += [gpu_food_obj]
        food_tr = sg.SceneGraphNode('food_tr')
        food_tr.transform = tr.translate(
            tx=self.view_pos[0],
            ty=self.view_pos[1],
            tz=0)
        food_tr.childs += [food]

        self.model = food_tr
        self.g_grid = self.game.grid
        self.g_size = self.game.size

    def draw(self, pipeline, projection, view, theta):
        self.model.transform = tr.matmul([
            tr.translate(
                tx=self.view_pos[0],
                ty=self.view_pos[1],
                tz=self.game.grid / 2),
            tr.rotationZ(1.5*theta)
        ])
        ctr = self.game.numb
        glUseProgram(pipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La1"), 0.8, 0.2, 0.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld1"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls1"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La2"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld2"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls2"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La3"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld3"), 1, 0.01, 0.01)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls3"), 1.0, 0.3, 0.3)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka1"), 0.008, 0.008, 0.008)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd1"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks1"), 0, 0, 0)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka2"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd2"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks2"), 1, 1, 1)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka3"), .3, .3, .3)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd3"), 1.0, 0.7, 0.7)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks3"), 0.36, 0.36, 0.36)

        # TO DO: Explore different parameter combinations to understand their effect!

        viewPos = self.game.view_cam
        snakePos = self.game.view_pos
        foodPos = self.game.view_food
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition1"), 0, 0, 1.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition2"), snakePos[0], snakePos[1], 0.09)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition3"), foodPos[0], foodPos[1], 0.7)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                    viewPos[2])

        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess1"), -1)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess2"), 100)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess3"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation1"), -1.93)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation1"), 2.04)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation1"), 1.78)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation2"), 0.78)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation2"), 3.3)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation2"), 0)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation3"), 0.78)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation3"), 3.3)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation3"), 0)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(self.model, pipeline)

    def update(self, snake):
        choice = self.game.empty - set(snake.tail) - {snake.pos}
        if choice != set():
            self.pos = rd.choice(list(choice))
            self.view_pos = get_pos(self.g_grid, self.g_size, self.pos)
            self.game.view_food = self.view_pos
        else:
            self.game.notFood = True


class Background(object):
    def __init__(self, game, cam, image):
        self.game = game
        self.cam = cam

        gpu_BG_quad = es.toGPUShape(
            bs.createTextureNormalsQuad(image, game.size, game.size), GL_REPEAT,
            GL_LINEAR)

        gpu_lamp_obj = es.toGPUShape(
            bs.readOBJ('libs/obj/streetLamp.obj', (0.1, 0.1, 0.1)))

        gpu_light_cube = es.toGPUShape(
            bs.createColorNormalsCube(1, 1, 1))

        gpu_wall_cube_h = es.toGPUShape(
            bs.createTextureNormalsQuad('libs/fig/bricks.png', game.size+1, 1), GL_REPEAT,
            GL_LINEAR)

        gpu_wall_cube_v = es.toGPUShape(
            bs.createTextureNormalsQuad('libs/fig/bricks.png', game.size, 1), GL_REPEAT,
            GL_LINEAR)

        BG = sg.SceneGraphNode('BG')
        BG.transform = tr.uniformScale(2)  # tr.scale(2, 2, 0.001)  #
        BG.childs += [gpu_BG_quad]

        _lamp = sg.SceneGraphNode('_lamp')
        _lamp.transform = tr.matmul([
            tr.rotationZ(np.pi / 4),
            tr.rotationX(3.14 / 2),
            tr.uniformScale(0.00045),
            tr.translate(0, -560, 0)])
        _lamp.childs += [gpu_lamp_obj]

        light = sg.SceneGraphNode('light')
        light.transform = tr.matmul([
            tr.translate(0, 0, 0.35),
            tr.uniformScale(0.03)])
        light.childs += [gpu_light_cube]

        lamp = sg.SceneGraphNode('lamp')
        lamp.transform = tr.uniformScale(0.8)
        lamp.childs += [_lamp, light]

        lamp1 = sg.SceneGraphNode('lamp1')
        lamp1.transform = tr.matmul([
            tr.translate(1, 1, 0)
        ])
        lamp1.childs += [lamp]

        lamp2 = sg.SceneGraphNode('lamp2')
        lamp2.transform = tr.matmul([
            tr.translate(-1, 1, 0)
        ])
        lamp2.childs += [lamp]

        lamp3 = sg.SceneGraphNode('lamp3')
        lamp3.transform = tr.matmul([
            tr.translate(1, -1, 0)
        ])
        lamp3.childs += [lamp]

        lamp4 = sg.SceneGraphNode('lamp4')
        lamp4.transform = tr.matmul([
            tr.translate(-1, -1, 0)
        ])
        lamp4.childs += [lamp]

        lamps = sg.SceneGraphNode('lamps')
        lamps.childs += [lamp1, lamp2, lamp3, lamp4]

        wall_v = sg.SceneGraphNode('wall_v')
        wall_v.transform = tr.matmul([
            tr.rotationX(np.pi/2),
            tr.uniformScale(2*game.grid),
            tr.translate(
                tx=0,
                ty=0.5,
                tz=0),
            tr.scale(game.size, 1, 1)])
        wall_v.childs += [gpu_wall_cube_v]

        wall_h = sg.SceneGraphNode('wall_h')
        wall_h.transform = tr.matmul([
            tr.rotationX(0),
            tr.uniformScale(2*game.grid),
            tr.translate(
                tx=0.5,
                ty=0.5,
                tz=1),
            tr.scale(game.size+1, 1, 1)])
        wall_h.childs += [gpu_wall_cube_h]

        wall = sg.SceneGraphNode('wall')
        wall.childs += [wall_h, wall_v]

        wall1 = sg.SceneGraphNode('wall1')
        wall1.transform = tr.translate(
            tx=0,
            ty=1,
            tz=0
        )
        wall1.childs += [wall]

        wall2 = sg.SceneGraphNode('wall2')
        wall2.transform = tr.matmul([tr.translate(
            tx=0,
            ty=-1,
            tz=0),
            tr.rotationZ(np.pi)])
        wall2.childs += [wall]

        wall3 = sg.SceneGraphNode('wall3')
        wall3.transform = tr.matmul([tr.translate(
            tx=-1,
            ty=0,
            tz=0),
            tr.rotationZ(np.pi/2)])
        wall3.childs += [wall]

        wall4 = sg.SceneGraphNode('wall4')
        wall4.transform = tr.matmul([tr.translate(
            tx=1,
            ty=0,
            tz=0),
            tr.rotationZ(-np.pi/2)])
        wall4.childs += [wall]

        BG_tr = sg.SceneGraphNode('BG_tr')
        BG_tr.childs += [BG, wall1, wall2, wall3, wall4]

        self.model_tx = BG_tr
        self.model_col = lamps

    def draw(self, pipeline_tx, pipeline_col, projection, view, size):
        dict = {'tx': (pipeline_tx, self.model_tx), 'col': (pipeline_col, self.model_col)}
        for p in ['tx', 'col']:
            pipeline = dict[p][0]
            glUseProgram(pipeline.shaderProgram)

            # White light in all components: ambient, diffuse and specular.
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La1"), 0.8, 0.2, 0.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld1"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls1"), 1.0, 1.0, 1.0)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La2"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld2"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls2"), 1.0, 1.0, 1.0)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La3"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld3"), 1, 0.01, 0.01)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls3"), 1.0, 0.3, 0.3)

            # Object is barely visible at only ambient. Bright white for diffuse and specular components.
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka1"), 0.008, 0.008, 0.008)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd1"), 0.5, 0.5, 0.5)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks1"), 0, 0, 0)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka2"), 0, 0, 0)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd2"), 0.7, 1.0, 0.7)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks2"), 0.0, 0.0, 0.0)

            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka3"), -0.04, -0.04, -0.04)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd3"), 1.0, 0.7, 0.7)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks3"), 0.36, 0.36, 0.36)

            # TO DO: Explore different parameter combinations to understand their effect!

            viewPos = self.game.view_cam
            snakePos = self.game.view_pos
            foodPos = self.game.view_food
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition1"), 0, 0, 1.5)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition2"), snakePos[0], snakePos[1], 0.09)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition3"), foodPos[0], foodPos[1], 0.04)
            glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1],
                        viewPos[2])

            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess1"), -1)
            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess2"), -1)
            glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess3"), 100)

            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation1"), -1.93)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation1"), 2.04)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation1"), 1.78)

            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation2"), 0.58)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation2"), 3.3)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation2"), 0)

            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation3"), 0.78)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation3"), 3.3)
            glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation3"), 0)

            lamps = {1: (1, 1), 2: (-1, 1), 3: (1, -1), 4: (-1, -1)}
            for j in range(1, size+1):
                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"La{3 + j}"), 1.0, 1.0, 1.0)
                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ld{3 + j}"), 1, 1, 1)
                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ls{3 + j}"), 1.0, 1.0, 1.0)

                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ka{3 + j}"), -0.04, -0.04, -0.04)
                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Kd{3 + j}"), 0.95, 1.0, 1.0)
                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"Ks{3 + j}"), 0.5, 0.5, 0.5)

                glUniform3f(glGetUniformLocation(pipeline.shaderProgram, f"lightPosition{3 + j}"),
                            0.9 * lamps[j][0], 0.9 * lamps[j][1], 0.34)

                glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, f"shininess{3 + j}"),
                             int(90+10*(np.sin(8*lamps[j][0]*self.game.t) + np.cos(5*lamps[j][1]*self.game.t))))

                glUniform1f(glGetUniformLocation(pipeline.shaderProgram, f"constantAttenuation{3 + j}"), 0.63)
                glUniform1f(glGetUniformLocation(pipeline.shaderProgram, f"linearAttenuation{3 + j}"), 0.59)
                glUniform1f(glGetUniformLocation(pipeline.shaderProgram, f"quadraticAttenuation{3 + j}"), 4)

            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
            # Drawing
            model = dict[p][1]
            sg.drawSceneGraphNode(model, pipeline)


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
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(model, pipeline, transformName='transform')


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

    def __init__(self, g):
        self.game = g
        self.status = 'R'
        ratio = 16 / 9
        self.projection = [
            tr.ortho(-1.1 * ratio, 1.1 * ratio, -1.1, 1.1, 0.1, 100),
            tr.perspective(2.2 * np.pi, ratio, 0.1, 100),
            tr.perspective(2 * np.pi, ratio, 0.1, 100)
        ]

    def get_cam_gta(self):
        view_cam = np.array([7 * np.sin(self.game.cam_angle) + self.game.view_pos[0],
                             -7 * np.cos(self.game.cam_angle) + self.game.view_pos[1], 6.1])
        self.game.view_cam = view_cam
        view_gta = tr.lookAt(
            view_cam,
            np.array([self.game.view_pos[i] for i in range(2)] + [1.8 * self.game.grid / 2]),
            np.array([0, 0, 1]))
        return self.projection[2], view_gta

    def get_cam_map(self):
        self.game.view_cam = np.array([0, 0, 10])
        view_map = tr.lookAt(
            np.array([0, 0, 10]),
            np.array([0, 0, 0]),
            np.array([0, 1, 0]))
        return self.projection[0], view_map

    def get_cam_pers(self):
        self.game.view_cam = np.array([0, -10.8, 10])
        view_pers = tr.lookAt(
            np.array([0, -10.8, 10]),
            np.array([0, 0, 0]),
            np.array([0, 0, 1]))
        return self.projection[1], view_pers

    def get_cam(self):
        if self.status == 'R':
            return self.get_cam_gta()

        elif self.status == 'T':
            return self.get_cam_pers()

        elif self.status == 'E':
            return self.get_cam_map()


def get_pos(grid, size, pos, next_pos=None, current=None, i=0, m=1):
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


def get_theta(theta_1, theta_2, i=0, m=1):
    if theta_1 == 0 and theta_2 == 3 * np.pi / 2:
        return (i / m) * (-np.pi / 2) + (1 - i / m) * theta_1
    elif theta_2 == 0 and theta_1 == 3 * np.pi / 2:
        return (i / m) * (2 * np.pi) + (1 - i / m) * theta_1
    else:
        return (i / m) * theta_2 + (1 - i / m) * theta_1
