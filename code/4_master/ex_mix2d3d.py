# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
Example drawing 2D over a 3D world.
The trick is to not clear the color buffer after drawing 3D, and then draw 2D with the shader.

If it is required to draw 3D over 2D, you may need to clear the depth buffer with
glClear(GL_DEPTH_BUFFER_BIT)
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import easy_shaders as es

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Example 2D-3D", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    texture2dPipeline = es.SimpleTextureTransformShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    gpuRainbowCube = es.toGPUShape(bs.createRainbowCube())
    gpuAxis = es.toGPUShape(bs.createAxis(2))
    gpuBoo = es.toGPUShape(bs.createTextureQuad("boo.png"), GL_REPEAT, GL_NEAREST)
    gpuQuestionBox = es.toGPUShape(bs.createTextureQuad("question_box.png", 10, 1), GL_REPEAT, GL_NEAREST)

    questionBoxTransform = np.matmul(tr.translate(0, -0.8, 0), tr.scale(2, 0.2, 1))

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        projection = tr.perspective(30, float(width)/float(height), 0.1, 100)

        view = tr.lookAt(
            np.array([5,5,2]),
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        theta = glfw.get_time()
        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.rotationA(theta, axis)

        # Drawing axes and cube in a 3D world
        glUseProgram(mvpPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        mvpPipeline.drawShape(gpuAxis, GL_LINES)

        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, model)
        mvpPipeline.drawShape(gpuRainbowCube)

        theta = glfw.get_time()
        tx = 0.7 * np.sin(0.5 * theta)
        ty = 0.2 * np.sin(5 * theta)
    
        # derivative of tx give us the direction
        dtx = 0.7 * 0.5 * np.cos(0.5 * theta)
        if dtx > 0:
            reflex = tr.identity()
        else:
            reflex = tr.scale(-1, 1, 1)

        glUseProgram(texture2dPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texture2dPipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                tr.translate(tx, ty, 0),
                tr.scale(0.5, 0.5, 1.0),
                reflex]))
        texture2dPipeline.drawShape(gpuBoo)

        glUniformMatrix4fv(glGetUniformLocation(texture2dPipeline.shaderProgram, "transform"), 1, GL_TRUE, questionBoxTransform)
        texture2dPipeline.drawShape(gpuQuestionBox)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
