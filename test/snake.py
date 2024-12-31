import turtle

# Crear la ventana
window = turtle.Screen()
window.title("Snake")
window.bgcolor("white")

# Definir el cuerpo del snake
snake_body = []

# Definir la posición inicial del cuerpo del snake
snake_position = [10, 10]

# Definir las direcciones para mover el snake
directions = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

# Función para mover el cuerpo del snake
def move_snake():
    for position in snake_body[:-1]:
        x = position[0]
        y = position[1]
        turtle.goto(x + directions[direction][0], y + directions[direction][1])

# Main loop para mantener el juego
while True:
    # Obtener la dirección del usuario
    direction = input("Enter your direction (UP, DOWN, LEFT, RIGHT): ")
    
    if direction == "UP":
        directions["UP"] = (0, -1)
    elif direction == "DOWN":
        directions["DOWN"] = (0, 1)
    elif direction == "LEFT":
        directions["LEFT"] = (-1, 0)
    elif direction == "RIGHT":
        directions["RIGHT"] = (1, 0)

    # Actualizar el cuerpo del snake
    move_snake()
    
    # Incrementar el número de cuadros en el cuerpo si se toca la pared
    if len(snake_body) >= 4 and snake_position == snake_body[3]:
        break
    
    # Aumentar la velocidad del cuerpo al presionar 'w' o 's'
    if keyboard.is_pressed('w'):
        directions["UP"] = (0, -1)
    elif keyboard.is_pressed('s'):
        directions["DOWN"] = (0, 1)
    elif keyboard.is_pressed('a'):
        directions["LEFT"] = (-1, 0)
    elif keyboard.is_pressed('d'):
        directions["RIGHT"] = (1, 0)

# Limpiar la ventana
turtle.done()
