"""
-----------> VIEW <-----------
"""

import glfw
import sys
from libs.models import *
from libs.controller import Controller

N = 10  # int(sys.argv[1])

if __name__ == '__main__':
    if not glfw.init():
        sys.exit()

    width = int(1920 * 0.7)
    height = int(1080 * 0.7)
    window = glfw.create_window(width, height, 'Snake Game 3D; Autor: Felipe Urrutia V.', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    game = Game(N)

    glfw.set_key_callback(window, controller.on_key)

    pipeline_tx = es.SimpleTextureModelViewProjectionShaderProgram()
    pipeline_col = es.SimpleModelViewProjectionShaderProgram()

    glClearColor(48/255, 48/255, 48/255, 1.0)

    glEnable(GL_DEPTH_TEST)

    bg = Background(game, "bricks.png")
    food = Food(game)
    snake = Snake(game, food)
    iW = interactiveWindow()

    controller.set_snake(snake)
    controller.set_game(game)

    axis = Axis(100)

    ratio = 16/9
    projection = tr.ortho(-1*ratio, 1*ratio, -1, 1, 0.1, 1000)

    view0 = tr.lookAt(
        np.array([10, -10, 10]),
        np.array([0, 0, 0]),
        np.array([0, 0, 1])
    )

    view1 = tr.lookAt(
        np.array([0, 0, 10]),
        np.array([0, 0, 0]),
        np.array([0, 1, 0])
    )
    view = [view0, view1][1]
    while not glfw.window_should_close(window):
        ti = glfw.get_time()
        game.post_time(ti)

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # if game.pause or game.dead or game.win or game.speed:
        #     glUseProgram(pipeline_tx.shaderProgram)
        #     if game.pause:
        #         iW.draw(pipeline_tx, game.time_pause, 'pause')
        #         if game.time_pause < 2*np.pi:
        #             game.time_pause += 0.01
        #         else:
        #             game.time_pause = 2*np.pi
        #
        #     elif game.win:
        #         iW.draw(pipeline_tx, game.time_pause, 'win')
        #         if game.time_pause < 2*np.pi:
        #             if game.time_pause == 0:
        #                 sleep(0.1)
        #             game.time_pause += 0.005
        #         else:
        #             game.time_pause = 2*np.pi
        #
        #     elif game.dead:
        #         iW.draw(pipeline_tx, game.time_pause, 'dead')
        #         if game.time_pause < 2*np.pi:
        #             game.time_pause += 0.01
        #         else:
        #             game.time_pause = 2*np.pi
        #     elif game.speed:
        #         iW.draw(pipeline_tx, game.time_pause, 'speed')
        #         if game.time_pause < 2*np.pi:
        #             game.time_pause += 0.01
        #         else:
        #             game.time_pause = 2*np.pi
        # else:

        axis.draw(pipeline_col, projection, view)

        bg.draw(pipeline_tx, projection, view)

        food.draw(pipeline_col, projection, view, ti)

        snake.draw(pipeline_col, projection, view)

        if game.check_time():
            snake.update()
            snake.collide()

        glfw.swap_buffers(window)
        game.count_time()
    glfw.terminate()
