import pgzrun
import random

# --- Configuración del Juego ---
WIDTH = 800  # Ancho de la ventana
HEIGHT = 600 # Alto de la ventana
TITLE = "Marcianitos" # Título de la ventana

# Colores (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# --- Configuración de Estrellas ---
NUM_STARS = 100 # Cuántas estrellas quieres en pantalla
STAR_SPEED = 1 # Velocidad a la que se mueven las estrellas
STAR_COLOR = (150, 150, 150) # Un gris claro para las estrellas
STAR_MIN_RADIUS = 1 # Radio mínimo de las estrellas
STAR_MAX_RADIUS = 3 # Radio máximo de las estrellas

stars = [] # Lista para almacenar las estrellas

# --- Variables del Juego ---
player = Actor('player') # La nave del jugador (necesita player.png en la carpeta images)
player.midbottom = (WIDTH / 2, HEIGHT - 20) # Posición inicial

bullets = [] # Lista para almacenar los proyectiles
enemies = [] # Lista para almacenar los enemigos

score = 0
lives = 3
game_over = False

# Temporizadores y velocidades
BULLET_SPEED = -10 # Negativo para que suban
ENEMY_SPEED = 2
ENEMY_SIDE_SPEED = 1.5 # Velocidad lateral de los enemigos
PLAYER_SPEED = 5 # Velocidad de movimiento del jugador
ENEMY_SPAWN_DELAY = 60 # Cada cuántos frames aparece un enemigo (60 frames = 1 segundo)
enemy_spawn_timer = ENEMY_SPAWN_DELAY

# --- Funciones de Ayuda ---
def init_stars():
    """Inicializa la lista de estrellas con posiciones y tamaños aleatorios."""
    stars.clear() # Limpiar estrellas existentes si se llama de nuevo
    for _ in range(NUM_STARS):
        stars.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'radius': random.randint(STAR_MIN_RADIUS, STAR_MAX_RADIUS)
        })

# Llama a esta función una vez al inicio del script para generar las estrellas iniciales
init_stars()

# --- Funciones del Juego ---

def draw():
    """Dibuja todos los elementos en la pantalla."""
    screen.fill(BLACK) # Fondo negro

    # --- Dibujar Estrellas ---
    for star in stars:
        screen.draw.filled_circle((star['x'], star['y']), star['radius'], STAR_COLOR)

    # Dibujar jugador
    player.draw()

    # Dibujar proyectiles
    for bullet in bullets:
        bullet.draw()

    # Dibujar enemigos
    for enemy in enemies:
        enemy.draw()

    # Dibujar puntuación y vidas
    screen.draw.text(f"Score: {score}", (10, 10), color=WHITE, fontsize=30)
    screen.draw.text(f"Vidas: {lives}", (WIDTH - 100, 10), color=WHITE, fontsize=30)

    # Mensaje de Game Over
    if game_over:
        screen.draw.text("¡GAME OVER!", (WIDTH / 2 - 150, HEIGHT / 2 - 30), color=RED, fontsize=60)
        screen.draw.text("Presiona R para Reiniciar", (WIDTH / 2 - 180, HEIGHT / 2 + 30), color=WHITE, fontsize=40)

def update():
    """Actualiza la lógica del juego en cada frame."""
    global score, lives, game_over, enemy_spawn_timer

    if game_over:
        return # No actualiza nada si el juego ha terminado

    # --- Mover y Reciclar Estrellas ---
    for star in stars:
        star['y'] += STAR_SPEED
        # Si la estrella sale por abajo, la movemos a la parte superior
        if star['y'] > HEIGHT:
            star['y'] = 0 # La ponemos en la parte superior
            star['x'] = random.randint(0, WIDTH) # Nueva posición X aleatoria
            star['radius'] = random.randint(STAR_MIN_RADIUS, STAR_MAX_RADIUS) # Nuevo tamaño aleatorio


    # --- Movimiento del Jugador ---
    if keyboard.left:
        player.x -= PLAYER_SPEED
    if keyboard.right:
        player.x += PLAYER_SPEED

    # Limitar el movimiento del jugador dentro de la pantalla
    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH

    # --- Movimiento de Proyectiles ---
    for bullet in bullets:
        bullet.y += BULLET_SPEED
        # Eliminar proyectiles que salen de la pantalla
        if bullet.bottom < 0:
            bullets.remove(bullet)

    # --- Generación de Enemigos ---
    enemy_spawn_timer -= 1
    if enemy_spawn_timer <= 0:
        enemy_spawn_timer = ENEMY_SPAWN_DELAY # Reiniciar el temporizador
        spawn_enemy() # Llamar a la función para crear un nuevo enemigo

    # --- Movimiento de Enemigos ---
    for enemy in enemies:
        enemy.y += ENEMY_SPEED
        enemy.x += enemy.vx # Mover horizontalmente
        
        # Rebotar en los bordes de la pantalla
        if enemy.left < 0 or enemy.right > WIDTH:
            enemy.vx *= -1 # Invertir la dirección horizontal

        # Eliminar enemigos que salen de la pantalla (y quitar una vida)
        if enemy.top > HEIGHT:
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                game_over = True
            # Es importante usar 'break' o una copia de la lista si modificas la lista mientras iteras
            # Para este caso simple, con un solo 'remove' por iteración, 'break' es suficiente
            break 

    # --- Detección de Colisiones ---
    # Proyectil vs Enemigo
    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy):
                # sounds.explosion.play() # Reproducir sonido de explosión
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10 # Sumar puntos
                break # Salir del bucle interno para evitar errores con el mismo proyectil

    # Jugador vs Enemigo
    for enemy in enemies:
        if player.colliderect(enemy):
            # sounds.explosion.play() # Reproducir sonido de explosión
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                game_over = True
            break

def on_key_down(key):
    """Maneja los eventos de pulsación de tecla."""
    global game_over

    # Disparar proyectil al presionar espacio
    if key == keys.SPACE and not game_over:
        shoot_bullet()

    # Reiniciar el juego si está en Game Over y presiona R
    if key == keys.R and game_over:
        reset_game()

def shoot_bullet():
    """Crea un nuevo proyectil y lo añade a la lista."""
    # 'bullet' es el nombre de la imagen que Pygame Zero buscará en la carpeta images
    bullet = Actor('bullet')
    bullet.midtop = player.midtop # Posicionar el proyectil en la parte superior de la nave del jugador
    bullets.append(bullet)
    # sounds.shoot.play() # Reproducir sonido de disparo

def spawn_enemy():
    """Crea un nuevo enemigo en una posición aleatoria en la parte superior."""
    enemy = Actor('enemy') # 'enemy' es el nombre de la imagen
    enemy.x = random.randint(enemy.width, WIDTH - enemy.width) # Posición X aleatoria
    enemy.y = -enemy.height # Aparece justo por encima de la pantalla
    
    # Asignar una velocidad horizontal aleatoria al enemigo
    # Empieza moviéndose a la izquierda o a la derecha
    enemy.vx = random.choice([-1, 1]) * ENEMY_SIDE_SPEED 
    
    enemies.append(enemy)

def reset_game():
    """Reinicia todas las variables del juego a su estado inicial."""
    global score, lives, game_over, enemy_spawn_timer
    score = 0
    lives = 3
    game_over = False
    bullets.clear() # Vaciar listas
    enemies.clear()
    enemy_spawn_timer = ENEMY_SPAWN_DELAY # Reiniciar temporizador de enemigos
    player.midbottom = (WIDTH / 2, HEIGHT - 20) # Posición inicial del jugador
    init_stars() # Reiniciar las estrellas también

# --- Iniciar el juego ---
pgzrun.go()