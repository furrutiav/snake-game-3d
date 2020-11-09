
# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
Projections example
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import transformations as tr
import basic_shapes as bs
import easy_shaders as es


PROJECTION_ORTHOGRAPHIC = 0
PROJECTION_FRUSTUM = 1
PROJECTION_PERSPECTIVE = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.projection = PROJECTION_ORTHOGRAPHIC


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_1:
        print('Orthographic projection')
        controller.projection = PROJECTION_ORTHOGRAPHIC

    elif key == glfw.KEY_2:
        print('Frustum projection')
        controller.projection = PROJECTION_FRUSTUM

    elif key == glfw.KEY_3:
        print('Perspective projection')
        controller.projection = PROJECTION_PERSPECTIVE

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Projections Demo", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    pipeline = es.SimpleModelViewProjectionShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))
    gpuRedCube = es.toGPUShape(bs.createColorCube(1,0,0))
    gpuGreenCube = es.toGPUShape(bs.createColorCube(0,1,0))
    gpuBlueCube = es.toGPUShape(bs.createColorCube(0,0,1))
    gpuYellowCube = es.toGPUShape(bs.createColorCube(1,1,0))
    gpuCyanCube = es.toGPUShape(bs.createColorCube(0,1,1))
    gpuPurpleCube = es.toGPUShape(bs.createColorCube(1,0,1))
    gpuRainbowCube = es.toGPUShape(bs.createRainbowCube())

    t0 = glfw.get_time()
    camera_theta = np.pi/4

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        # Setting up the view transform

        camX = 10 * np.sin(camera_theta)
        camY = 10 * np.cos(camera_theta)

        viewPos = np.array([camX, camY, 10])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform

        if controller.projection == PROJECTION_ORTHOGRAPHIC:
            projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

        elif controller.projection == PROJECTION_FRUSTUM:
            projection = tr.frustum(-5, 5, -5, 5, 9, 100)

        elif controller.projection == PROJECTION_PERSPECTIVE:
            projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        
        else:
            raise Exception()

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)


        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes with different model transformations
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(5,0,0))
        pipeline.drawShape(gpuRedCube)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(-5,0,0))
        pipeline.drawShape(gpuGreenCube)


        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0,5,0))
        pipeline.drawShape(gpuBlueCube)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0,-5,0))
        pipeline.drawShape(gpuYellowCube)


        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0,0,5))
        pipeline.drawShape(gpuCyanCube)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0,0,-5))
        pipeline.drawShape(gpuPurpleCube)


        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(gpuRainbowCube)
        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(gpuAxis, GL_LINES)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
