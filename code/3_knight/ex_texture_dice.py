# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
Textures and transformations in 3D
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


def createDice(image_filename):

    # Defining locations and texture coordinates for each vertex of the shape  
    vertices = [
    #   positions         texture coordinates
    # Z+: number 1
        -0.5, -0.5,  0.5, 0, 1/3,
         0.5, -0.5,  0.5, 1/2, 1/3,
         0.5,  0.5,  0.5, 1/2, 0,
        -0.5,  0.5,  0.5, 0, 0,

    # Z-: number 6
        -0.5, -0.5, -0.5, 1/2, 1,
         0.5, -0.5, -0.5, 1, 1,
         0.5,  0.5, -0.5, 1, 2/3,
        -0.5,  0.5, -0.5, 1/2, 2/3,
        
    # X+: number 5
         0.5, -0.5, -0.5, 0, 1,
         0.5,  0.5, -0.5, 1/2, 1,
         0.5,  0.5,  0.5, 1/2, 2/3,
         0.5, -0.5,  0.5, 0, 2/3,
 
    # X-: number 2
        -0.5, -0.5, -0.5, 1/2, 1/3,
        -0.5,  0.5, -0.5, 1, 1/3,
        -0.5,  0.5,  0.5, 1, 0,
        -0.5, -0.5,  0.5, 1/2, 0,

    # Y+: number 4
        -0.5,  0.5, -0.5, 1/2, 2/3,
         0.5,  0.5, -0.5, 1, 2/3,
         0.5,  0.5,  0.5, 1, 1/3,
        -0.5,  0.5,  0.5, 1/2, 1/3,

    # Y-: number 3
        -0.5, -0.5, -0.5, 0, 2/3,
         0.5, -0.5, -0.5, 1/2, 2/3,
         0.5, -0.5,  0.5, 1/2, 1/3,
        -0.5, -0.5,  0.5, 0, 1/3
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return bs.Shape(vertices, indices, image_filename)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Dice", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colores
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuDice = es.toGPUShape(createDice("dice_blue.jpg"), GL_REPEAT, GL_LINEAR)
    gpuAxis = es.toGPUShape(bs.createAxis(2))

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

        projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)

        view = tr.lookAt(
            np.array([10,10,5]),
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        theta = glfw.get_time()
        axis = np.array([1,-1,1])
        axis = axis / np.linalg.norm(axis)
        model = tr.rotationA(theta, axis)

        # Drawing axes (no texture)
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        colorShaderProgram.drawShape(gpuAxis, GL_LINES)

        # Drawing dice (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "model"), 1, GL_TRUE, model)
        textureShaderProgram.drawShape(gpuDice)        

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
