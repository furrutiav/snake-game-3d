# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
vertices and indices for simple shapes

F. Urrutia V., CC3501, 2020-1
add createTextureQuad(REPEAT), createTextureNormalsQuad(REPEAT), read(OBJ)
"""


# A simple class container to store vertices and indices that define a shape
class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName


def createAxis(length=1.0):
    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #    positions        colors
        -length, 0.0, 0.0, 0.0, 0.0, 0.0,
        length, 0.0, 0.0, 1.0, 0.0, 0.0,

        0.0, -length, 0.0, 0.0, 0.0, 0.0,
        0.0, length, 0.0, 0.0, 1.0, 0.0,

        0.0, 0.0, -length, 0.0, 0.0, 0.0,
        0.0, 0.0, length, 0.0, 0.0, 1.0]

    # This shape is meant to be drawn with GL_LINES,
    # i.e. every 2 indices, we have 1 line.
    indices = [
        0, 1,
        2, 3,
        4, 5]

    return Shape(vertices, indices)


def createRainbowTriangle():
    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #   positions        colors
        -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
        0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
        0.0, 0.5, 0.0, 0.0, 0.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return Shape(vertices, indices)


def createRainbowQuad():
    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #   positions        colors
        -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
        0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.0, 0.0, 0.0, 1.0,
        -0.5, 0.5, 0.0, 1.0, 1.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0]

    return Shape(vertices, indices)


def createColorQuad(r, g, b):
    # Defining locations and colors for each vertex of the shape
    vertices = [
        #   positions        colors
        -0.5, -0.5, 0.0, r, g, b,
        0.5, -0.5, 0.0, r, g, b,
        0.5, 0.5, 0.0, r, g, b,
        -0.5, 0.5, 0.0, r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0]

    return Shape(vertices, indices)


def createTextureQuad(image_filename, nx=1, ny=1):
    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        #   positions        texture
        -0.5, -0.5, 0.0, 0, ny,
        0.5, -0.5, 0.0, nx, ny,
        0.5, 0.5, 0.0, nx, 0,
        -0.5, 0.5, 0.0, 0, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0]

    textureFileName = image_filename

    return Shape(vertices, indices, textureFileName)


def createRainbowCube():
    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #    positions         colors
        -0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
        0.5, -0.5, 0.5, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
        -0.5, 0.5, 0.5, 1.0, 1.0, 1.0,

        -0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
        0.5, -0.5, -0.5, 0.0, 1.0, 1.0,
        0.5, 0.5, -0.5, 1.0, 0.0, 1.0,
        -0.5, 0.5, -0.5, 1.0, 1.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7]

    return Shape(vertices, indices)


def createColorCube(r, g, b):
    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #    positions        colors
        -0.5, -0.5, 0.5, r, g, b,
        0.5, -0.5, 0.5, r, g, b,
        0.5, 0.5, 0.5, r, g, b,
        -0.5, 0.5, 0.5, r, g, b,

        -0.5, -0.5, -0.5, r, g, b,
        0.5, -0.5, -0.5, r, g, b,
        0.5, 0.5, -0.5, r, g, b,
        -0.5, 0.5, -0.5, r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7]

    return Shape(vertices, indices)


def createTextureCube(image_filename):
    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        #   positions         texture coordinates
        # Z+
        -0.5, -0.5, 0.5, 0, 1,
        0.5, -0.5, 0.5, 1, 1,
        0.5, 0.5, 0.5, 1, 0,
        -0.5, 0.5, 0.5, 0, 0,

        # Z-
        -0.5, -0.5, -0.5, 0, 1,
        0.5, -0.5, -0.5, 1, 1,
        0.5, 0.5, -0.5, 1, 0,
        -0.5, 0.5, -0.5, 0, 0,

        # X+
        0.5, -0.5, -0.5, 0, 1,
        0.5, 0.5, -0.5, 1, 1,
        0.5, 0.5, 0.5, 1, 0,
        0.5, -0.5, 0.5, 0, 0
        ,

        # X-
        -0.5, -0.5, -0.5, 0, 1,
        -0.5, 0.5, -0.5, 1, 1,
        -0.5, 0.5, 0.5, 1, 0,
        -0.5, -0.5, 0.5, 0, 0,

        # Y+
        -0.5, 0.5, -0.5, 0, 1,
        0.5, 0.5, -0.5, 1, 1,
        0.5, 0.5, 0.5, 1, 0,
        -0.5, 0.5, 0.5, 0, 0,

        # Y-
        -0.5, -0.5, -0.5, 0, 1,
        0.5, -0.5, -0.5, 1, 1,
        0.5, -0.5, 0.5, 1, 0,
        -0.5, -0.5, 0.5, 0, 0
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,  # Z+
        7, 6, 5, 5, 4, 7,  # Z-
        8, 9, 10, 10, 11, 8,  # X+
        15, 14, 13, 13, 12, 15,  # X-
        19, 18, 17, 17, 16, 19,  # Y+
        20, 21, 22, 22, 23, 20]  # Y-

    return Shape(vertices, indices, image_filename)


def createRainbowNormalsCube():
    sq3 = 0.57735027

    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #    positions        colors          normals
        -0.5, -0.5, 0.5, 1.0, 0.0, 0.0, -sq3, -sq3, sq3,
        0.5, -0.5, 0.5, 0.0, 1.0, 0.0, sq3, -sq3, sq3,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0, sq3, sq3, sq3,
        -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, -sq3, sq3, sq3,

        -0.5, -0.5, -0.5, 1.0, 1.0, 0.0, -sq3, -sq3, -sq3,
        0.5, -0.5, -0.5, 0.0, 1.0, 1.0, sq3, -sq3, -sq3,
        0.5, 0.5, -0.5, 1.0, 0.0, 1.0, sq3, sq3, -sq3,
        -0.5, 0.5, -0.5, 1.0, 1.0, 1.0, -sq3, sq3, -sq3]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2, 2, 3, 0,
               4, 5, 6, 6, 7, 4,
               4, 5, 1, 1, 0, 4,
               6, 7, 3, 3, 2, 6,
               5, 6, 2, 2, 1, 5,
               7, 4, 0, 0, 3, 7]

    return Shape(vertices, indices)


def createColorNormalsCube(r, g, b):
    # Defining the location and colors of each vertex  of the shape
    vertices = [
        #   positions         colors   normals
        # Z+
        -0.5, -0.5, 0.5, r, g, b, 0, 0, 1,
        0.5, -0.5, 0.5, r, g, b, 0, 0, 1,
        0.5, 0.5, 0.5, r, g, b, 0, 0, 1,
        -0.5, 0.5, 0.5, r, g, b, 0, 0, 1,

        # Z-
        -0.5, -0.5, -0.5, r, g, b, 0, 0, -1,
        0.5, -0.5, -0.5, r, g, b, 0, 0, -1,
        0.5, 0.5, -0.5, r, g, b, 0, 0, -1,
        -0.5, 0.5, -0.5, r, g, b, 0, 0, -1,

        # X+
        0.5, -0.5, -0.5, r, g, b, 1, 0, 0,
        0.5, 0.5, -0.5, r, g, b, 1, 0, 0,
        0.5, 0.5, 0.5, r, g, b, 1, 0, 0,
        0.5, -0.5, 0.5, r, g, b, 1, 0, 0,

        # X-
        -0.5, -0.5, -0.5, r, g, b, -1, 0, 0,
        -0.5, 0.5, -0.5, r, g, b, -1, 0, 0,
        -0.5, 0.5, 0.5, r, g, b, -1, 0, 0,
        -0.5, -0.5, 0.5, r, g, b, -1, 0, 0,

        # Y+
        -0.5, 0.5, -0.5, r, g, b, 0, 1, 0,
        0.5, 0.5, -0.5, r, g, b, 0, 1, 0,
        0.5, 0.5, 0.5, r, g, b, 0, 1, 0,
        -0.5, 0.5, 0.5, r, g, b, 0, 1, 0,

        # Y-
        -0.5, -0.5, -0.5, r, g, b, 0, -1, 0,
        0.5, -0.5, -0.5, r, g, b, 0, -1, 0,
        0.5, -0.5, 0.5, r, g, b, 0, -1, 0,
        -0.5, -0.5, 0.5, r, g, b, 0, -1, 0
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,  # Z+
        7, 6, 5, 5, 4, 7,  # Z-
        8, 9, 10, 10, 11, 8,  # X+
        15, 14, 13, 13, 12, 15,  # X-
        19, 18, 17, 17, 16, 19,  # Y+
        20, 21, 22, 22, 23, 20]  # Y-

    return Shape(vertices, indices)


def createTextureNormalsCube(image_filename):
    # Defining locations,texture coordinates and normals for each vertex of the shape
    vertices = [
        #   positions            tex coords   normals
        # Z+
        -0.5, -0.5, 0.5, 0, 1, 0, 0, 1,
        0.5, -0.5, 0.5, 1, 1, 0, 0, 1,
        0.5, 0.5, 0.5, 1, 0, 0, 0, 1,
        -0.5, 0.5, 0.5, 0, 0, 0, 0, 1,
        # Z-
        -0.5, -0.5, -0.5, 0, 1, 0, 0, -1,
        0.5, -0.5, -0.5, 1, 1, 0, 0, -1,
        0.5, 0.5, -0.5, 1, 0, 0, 0, -1,
        -0.5, 0.5, -0.5, 0, 0, 0, 0, -1,

        # X+
        0.5, -0.5, -0.5, 0, 1, 1, 0, 0,
        0.5, 0.5, -0.5, 1, 1, 1, 0, 0,
        0.5, 0.5, 0.5, 1, 0, 1, 0, 0,
        0.5, -0.5, 0.5, 0, 0, 1, 0, 0,
        # X-
        -0.5, -0.5, -0.5, 0, 1, -1, 0, 0,
        -0.5, 0.5, -0.5, 1, 1, -1, 0, 0,
        -0.5, 0.5, 0.5, 1, 0, -1, 0, 0,
        -0.5, -0.5, 0.5, 0, 0, -1, 0, 0,
        # Y+
        -0.5, 0.5, -0.5, 0, 1, 0, 1, 0,
        0.5, 0.5, -0.5, 1, 1, 0, 1, 0,
        0.5, 0.5, 0.5, 1, 0, 0, 1, 0,
        -0.5, 0.5, 0.5, 0, 0, 0, 1, 0,
        # Y-
        -0.5, -0.5, -0.5, 0, 1, 0, -1, 0,
        0.5, -0.5, -0.5, 1, 1, 0, -1, 0,
        0.5, -0.5, 0.5, 1, 0, 0, -1, 0,
        -0.5, -0.5, 0.5, 0, 0, 0, -1, 0
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,  # Z+
        7, 6, 5, 5, 4, 7,  # Z-
        8, 9, 10, 10, 11, 8,  # X+
        15, 14, 13, 13, 12, 15,  # X-
        19, 18, 17, 17, 16, 19,  # Y+
        20, 21, 22, 22, 23, 20]  # Y-

    return Shape(vertices, indices, image_filename)


def createTextureNormalsQuad(image_filename, nx=1, ny=1):
    # Defining locations,texture coordinates and normals for each vertex of the shape
    vertices = [
        #   positions        texture        normals
        -0.5, -0.5, 0, 0, ny, 0, 0, 1,
        0.5, -0.5, 0, nx, ny, 0, 0, 1,
        0.5, 0.5, 0, nx, 0, 0, 0, 1,
        -0.5, 0.5, 0, 0, 0, 0, 0, 1, ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified

    indices = [
        0, 1, 2,
        2, 3, 0]

    return Shape(vertices, indices, image_filename)


def readFaceVertex(faceDescription):
    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]
    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex


def readOBJ(filename, color, status=True):
    vertices = []
    normals = []
    textCoords = []
    faces = []

    with open(filename, 'r') as file:
        count = 0
        for line in file.readlines():
            count += 1
            aux = line.strip().split(' ')
            if aux[0] == 'v':
                if status:
                    vertices += [[float(coord) for coord in aux[2:]]]
                else:
                    vertices += [[float(coord) for coord in aux[1:]]]
            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                if status:
                    textCoords += [[float(coord) for coord in aux[1:3]]]
                else:
                    assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                    textCoords += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'f':
                N = len(aux)
                faces += [[readFaceVertex(faceVertex) for faceVertex in aux[1:4]]]
                for i in range(3, N - 1):
                    faces += [[readFaceVertex(faceVertex) for faceVertex in [aux[i], aux[i + 1], aux[1]]]]

        vertexData = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0, 3):
                vertex = vertices[face[i][0] - 1]
                normal = normals[face[i][2] - 1]

                vertexData += [
                    vertex[0], vertex[1], vertex[2],
                    color[0], color[1], color[2],
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3

        return Shape(vertexData, indices)
