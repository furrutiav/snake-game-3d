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

    width = int(1920 * 1)
    height = int(1080 * 1)
    window = glfw.create_window(
        width, height, 'Snake Game 3D; Autor: F. Urrutia V.', glfw.get_primary_monitor(), None)   # glfw.get_primary_monitor()

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    game = Game(N)

    glfw.set_key_callback(window, controller.on_key)
    glfw.set_scroll_callback(window, controller.on_scroll)
    # glfw.set_cursor_pos_callback(window, controller.on_cursor)

    pipeline_tx = es.SimpleTextureModelViewProjectionShaderProgram()
    pipeline_ls_tx = ls.SimpleTexturePhongShaderProgram()
    pipeline_ls_tx2 = ls.SimpleTexturePhongShaderProgramMulti(2)
    pipeline_ls_tx3 = ls.SimpleTexturePhongShaderProgramMulti(3)
    pipeline_ls_tx4 = ls.SimpleTexturePhongShaderProgramMulti(4)
    pipeline_ls_tx7 = ls.SimpleTexturePhongShaderProgramMulti(7)
    pipeline_col = es.SimpleModelViewProjectionShaderProgram()
    pipeline_ls_col = ls.SimplePhongShaderProgram()
    pipeline_ls_col2 = ls.SimplePhongShaderProgramMulti(2)
    pipeline_ls_col3 = ls.SimplePhongShaderProgramMulti(3)
    pipeline_ls_col4 = ls.SimplePhongShaderProgramMulti(4)
    pipeline_ls_col7 = ls.SimplePhongShaderProgramMulti(7)

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
            elif game.speed:
                iW.draw(pipeline_tx_2d, game.time_pause, 'speed')
                if game.time_pause < 2*np.pi:
                    game.time_pause += 0.01
                else:
                    game.time_pause = 2*np.pi
        else:
            projection, view = cam.get_cam()

            axis.draw(pipeline_col, projection, view)

            bg.draw(pipeline_ls_tx7, pipeline_ls_col7, projection, view)

            food.draw(pipeline_ls_col3, projection, view, ti)

            snake.draw(pipeline_ls_col7, projection, view)

        if game.check_time():
            snake.update()
            snake.collide()

        glfw.swap_buffers(window)
        game.count_time()
    glfw.terminate()
