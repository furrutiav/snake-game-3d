"""
-----------> VIEW <-----------
"""

import glfw
import sys
from time import *
from libs.models import *
from libs.controller import Controller

N = int(sys.argv[1])

if __name__ == '__main__':
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

    window = glfw.create_window(width, height, 'Snake Game; Autor: Felipe Urrutia V.', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controller = Controller()

    game = Game(N)

    glfw.set_key_callback(window, controller.on_key)

    pipeline_tx = es.SimpleTextureTransformShaderProgram()
    pipeline_pol = es.SimpleTransformShaderProgram()

    glClearColor(48/255, 48/255, 48/255, 1.0)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    bg = Background(game)
    food = Food(game)
    snake = Snake(game, food)
    iW = interactiveWindow()

    controller.set_snake(snake)
    controller.set_game(game)

    t0 = 0
    t = 0
    while not glfw.window_should_close(window):
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)

        if game.pause or game.dead or game.win or game.speed:
            glUseProgram(pipeline_tx.shaderProgram)
            if game.pause:
                iW.draw(pipeline_tx, game.time_pause, 'pause')
                if game.time_pause < 2*np.pi:
                    game.time_pause += 0.01
                else:
                    game.time_pause = 2*np.pi

            elif game.win:
                iW.draw(pipeline_tx, game.time_pause, 'win')
                if game.time_pause < 2*np.pi:
                    if game.time_pause == 0:
                        sleep(0.1)
                    game.time_pause += 0.005
                else:
                    game.time_pause = 2*np.pi

            elif game.dead:
                iW.draw(pipeline_tx, game.time_pause, 'dead')
                if game.time_pause < 2*np.pi:
                    game.time_pause += 0.01
                else:
                    game.time_pause = 2*np.pi
            elif game.speed:
                iW.draw(pipeline_tx, game.time_pause, 'speed')
                if game.time_pause < 2*np.pi:
                    game.time_pause += 0.01
                else:
                    game.time_pause = 2*np.pi
        else:
            glUseProgram(pipeline_pol.shaderProgram)
            bg.draw(pipeline_pol)
            food.draw(pipeline_pol, ti)

            glUseProgram(pipeline_tx.shaderProgram)
            snake.draw(pipeline_tx)

        if t * dt > game.time:
            snake.update()
            snake.collide()
            t = 0

        glfw.swap_buffers(window)
        t += 1

    glfw.terminate()
