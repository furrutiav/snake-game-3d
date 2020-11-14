"""
-----------> VIEW <-----------
"""
import glfw
import sys
from libs.models import *
from libs.controller import Controller
from time import time

N = 20
fullScreen = 0  # int(sys.argv[1]) == 1

if __name__ == '__main__':
    if not glfw.init():
        sys.exit()

    wFun = None
    wSize = 0.6
    if fullScreen:
        wFun = glfw.get_primary_monitor()
        wSize = 1

    width = int(1920 * wSize)
    height = int(1080 * wSize)
    window = glfw.create_window(
        width, height, 'Snake Game 3D; Autor: F. Urrutia V.', wFun, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    game = Game(N)

    glfw.set_key_callback(window, controller.on_key)
    glfw.set_scroll_callback(window, controller.on_scroll)

    pipelines_ls_col = [ls.SimplePhongShaderProgramMulti(i) for i in range(3, 8)]
    pipelines_ls_tx = [ls.SimpleTexturePhongShaderProgramMulti(i) for i in range(3, 8)]

    pipeline_tx_2d = es.SimpleTextureTransformShaderProgram()

    glClearColor(8 / 255, 8 / 255, 8 / 255, 1.0)

    glEnable(GL_DEPTH_TEST)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    food = Food(game)
    snake = Snake(game, food)
    iW = interactiveWindow(game)
    cam = Cam(game)
    bg = Background(game, cam, 'libs/fig/bricks.png', 'libs/fig/leaves.png')

    controller.set_snake(snake)
    controller.set_game(game)
    controller.set_cam(cam)

    while not glfw.window_should_close(window):

        ti = glfw.get_time()
        game.post_time(ti)

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if game.pause or game.dead or game.win or game.speed:
            if game.pause:
                iW.draw(pipeline_tx_2d, 'pause')
            elif game.win:
                iW.draw(pipeline_tx_2d, 'win')
            elif game.dead:
                iW.draw(pipeline_tx_2d, 'dead')
        else:
            projection, view = cam.get_cam()

            top = game.count_food
            if top > 3:
                top = 4

            bg.draw(pipelines_ls_tx[top], pipelines_ls_col[top], projection, view, top)
            food.draw(pipelines_ls_col[0], projection, view, ti)
            snake.draw(pipelines_ls_col[top], projection, view, top)

        if game.check_time():
            snake.update()
            snake.collide()

        glfw.swap_buffers(window)
        game.count_time()
    glfw.terminate()
