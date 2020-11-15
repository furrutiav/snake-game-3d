# snake-game-3d
Proyecto personal, utilizando OpenGL para python 3, de la implementación del juego clásico [Snake en 2D](https://en.wikipedia.org/wiki/Snake_(video_game_genre)) pero con gráficos 3D. Para esto fue necesario la manipulación de shaders, texturas 2D, importación de modelos .obj, diseño y configuración de cámaras (vistas perspectiva y ortográfica), controlador para interacción con el usuario y mucho código.

## ¿Cómo jugar?
### Pre-requisitos
Para jugar es necesario pre-instalar las siguientes librerias para python: [glfw](https://pypi.org/project/glfw/), [pyopengl](https://pypi.org/project/PyOpenGL/), [numpy](https://pypi.org/project/numpy/) y [pillow](https://pypi.org/project/Pillow/)
```bash
glfw      # librería OpenGL
pyopengl  # OpenGL para python
numpy     # operación con vectores y matrices
pillow    # procesamiento de imágenes
```
### Inicio
Ahora bien, para jugar basta inicializar con python el código view.py. Por defecto el juego inicia en formato ventana (emergente), en caso de jugar en Fullscreen en necesario entregar como parámetro un 1 en la inicialización, esto es:
```bash
python view.py   # (default) ventana
python view.py 1 # fullscreen
python view.py 0 # ventana
```
### Controles
El modelo de jugabilidad se simplifica en el libre movimiento sobre una grilla (cuadrada y acotada) con transiciones continuas.

Para moverse es necesario definir una rapidez y dirección. Primero, con el scroll del mouse puede setear un rapidez a gusto antes y durante la partida. Luego, con las flechas del teclado, o bien teclas WASD (recomendado) puede definir una dirección en el instante actual.

_Observación: Se recomienda utilizar una rapidez apropiada para un movimiento suave de la cámara cada vez que se realiza un giro._

### Vistas
Existen tres estados de vista. El primero, y por defecto, 3era persona el cual se puede setear con la tecla R del teclado. El segundo, es la vista en perspectiva frontal o 2.5D, activo con tecla T. Y el tercero, es la vista aérea o top-down, activo con tecla E. Esto es:
```bash
3era persona  # R
Perspectiva   # T
Aerea         # E
```
_Observación: Todos y cada uno de los estados pueden ser elegidos durante la partida a gusto del usuario._

## Lógica y dinámica
En el juego original, la serpiente se mueve constantemente sobre el mapa siempre que no choque con el borde del mapa, o bien con su cola. Al inicio, la serpiente posee una cola de largo nulo y para crecer en una unidad de largo basta que la cabeza colisione con un elemento de comida, en caso de que exista espacio disponible en el mapa se genera un nuevo elemento de comida en dicho espacio. Para ganar, es necesario ocupar todo el espacio del mapa con la serpiente, o de manera equivalente crecer hasta cierto largo máximo.

La lógica se simplifica con la interacción de la cabeza, comida,  el espacio que ocupa la cola, borde y otros elementos de colisión, como componentes de una matriz cuadrada de misma dimensión de la grilla para cada instante de tiempo.

La dinámica del juego en 3D viene dada por como se ve la lógica en cada fotograma. Para un movimiento continuo de la serpiente se consideran las configuraciones (posición-direccion) actuales y posteriores de la serpiente para cada instante de tiempo, donde un "paso" (secuencia de tiempo actual al siguiente) se discretiza por una cantidad suficientemente grande de fotogramas para observar un movimiento fluido. Para dibujar cada fotograma se realiza una interpolación entre posiciones; y de la misma forma con direcciones (ángulos de rotación).

## Diseño
Para el diseño de imágenes 2D como el pop-up de inicio, pausa, muerte y ganar, texturas de suelo y borde, fueron creadas en el software [Photoshop](https://www.adobe.com/products/photoshop.html) en versión de prueba.

Los modelos 3D como el arco del triunfo, ampolleta y faroles fueron cargados de la pagina de modelos 3D gratuitos [TurboSquid](https://www.turbosquid.com/). Y para el diseño de la serpiente (cabeza y cola) fueron creados con el software [SketchUp](https://www.sketchup.com/) en versión de prueba.

## Próximas versiones

* Overlay con contador
* Sonidos
* Gestor de partidas
* Escenarios

## Anexos
```bash
Material Semestre Pasado/Códigos Otoño 2020.zip
Códigos/code: CC 3501-1 - Primavera 2020
No propietario / Librerías, Implementaciones, Base y Ejemplos, etc. Owner: Daniel Calderon, CC 3501, 2019-2
```
## Licencia
Este proyecto está bajo la Licencia (GNU General Public License v3.0 License) - mira el archivo [GNU v3](https://www.gnu.org/licenses/gpl-3.0.html) para detalles.
