# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
Lighting Shaders

v2 - Bug fixed: Textures were not binded

F. Urrutia V.
update Lighting Shaders

v2.2: More light with PhongShader; color and texture
"""

from OpenGL.GL import *
import OpenGL.GL.shaders
from libs.easy_shaders import GPUShape


class SimpleFlatShaderProgram():

    def __init__(self):
        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;
            in vec3 normal;

            flat out vec4 vertexColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition;
            uniform vec3 viewPosition;
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);
                vec3 toLight = lightPosition - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                
                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * color;
                vertexColor = vec4(result, 1.0);
            }
            """

        fragment_shader = """
            #version 130

            flat in vec4 vertexColor;
            out vec4 fragColor;

            void main()
            {
                fragColor = vertexColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimpleTextureFlatShaderProgram():

    def __init__(self):
        vertex_shader = """
            #version 130

            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec2 fragTexCoords;
            flat out vec3 vertexLightColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition; 
            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                fragTexCoords = texCoords;

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);
                vec3 toLight = lightPosition - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                
                vertexLightColor = ambient + ((diffuse + specular) / attenuation);
            }
            """

        fragment_shader = """
            #version 130

            flat in vec3 vertexLightColor;
            in vec2 fragTexCoords;

            out vec4 fragColor;

            uniform sampler2D samplerTex;

            void main()
            {
                vec4 textureColor = texture(samplerTex, fragTexCoords);
                fragColor = vec4(vertexLightColor, 1.0) * textureColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_2D, shape.texture)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimpleGouraudShaderProgram():

    def __init__(self):
        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;
            in vec3 normal;

            out vec4 vertexColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition;
            uniform vec3 viewPosition;
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);
                vec3 toLight = lightPosition - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                
                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * color;
                vertexColor = vec4(result, 1.0);
            }
            """

        fragment_shader = """
            #version 130

            in vec4 vertexColor;
            out vec4 fragColor;

            void main()
            {
                fragColor = vertexColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimpleTextureGouraudShaderProgram():

    def __init__(self):
        vertex_shader = """
            #version 130

            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec2 fragTexCoords;
            out vec3 vertexLightColor;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            uniform vec3 lightPosition; 
            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;
            
            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);

                fragTexCoords = texCoords;

                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse 
                vec3 norm = normalize(normal);
                vec3 toLight = lightPosition - vertexPos;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - vertexPos);
                vec3 reflectDir = reflect(-lightDir, norm);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                
                vertexLightColor = ambient + ((diffuse + specular) / attenuation);
            }
            """

        fragment_shader = """
            #version 130

            in vec3 vertexLightColor;
            in vec2 fragTexCoords;

            out vec4 fragColor;

            uniform sampler2D samplerTex;

            void main()
            {
                vec4 textureColor = texture(samplerTex, fragTexCoords);
                fragColor = vec4(vertexLightColor, 1.0) * textureColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_2D, shape.texture)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimplePhongShaderProgram:

    def __init__(self):
        vertex_shader = """
            #version 330 core

            layout (location = 0) in vec3 position;
            layout (location = 1) in vec3 color;
            layout (location = 2) in vec3 normal;

            out vec3 fragPosition;
            out vec3 fragOriginalColor;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragOriginalColor = color;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330 core

            out vec4 fragColor;

            in vec3 fragNormal;
            in vec3 fragPosition;
            in vec3 fragOriginalColor;
            
            uniform vec3 lightPosition; 
            uniform vec3 viewPosition;
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            void main()
            {
                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse
                // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
                vec3 normalizedNormal = normalize(fragNormal);
                vec3 toLight = lightPosition - fragPosition;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(normalizedNormal, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - fragPosition);
                vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                    
                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * fragOriginalColor;
                fragColor = vec4(result, 1.0);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimpleTexturePhongShaderProgram:

    def __init__(self):
        vertex_shader = """
            #version 330 core
            
            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec3 fragPosition;
            out vec2 fragTexCoords;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragTexCoords = texCoords;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330 core

            in vec3 fragNormal;
            in vec3 fragPosition;
            in vec2 fragTexCoords;

            out vec4 fragColor;
            
            uniform vec3 lightPosition; 
            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            uniform sampler2D samplerTex;

            void main()
            {
                // ambient
                vec3 ambient = Ka * La;
                
                // diffuse
                // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
                vec3 normalizedNormal = normalize(fragNormal);
                vec3 toLight = lightPosition - fragPosition;
                vec3 lightDir = normalize(toLight);
                float diff = max(dot(normalizedNormal, lightDir), 0.0);
                vec3 diffuse = Kd * Ld * diff;
                
                // specular
                vec3 viewDir = normalize(viewPosition - fragPosition);
                vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                vec3 specular = Ks * Ls * spec;

                // attenuation
                float distToLight = length(toLight);
                float attenuation = constantAttenuation
                    + linearAttenuation * distToLight
                    + quadraticAttenuation * distToLight * distToLight;
                    
                vec4 fragOriginalColor = texture(samplerTex, fragTexCoords);

                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * fragOriginalColor.rgb;
                fragColor = vec4(result, 1.0);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_2D, shape.texture)

        # 3d vertices + 2d texture coordinates + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


# SOLUTION
class SimpleTexturePhongShaderProgramMulti:

    def __init__(self, num):
        vertex_shader = """
            #version 330 core

            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec3 fragPosition;
            out vec2 fragTexCoords;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragTexCoords = texCoords;
                fragNormal = mat3(transpose(inverse(model))) * normal;  

                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = dual_multi_fragment_shader_code(num, 'tx')

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_2D, shape.texture)

        # 3d vertices + 2d texture coordinates + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimplePhongShaderProgramMulti:

    def __init__(self, num):
        vertex_shader = """
            #version 330 core

            layout (location = 0) in vec3 position;
            layout (location = 1) in vec3 color;
            layout (location = 2) in vec3 normal;

            out vec3 fragPosition;
            out vec3 fragOriginalColor;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragOriginalColor = color;
                fragNormal = mat3(transpose(inverse(model))) * normal;  

                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = dual_multi_fragment_shader_code(num, 'col')

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode = GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


def dual_multi_fragment_shader_code(size, mod='col'):
    assert type(size) == int and size > 1, """ Error size: int and >1"""
    assert mod in ['col', 'tx'], """ Error mod: col or tx"""

    dict = {'col': ['in vec3 fragOriginalColor;', '', '' , ''],
            'tx': ['in vec2 fragTexCoords;', 'uniform sampler2D samplerTex;',
                   'vec4 fragOriginalColor = texture(samplerTex, fragTexCoords);', '.rgb']}

    code = """
        #version 330 core

        in vec3 fragNormal;
        in vec3 fragPosition;
        """ + dict[mod][0] + """

        out vec4 fragColor;

        uniform vec3 viewPosition;
    """
    for i in range(1, size + 1):
        code += f"""
        uniform vec3 lightPosition{i};
        uniform vec3 La{i};
        uniform vec3 Ld{i};
        uniform vec3 Ls{i};
        uniform vec3 Ka{i};
        uniform vec3 Kd{i};
        uniform vec3 Ks{i};
        uniform uint shininess{i};
        uniform float constantAttenuation{i};
        uniform float linearAttenuation{i};
        uniform float quadraticAttenuation{i};
        """
    code += """
        """ + dict[mod][1] + """

        void main()
        {
            // ambient
        """
    for i in range(1, size + 1):
        code += f"""
            vec3 ambient{i} = Ka{i} * La{i};
        """
    code += """
            // diffuse
            // fragment normal has been interpolated, so it does not necessarily have norm equal to 1
            vec3 normalizedNormal = normalize(fragNormal);
        """
    for i in range(1, size + 1):
        code += f"""
            vec3 toLight{i} = lightPosition{i} - fragPosition;
            vec3 lightDir{i} = normalize(toLight{i});
            float diff{i} = max(dot(normalizedNormal, lightDir{i}), 0.0);
            vec3 diffuse{i} = Kd{i} * Ld{i} * diff{i};
        """
    code += """
            // specular
            vec3 viewDir = normalize(viewPosition - fragPosition);
        """
    for i in range(1, size + 1):
        code += f"""
            vec3 reflectDir{i} = reflect(-lightDir{i}, normalizedNormal);  
            float spec{i} = pow(max(dot(viewDir, reflectDir{i}), 0.0), shininess{i});
            vec3 specular{i} = Ks{i} * Ls{i} * spec{i};
        """
    code += """
            // attenuation
        """
    for i in range(1, size + 1):
        code += f"""
            float distToLight{i} = length(toLight{i});
            float attenuation{i} = constantAttenuation{i}
                + linearAttenuation{i} * distToLight{i}
                + quadraticAttenuation{i} * distToLight{i} * distToLight{i};
            """
    line = ""
    for i in range(1, size + 1):
        line += f"(ambient{i} + ((diffuse{i} + specular{i}) / attenuation{i})) + "
    line = line[:-2]
    code += """
            """ + dict[mod][2] + """
            vec3 result = ( """ + line + """ ) * fragOriginalColor""" + dict[mod][3] + """;
            fragColor = vec4(result, 1.0);
        }
        """
    # print(code)
    return code


class SimpleGouraudShaderProgramMulti:

    def __init__(self, num):
        vertex_shader = dual_multi_vertex_shader_code(num, 'col')

        fragment_shader = """
            #version 130

            in vec4 vertexColor;
            out vec4 fragColor;

            void main()
            {
                fragColor = vertexColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode=GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 3*4 + 3*4 = 36 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


class SimpleTextureGouraudShaderProgramMulti():

    def __init__(self, num):
        vertex_shader = dual_multi_vertex_shader_code(num, 'tx')

        fragment_shader = """
            #version 330

            in vec3 vertexLightColor;
            in vec2 fragTexCoords;

            out vec4 fragColor;

            uniform sampler2D samplerTex;

            void main()
            {
                vec4 textureColor = texture(samplerTex, fragTexCoords);
                fragColor = vec4(vertexLightColor, 1.0) * textureColor;
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def drawShape(self, shape, mode=GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the proper buffers
        glBindVertexArray(shape.vao)
        glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)
        glBindTexture(GL_TEXTURE_2D, shape.texture)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Render the active element buffer with the active shader program
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)


def dual_multi_vertex_shader_code(size, mod='col'):
    assert type(size) == int and size > 1, """ Error size: int and >1"""
    assert mod in ['col', 'tx'], """ Error mod: col or tx"""

    dict = {'col': ['in vec3 color;', 'out vec4 vertexColor;', '', 'vec3 result', '* color',
                    'vertexColor = vec4(result, 1.0);'],
            'tx': ['in vec2 texCoords;', 'out vec2 fragTexCoords;', 'out vec3 vertexLightColor;', 'vertexLightColor',
                   '', '']}

    code = """
        #version 330 core
        
        in vec3 position;
        """ + dict[mod][0] + """
        in vec3 normal;

        """ + dict[mod][1] + """
        """ + dict[mod][2] + """
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        uniform vec3 viewPosition;
    """
    for i in range(1, size + 1):
        code += f"""
        uniform vec3 lightPosition{i};
        uniform vec3 La{i};
        uniform vec3 Ld{i};
        uniform vec3 Ls{i};
        uniform vec3 Ka{i};
        uniform vec3 Kd{i};
        uniform vec3 Ks{i};
        uniform uint shininess{i};
        uniform float constantAttenuation{i};
        uniform float linearAttenuation{i};
        uniform float quadraticAttenuation{i};
        """
    code += """
    
        void main()
        {
            vec3 vertexPos = vec3(model * vec4(position, 1.0));
            gl_Position = projection * view * vec4(vertexPos, 1.0);
            
            // ambient
        """
    for i in range(1, size + 1):
        code += f"""
            vec3 ambient{i} = Ka{i} * La{i};
        """
    code += """
            // diffuse
            vec3 norm = normalize(normal);
        """
    for i in range(1, size + 1):
        code += f"""
            vec3 toLight{i} = lightPosition{i} - vertexPos;
            vec3 lightDir{i} = normalize(toLight{i});
            float diff{i} = max(dot(norm, lightDir{i}), 0.0);
            vec3 diffuse{i} = Kd{i} * Ld{i} * diff{i};
        """
    code += """
            // specular
            vec3 viewDir = normalize(viewPosition - vertexPos);
        """
    for i in range(1, size + 1):
        code += f"""
            vec3 reflectDir{i} = reflect(-lightDir{i}, norm);  
            float spec{i} = pow(max(dot(viewDir, reflectDir{i}), 0.0), shininess{i});
            vec3 specular{i} = Ks{i} * Ls{i} * spec{i};
        """
    code += """
            // attenuation
        """
    for i in range(1, size + 1):
        code += f"""
            float distToLight{i} = length(toLight{i});
            float attenuation{i} = constantAttenuation{i}
                + linearAttenuation{i} * distToLight{i}
                + quadraticAttenuation{i} * distToLight{i} * distToLight{i};
            """
    line = ""
    for i in range(1, size + 1):
        line += f"(ambient{i} + ((diffuse{i} + specular{i}) / attenuation{i})) + "
    line = line[:-2]
    code += """
    
            """ + dict[mod][3] + """ = ( """ + line + """ ) """ + dict[mod][4] + """;
            """ + dict[mod][5] + """
        }
        """
    print(code)
    return code
