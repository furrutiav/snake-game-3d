"""
-----------> VIEW <-----------
"""
import glfw
import sys
from libs.models import *
from libs.controller import Controller
from time import sleep

N = 20  # int(sys.argv[1])

if __name__ == '__main__':
    if not glfw.init():
        sys.exit()

    width = int(1920 * 0.8)
    height = int(1080 * 0.8)
    window = glfw.create_window(
        width, height, 'Snake Game 3D; Autor: F. Urrutia V.', None, None)   # glfw.get_primary_monitor()

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
    iW = interactiveWindow()
    cam = Cam(game)
    bg = Background(game, cam, 'libs/fig/bricks.png')

    controller.set_snake(snake)
    controller.set_game(game)
    controller.set_cam(cam)

    axis = Axis(100)

    while not glfw.window_should_close(window):

        ti = glfw.get_time()
        game.post_time(ti)

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if game.pause or game.dead or game.win or game.speed:
            if game.pause:
                iW.draw(pipeline_tx_2d, game.time_pause, 'pause')
                if game.time_pause < 2*np.pi:
                    game.time_pause += 0.01
                else:
                    game.time_pause = 2*np.pi

            elif game.win:
                iW.draw(pipeline_tx_2d, game.time_pause, 'win')
                if game.time_pause < 2*np.pi:
                    if game.time_pause == 0:
                        sleep(0.1)
                    game.time_pause += 0.005
                else:
                    game.time_pause = 2*np.pi

            elif game.dead:
                iW.draw(pipeline_tx_2d, game.time_pause, 'dead')
                if game.time_pause < 2*np.pi:
                    game.time_pause += 0.01
                else:
                    game.time_pause = 2*np.pi
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
