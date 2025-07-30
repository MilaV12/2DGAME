import pygame
import sys
import os
import json

pygame.init()
pygame.mixer.init()

ANCHO, ALTO = 960, 640
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Shadows of Skaldheim")

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS_OSCURO = (40, 40, 40)
GRIS_CLARO = (150, 150, 150)
AZUL = (50, 100, 200)

# Fuentes
fuente_titulo = pygame.font.SysFont("arialblack", 56)
fuente_botones = pygame.font.SysFont("verdana", 24, bold=True)
fuente_intro = pygame.font.SysFont("timesnewroman", 24, italic=True)
fuente_version = pygame.font.SysFont("consolas", 18, bold=True)
fuente_opcion = pygame.font.SysFont("verdana", 28, bold=True)

ASSETS = "assets"
FONDO_IMG = os.path.join(ASSETS, "FONDO_NEW.jpg")
MUSICA = os.path.join(ASSETS, "MUSICA-INICIO.ogg")
SONIDO_HOVER = os.path.join(ASSETS, "boton_hover.wav")
SONIDO_CLICK = os.path.join(ASSETS, "boton_click.wav")

ARCHIVO_CONFIG = "config.json"

fondo = pygame.image.load(FONDO_IMG).convert() if os.path.exists(FONDO_IMG) else None

try:
    pygame.mixer.music.load(MUSICA)
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
except:
    print("⚠️ No se pudo cargar la música de fondo.")

sonido_hover = pygame.mixer.Sound(SONIDO_HOVER) if os.path.exists(SONIDO_HOVER) else None
sonido_click = pygame.mixer.Sound(SONIDO_CLICK) if os.path.exists(SONIDO_CLICK) else None

# Estados del menú
MENU_PRINCIPAL = 0
SELECCION_MUNDO = 1
CREAR_PERSONAJE = 2
INTRODUCCION = 3
MULTIJUGADOR = 4
TUTORIAL = 5
LOGROS = 6
CREDITOS = 7
AJUSTES = 8


# Índice de opción seleccionada en el menú principal
opcion_menu_principal = 0
estado = MENU_PRINCIPAL

introduccion = [
    "En las tierras olvidadas de Skaldheim,",
    "la oscuridad despierta en antiguas ruinas.",
    "Un elegido deberá restaurar el equilibrio...",
    "",
    "Presiona ESC para volver o ENTER para continuar."
]

linea_actual = 0
ultimo_tiempo = pygame.time.get_ticks()
TIEMPO_ENTRE_LINEAS = 1500  # ms

# Variables de ajustes (valores por defecto)
volumen_musica = 0.5
volumen_efectos = 0.5
pantalla_completa = False
dificultad_niveles = ['Fácil', 'Normal', 'Difícil']
indice_dificultad = 1  # Normal

opcion_ajustes = 0

# Clase Boton
class Boton:
    def __init__(self, texto, x, y, ancho=180, alto=50):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.hover = False

    def dibujar(self, superficie):
        # Colores y gradiente
        color_base = (40, 60, 120)
        color_hover = (80, 140, 220)
        color_borde = (200, 220, 255)
        color_sombra = (0, 0, 0, 100)
        # Color especial para selección por teclado/mouse
        color_seleccion = (255, 211, 54)  # Amarillo dorado
        color_seleccion2 = (255, 245, 180)  # Más claro para gradiente

        if self.hover:
            # Si está seleccionado, usa un gradiente dorado y borde más grueso
            color1 = color_seleccion
            color2 = color_seleccion2
            borde_color = (255, 230, 100)
            borde_grosor = 5
        else:
            color1 = color_base
            color2 = color_hover
            borde_color = color_borde
            borde_grosor = 3

        # Sombra exterior
        sombra_rect = self.rect.inflate(10, 10)
        sombra_surf = pygame.Surface(sombra_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra_surf, color_sombra, sombra_surf.get_rect(), border_radius=18)
        superficie.blit(sombra_surf, (sombra_rect.x, sombra_rect.y))

        # Gradiente vertical
        grad = pygame.Surface(self.rect.size)
        for i in range(self.rect.height):
            ratio = i / self.rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            grad.fill((r, g, b), rect=pygame.Rect(0, i, self.rect.width, 1))
        grad.set_alpha(235)
        superficie.blit(grad, self.rect.topleft)

        # Borde exterior
        pygame.draw.rect(superficie, borde_color, self.rect, borde_grosor, border_radius=16)
        # Borde interior
        pygame.draw.rect(superficie, (255,255,255,40), self.rect.inflate(-6, -6), 0, border_radius=12)

        # Texto con sombra y color especial si está seleccionado
        if self.hover:
            texto_color = (60, 40, 0)
        else:
            texto_color = BLANCO
        texto_render = fuente_botones.render(self.texto, True, texto_color)
        sombra = fuente_botones.render(self.texto, True, (0, 0, 0, 180))
        sombra_pos = (self.rect.centerx + 2, self.rect.centery + 2)
        superficie.blit(sombra, sombra.get_rect(center=sombra_pos))
        superficie.blit(texto_render, texto_render.get_rect(center=self.rect.center))

    def verificar_hover(self, mouse_pos):
        estaba = self.hover
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.hover and not estaba and sonido_hover:
            sonido_hover.play()

    def clic(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if sonido_click:
                sonido_click.play()
            return True
        return False

# Botones menú principal
botones_texto = [
    "Un jugador",
    "Multijugador",
    "Tutorial",
    "Logros",
    "Créditos",
    "Ajustes"
]

botones_menu = []
espacio = 15
ancho_boton = 180
alto_boton = 50
total_altura = alto_boton * len(botones_texto) + espacio * (len(botones_texto) - 1)
inicio_y = ALTO - total_altura - 40

for i, texto in enumerate(botones_texto):
    x = (ANCHO - ancho_boton) // 2
    y = inicio_y + i * (alto_boton + espacio)
    botones_menu.append(Boton(texto, x, y, ancho_boton, alto_boton))

# Botones selección mundo
botones_mundos = []
mundos = ["Mundo 1: Skaldar", "Mundo 2: Yggdrasil", "Mundo 3: Helheim"]
inicio_y_mundos = (ALTO - (alto_boton * len(mundos) + espacio * (len(mundos) - 1))) // 2

for i, texto in enumerate(mundos):
    x = (ANCHO - ancho_boton) // 2
    y = inicio_y_mundos + i * (alto_boton + espacio)
    botones_mundos.append(Boton(texto, x, y, ancho_boton, alto_boton))

# Opciones para crear personaje (color simple)
colores_piel = [(255, 224, 189), (205, 133, 63), (139, 69, 19)]
colores_pelo = [(255, 255, 255), (255, 215, 0), (0, 0, 0)]
colores_ropa = [(70, 130, 180), (128, 0, 128), (139, 0, 0)]

indice_piel = 0
indice_pelo = 0
indice_ropa = 0

boton_adelante = Boton("Siguiente", ANCHO - 220, ALTO - 80, 180, 50)
boton_atras = Boton("Atrás", 40, ALTO - 80, 140, 50)

# Flechas para cambiar opciones
class Flecha:
    def __init__(self, x, y, direccion='izq'):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.direccion = direccion
        self.hover = False

    def dibujar(self, surf):
        color = (180, 180, 220) if self.hover else (140, 140, 180)
        puntos = []
        cx, cy = self.rect.center
        if self.direccion == 'izq':
            puntos = [(cx+10, cy-15), (cx-10, cy), (cx+10, cy+15)]
        else:
            puntos = [(cx-10, cy-15), (cx+10, cy), (cx-10, cy+15)]

        pygame.draw.polygon(surf, color, puntos)

    def verificar_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def clic(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

flechas_piel = [Flecha(ANCHO//4 - 60, ALTO//2 + 170, 'izq'), Flecha(ANCHO//4 + 20, ALTO//2 + 170, 'der')]
flechas_pelo = [Flecha(ANCHO//2 - 60, ALTO//2 + 170, 'izq'), Flecha(ANCHO//2 + 20, ALTO//2 + 170, 'der')]
flechas_ropa = [Flecha(3*ANCHO//4 - 60, ALTO//2 + 170, 'izq'), Flecha(3*ANCHO//4 + 20, ALTO//2 + 170, 'der')]

def dibujar_texto(texto, fuente, color, superficie, x, y):
    render = fuente.render(texto, True, color)
    superficie.blit(render, (x, y))

def cargar_config():
    global volumen_musica, volumen_efectos, pantalla_completa, indice_dificultad
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, 'r') as f:
                config = json.load(f)
            volumen_musica = config.get('volumen_musica', 0.5)
            volumen_efectos = config.get('volumen_efectos', 0.5)
            pantalla_completa = config.get('pantalla_completa', False)
            indice_dificultad = config.get('indice_dificultad', 1)
        except Exception as e:
            print("Error cargando configuración:", e)

def guardar_config():
    config = {
        'volumen_musica': volumen_musica,
        'volumen_efectos': volumen_efectos,
        'pantalla_completa': pantalla_completa,
        'indice_dificultad': indice_dificultad
    }
    try:
        with open(ARCHIVO_CONFIG, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print("Error guardando configuración:", e)

def aplicar_volumen():
    pygame.mixer.music.set_volume(volumen_musica)
    # Si tienes efectos globales, ajustar volumen aquí

def cambiar_pantalla_completa():
    global pantalla_completa, pantalla
    pantalla_completa = not pantalla_completa
    if pantalla_completa:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))

def ajustes():
    global opcion_ajustes, volumen_musica, volumen_efectos, pantalla_completa, indice_dificultad
    opciones_ajustes = [
        f"Volumen Música: {int(volumen_musica * 100)}%",
        f"Volumen Efectos: {int(volumen_efectos * 100)}%",
        f"Pantalla Completa: {'Sí' if pantalla_completa else 'No'}",
        f"Dificultad: {dificultad_niveles[indice_dificultad]}",
        "Volver"
    ]

    run = True
    mouse_pos = (0, 0)
    while run:
        # Fondo degradado
        grad = pygame.Surface((ANCHO, ALTO))
        for y in range(ALTO):
            ratio = y / ALTO
            r = int(40 * (1 - ratio) + 80 * ratio)
            g = int(60 * (1 - ratio) + 120 * ratio)
            b = int(120 * (1 - ratio) + 220 * ratio)
            grad.fill((r, g, b), rect=pygame.Rect(0, y, ANCHO, 1))
        grad.set_alpha(220)
        pantalla.blit(grad, (0, 0))

        # Caja central más elegante, amplia y con mejor contraste
        caja_ancho = 700  # Mucho más ancho
        caja_alto = 500   # Más alto para dar aire
        caja_x = (ANCHO - caja_ancho) // 2
        caja_y = (ALTO - caja_alto) // 2 + 10
        sombra_rect = pygame.Rect(caja_x-16, caja_y+16, caja_ancho+32, caja_alto+32)
        sombra_surf = pygame.Surface((caja_ancho+32, caja_alto+32), pygame.SRCALPHA)
        pygame.draw.rect(sombra_surf, (0,0,0,110), sombra_surf.get_rect(), border_radius=36)
        pantalla.blit(sombra_surf, (caja_x-16, caja_y+16))
        caja_surf = pygame.Surface((caja_ancho, caja_alto), pygame.SRCALPHA)
        pygame.draw.rect(caja_surf, (38, 48, 80, 235), caja_surf.get_rect(), border_radius=26)
        pygame.draw.rect(caja_surf, (255,255,255,60), caja_surf.get_rect(), 0, border_radius=26)
        pygame.draw.rect(caja_surf, (200,220,255,120), caja_surf.get_rect(), 4, border_radius=26)
        pantalla.blit(caja_surf, (caja_x, caja_y))

        # Título con sombra, bien separado y siempre visible
        titulo = "Ajustes"
        fuente_titulo_ajustes = pygame.font.SysFont("arialblack", 48, bold=True)
        sombra = fuente_titulo_ajustes.render(titulo, True, (0,0,0))
        pantalla.blit(sombra, (ANCHO//2 - sombra.get_width()//2 + 3, caja_y - 54))
        render_titulo = fuente_titulo_ajustes.render(titulo, True, (255,255,255))
        pantalla.blit(render_titulo, (ANCHO//2 - render_titulo.get_width()//2, caja_y - 58))

        # Actualiza opciones dinámicamente
        opciones_ajustes[0] = f"Volumen Música: {int(volumen_musica * 100)}%"
        opciones_ajustes[1] = f"Volumen Efectos: {int(volumen_efectos * 100)}%"
        opciones_ajustes[2] = f"Pantalla Completa: {'Sí' if pantalla_completa else 'No'}"
        opciones_ajustes[3] = f"Dificultad: {dificultad_niveles[indice_dificultad]}"

        # Opciones como "botones" bien centrados y organizados
        fuente_opc = pygame.font.SysFont("arialblack", 27, bold=True)  # Mantener tamaño original
        alto_opc = 56  # Mantener tamaño original
        espacio = 36   # Más espacio entre opciones, pero sin agrandar los controles
        margen_lateral = 44
        ancho_opc = caja_ancho - 2 * margen_lateral
        total_altura = alto_opc * len(opciones_ajustes) + espacio * (len(opciones_ajustes) - 1)
        # Espacio extra arriba para separar del título
        inicio_y = caja_y + 38

        # Detectar mouse
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        # Dibuja cada opción como botón visual, con barra y flechas para volumen/dificultad
        rects_opciones = []

        for i, opcion in enumerate(opciones_ajustes):
            rect = pygame.Rect(caja_x + margen_lateral, inicio_y + i * (alto_opc + espacio), ancho_opc, alto_opc)
            rects_opciones.append(rect)
            hover = rect.collidepoint(mouse_pos)
            color_base = (44, 60, 110)
            color_hover = (80, 140, 220)
            color_seleccion = (255, 211, 54)
            color_seleccion2 = (255, 245, 180)
            if i == opcion_ajustes or hover:
                color1 = color_seleccion
                color2 = color_seleccion2
                borde_color = (255, 230, 100)
                borde_grosor = 4
                texto_color = (60, 40, 0)
            else:
                color1 = color_base
                color2 = color_hover
                borde_color = (200,220,255)
                borde_grosor = 2
                texto_color = (255,255,255)
            # Fondo gradiente
            grad = pygame.Surface((rect.width, rect.height))
            for y2 in range(rect.height):
                ratio = y2 / rect.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                grad.fill((r, g, b), rect=pygame.Rect(0, y2, rect.width, 1))
            grad.set_alpha(220)
            pantalla.blit(grad, rect.topleft)
            # Bordes
            pygame.draw.rect(pantalla, borde_color, rect, borde_grosor, border_radius=12)
            # Sombra sutil inferior
            sombra_surf = pygame.Surface((rect.width, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra_surf, (0,0,0,40), sombra_surf.get_rect())
            pantalla.blit(sombra_surf, (rect.x, rect.bottom-5))

            visual_centro_y = rect.centery
            # --- Layout: texto a la izquierda, controles a la derecha ---
            # Texto de la opción (alineado a la izquierda)
            texto_opcion = opcion.split(':')[0] + (':' if ':' in opcion else '')
            render = fuente_opc.render(texto_opcion, True, texto_color)
            sombra = fuente_opc.render(texto_opcion, True, (0,0,0,120))
            text_rect = render.get_rect()
            # Más espacio a la derecha del texto
            text_rect.midleft = (rect.left + 38, rect.centery)
            pantalla.blit(sombra, text_rect.move(2,2))
            pantalla.blit(render, text_rect)

            # Controles a la derecha
            if i == 0 or i == 1:
                # Volumen Música/Efectos
                # Layout: [Texto]---[Flecha izq]  [Barra]  [Flecha der]  [Porcentaje]
                barra_ancho = 140
                barra_alto = 16
                espacio_total_controles = 340  # Espacio reservado a la derecha para controles
                padding_texto_controles = 60   # Más espacio entre texto y controles
                padding_flecha_barra = 32      # Más espacio entre flecha y barra
                padding_barra_flecha = 32      # Más espacio entre barra y flecha der
                padding_barra_pct = 36         # Más espacio entre flecha der y porcentaje

                # Posición base de controles (alineados a la derecha de la caja)
                controles_x = rect.right - espacio_total_controles + 10
                cy = rect.centery

                # Flecha izquierda
                flecha_izq_cx = controles_x + 20
                flecha_color = (255, 211, 54) if i == 0 else (44, 202, 255)
                if i == opcion_ajustes or hover:
                    flecha_color = (255, 211, 54) if i == 0 else (44, 202, 255)
                else:
                    flecha_color = (180, 180, 220)
                puntos_izq = [
                    (flecha_izq_cx-12, cy),
                    (flecha_izq_cx+8, cy-13),
                    (flecha_izq_cx+8, cy+13)
                ]
                pygame.draw.polygon(pantalla, flecha_color, puntos_izq)

                # Barra de volumen
                barra_x = flecha_izq_cx + 18 + padding_flecha_barra
                barra_y = cy - barra_alto//2
                pygame.draw.rect(pantalla, (60,60,80), (barra_x, barra_y, barra_ancho, barra_alto), border_radius=7)
                valor = volumen_musica if i == 0 else volumen_efectos
                color_barra = (255, 211, 54) if i == 0 else (44, 202, 255)
                color_borde = (200,200,120) if i == 0 else (120,200,255)
                fill = int(barra_ancho * valor)
                pygame.draw.rect(pantalla, color_barra, (barra_x, barra_y, fill, barra_alto), border_radius=7)
                pygame.draw.rect(pantalla, color_borde, (barra_x, barra_y, barra_ancho, barra_alto), 2, border_radius=7)

                # Flecha derecha
                flecha_der_cx = barra_x + barra_ancho + padding_barra_flecha
                puntos_der = [
                    (flecha_der_cx+12, cy),
                    (flecha_der_cx-8, cy-13),
                    (flecha_der_cx-8, cy+13)
                ]
                pygame.draw.polygon(pantalla, flecha_color, puntos_der)

                # Porcentaje
                fuente_pct = pygame.font.SysFont("arialblack", 24, bold=True)
                pct_txt = f"{int(valor*100)}%"
                pct_render = fuente_pct.render(pct_txt, True, texto_color)
                pct_rect = pct_render.get_rect(midleft=(flecha_der_cx + padding_barra_pct, cy))
                pantalla.blit(pct_render, pct_rect)

            elif i == 2:
                # Pantalla Completa: texto a la derecha, más separado pero sin agrandar
                estado_txt = opcion.split(':')[1].strip() if ':' in opcion else ''
                fuente_estado = pygame.font.SysFont("arialblack", 22, bold=True)
                color_estado = (44, 202, 255) if (i == opcion_ajustes or hover) else (200,220,255)
                render_estado = fuente_estado.render(estado_txt, True, color_estado)
                estado_rect = render_estado.get_rect(midleft=(rect.right - 80, visual_centro_y))
                pantalla.blit(render_estado, estado_rect)

            elif i == 3:
                # Dificultad
                flecha_color = (255, 211, 54) if (i == opcion_ajustes or hover) else (180, 180, 220)
                flecha_cx = rect.right - 120
                cy = rect.centery
                puntos_izq = [(flecha_cx-18, cy), (flecha_cx+2, cy-13), (flecha_cx+2, cy+13)]
                pygame.draw.polygon(pantalla, flecha_color, puntos_izq)
                flecha_cx2 = rect.right - 38
                puntos_der = [(flecha_cx2+18, cy), (flecha_cx2-2, cy-13), (flecha_cx2-2, cy+13)]
                pygame.draw.polygon(pantalla, flecha_color, puntos_der)
                dif_text = dificultad_niveles[indice_dificultad]
                fuente_dif = pygame.font.SysFont("arialblack", 22, bold=True)
                color_dif = (255, 211, 54) if (i == opcion_ajustes or hover) else (255,255,255)
                render_dif = fuente_dif.render(dif_text, True, color_dif)
                pantalla.blit(render_dif, (rect.right - 68 - render_dif.get_width()//2, cy - render_dif.get_height()//2))

        # Pie de página
        fuente_pie = pygame.font.SysFont("verdana", 18, italic=True)
        pie = fuente_pie.render("Usa ↑ ↓, ENTER o haz clic para seleccionar. ESC para salir", True, (230,230,255))
        sombra_pie = fuente_pie.render("Usa ↑ ↓, ENTER o haz clic para seleccionar. ESC para salir", True, (0,0,0))
        pantalla.blit(sombra_pie, (ANCHO//2 - pie.get_width()//2 + 2, caja_y + caja_alto + 14))
        pantalla.blit(pie, (ANCHO//2 - pie.get_width()//2, caja_y + caja_alto + 12))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                guardar_config()
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcion_ajustes = (opcion_ajustes - 1) % len(opciones_ajustes)
                elif evento.key == pygame.K_DOWN:
                    opcion_ajustes = (opcion_ajustes + 1) % len(opciones_ajustes)
                elif evento.key == pygame.K_LEFT:
                    if opcion_ajustes == 0:
                        volumen_musica = max(0.0, volumen_musica - 0.05)
                        aplicar_volumen()
                    elif opcion_ajustes == 1:
                        volumen_efectos = max(0.0, volumen_efectos - 0.05)
                    elif opcion_ajustes == 3:
                        indice_dificultad = (indice_dificultad - 1) % len(dificultad_niveles)
                elif evento.key == pygame.K_RIGHT:
                    if opcion_ajustes == 0:
                        volumen_musica = min(1.0, volumen_musica + 0.05)
                        aplicar_volumen()
                    elif opcion_ajustes == 1:
                        volumen_efectos = min(1.0, volumen_efectos + 0.05)
                    elif opcion_ajustes == 3:
                        indice_dificultad = (indice_dificultad + 1) % len(dificultad_niveles)
                elif evento.key == pygame.K_RETURN:
                    if opciones_ajustes[opcion_ajustes] == "Volver":
                        guardar_config()
                        run = False
                    elif opcion_ajustes == 2:  # Pantalla completa
                        cambiar_pantalla_completa()
                elif evento.key == pygame.K_ESCAPE:
                    guardar_config()
                    run = False
            elif evento.type == pygame.MOUSEMOTION:
                mouse_pos = evento.pos
                # Resalta la opción bajo el mouse
                for i, rect in enumerate(rects_opciones):
                    if rect.collidepoint(mouse_pos):
                        opcion_ajustes = i
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = evento.pos
                for i, rect in enumerate(rects_opciones):
                    if rect.collidepoint(mouse_pos):
                        opcion_ajustes = i
                        # Acciones con clic
                        if opcion_ajustes == 0:
                            # Volumen música: clic izquierdo/derecho sube/baja
                            if evento.button == 1:
                                volumen_musica = min(1.0, volumen_musica + 0.05)
                            elif evento.button == 3:
                                volumen_musica = max(0.0, volumen_musica - 0.05)
                            aplicar_volumen()
                        elif opcion_ajustes == 1:
                            if evento.button == 1:
                                volumen_efectos = min(1.0, volumen_efectos + 0.05)
                            elif evento.button == 3:
                                volumen_efectos = max(0.0, volumen_efectos - 0.05)
                        elif opcion_ajustes == 2:
                            cambiar_pantalla_completa()
                        elif opcion_ajustes == 3:
                            if evento.button == 1:
                                indice_dificultad = (indice_dificultad + 1) % len(dificultad_niveles)
                            elif evento.button == 3:
                                indice_dificultad = (indice_dificultad - 1) % len(dificultad_niveles)
                        elif opcion_ajustes == 4:
                            guardar_config()
                            run = False

        pygame.display.flip()
        pygame.time.Clock().tick(30)

def dibujar_menu():
    if fondo:
        pantalla.blit(pygame.transform.scale(fondo, (ANCHO, ALTO)), (0, 0))
    else:
        pantalla.fill(GRIS_OSCURO)



    # --- Título animado inspirado en el logo adjunto ---
    fuente_logo_grande = pygame.font.SysFont("arialblack", 64, bold=True)
    x_centro = ANCHO//2
    y_titulo = 70
    # Animación de aparición (fade in y subida)
    if not hasattr(dibujar_menu, "titulo_anim_timer"):
        dibujar_menu.titulo_anim_timer = pygame.time.get_ticks()
    tiempo_actual = pygame.time.get_ticks()
    duracion_titulo = 700
    progreso_titulo = min(1.0, (tiempo_actual - dibujar_menu.titulo_anim_timer) / duracion_titulo)
    alpha_titulo = int(255 * progreso_titulo)
    y_offset = int((1.0 - progreso_titulo) * 40)

    def render_con_sombra_anim(texto, fuente, color, x, y, sombra_color=(0,0,0), sombra_offset=(4,4)):
        surf = pygame.Surface((fuente.size(texto)[0]+20, fuente.get_height()+20), pygame.SRCALPHA)
        sombra = fuente.render(texto, True, sombra_color)
        surf.blit(sombra, (sombra_offset[0]+10, sombra_offset[1]+10))
        render = fuente.render(texto, True, color)
        surf.blit(render, (10,10))
        surf.set_alpha(alpha_titulo)
        pantalla.blit(surf, (x, y + y_offset))

    # Palabra "SHAD" (amarillo)
    texto_shad = "SHAD"
    color_shad = (255, 211, 54)
    render_con_sombra_anim(texto_shad, fuente_logo_grande, color_shad, x_centro - 260, y_titulo)

    # Palabra "OWS" (gris azulado)
    texto_ows = "OWS"
    color_ows = (90, 120, 160)
    render_con_sombra_anim(texto_ows, fuente_logo_grande, color_ows, x_centro - 70, y_titulo)

    # Palabra "OF" (amarillo)
    texto_of = "OF"
    color_of = (255, 211, 54)
    render_con_sombra_anim(texto_of, fuente_logo_grande, color_of, x_centro + 140, y_titulo)

    # Palabra "SKALDHEIM" (azul celeste)
    texto_skald = "SKALDHEIM"
    color_skald = (44, 202, 255)
    ancho_skald = fuente_logo_grande.size(texto_skald)[0]
    # Sombra y trazo animados
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        surf_borde = pygame.Surface((ancho_skald+20, fuente_logo_grande.get_height()+20), pygame.SRCALPHA)
        borde = fuente_logo_grande.render(texto_skald, True, (0,60,120))
        surf_borde.blit(borde, (10,10))
        surf_borde.set_alpha(alpha_titulo)
        pantalla.blit(surf_borde, (x_centro - ancho_skald//2 + dx, y_titulo + 70 + dy + y_offset))
    surf_skald = pygame.Surface((ancho_skald+20, fuente_logo_grande.get_height()+20), pygame.SRCALPHA)
    render = fuente_logo_grande.render(texto_skald, True, color_skald)
    surf_skald.blit(render, (10,10))
    surf_skald.set_alpha(alpha_titulo)
    pantalla.blit(surf_skald, (x_centro - ancho_skald//2, y_titulo + 70 + y_offset))

    # Opcional: dibujar dos "espadas" cruzadas detrás del texto si tienes imágenes
    # Si tienes los archivos de las espadas, puedes cargarlos y dibujarlos aquí
    # Por ejemplo:
    # espada_img = pygame.image.load(os.path.join(ASSETS, "espada.png")).convert_alpha()
    # pantalla.blit(espada_img, (x_centro - 120, y_titulo - 60))


    # Versión (aparece junto con el título)
    if progreso_titulo > 0.95:
        dibujar_texto("v1.0", fuente_version, BLANCO, pantalla, ANCHO - 80, ALTO - 30)

    # --- Menú principal: opciones bien organizadas y separadas del título ---
    mouse_pos = pygame.mouse.get_pos()

    # --- Animación de aparición para las opciones del menú ---
    if not hasattr(dibujar_menu, "anim_timer") or progreso_titulo < 1.0:
        dibujar_menu.anim_timer = pygame.time.get_ticks()
        dibujar_menu.anim_progreso = [0.0 for _ in botones_menu]
    tiempo_actual = pygame.time.get_ticks()
    duracion_anim = 350  # ms por botón
    delay = 80  # ms entre botones
    for i in range(len(botones_menu)):
        t_inicio = dibujar_menu.anim_timer + i * delay
        if progreso_titulo >= 1.0 and tiempo_actual > t_inicio:
            progreso = min(1.0, (tiempo_actual - t_inicio) / duracion_anim)
            dibujar_menu.anim_progreso[i] = progreso
        else:
            dibujar_menu.anim_progreso[i] = 0.0

    # Caja para los botones (más compacta y ajustada)
    caja_ancho = 320
    alto_boton = 40
    espacio = 10
    margen_superior = 18
    total_altura = alto_boton * len(botones_menu) + espacio * (len(botones_menu) - 1)
    caja_alto = total_altura + margen_superior * 2
    caja_x = (ANCHO - caja_ancho) // 2
    caja_y = int(ALTO * 0.40)
    sombra_surf = pygame.Surface((caja_ancho+16, caja_alto+16), pygame.SRCALPHA)
    pygame.draw.rect(sombra_surf, (0,0,0,90), sombra_surf.get_rect(), border_radius=22)
    pantalla.blit(sombra_surf, (caja_x-8, caja_y+8))
    caja_surf = pygame.Surface((caja_ancho, caja_alto), pygame.SRCALPHA)
    pygame.draw.rect(caja_surf, (60, 80, 140, 220), caja_surf.get_rect(), border_radius=16)
    pygame.draw.rect(caja_surf, (200,220,255,80), caja_surf.get_rect(), 3, border_radius=16)
    pantalla.blit(caja_surf, (caja_x, caja_y))

    # Botones organizados dentro de la caja (sin animación)
    global opcion_menu_principal
    for i, boton in enumerate(botones_menu):
        boton.rect.width = caja_ancho - 32
        boton.rect.height = alto_boton
        boton.rect.x = caja_x + 16
        boton.rect.y = caja_y + margen_superior + i * (alto_boton + espacio)
        # Resalta el botón si está seleccionado por teclado
        if i == opcion_menu_principal:
            boton.hover = True
        else:
            boton.verificar_hover(mouse_pos)
        boton.dibujar(pantalla)

def seleccionar_mundo():

    # Fondo degradado vertical
    grad = pygame.Surface((ANCHO, ALTO))
    for y in range(ALTO):
        ratio = y / ALTO
        r = int(40 * (1 - ratio) + 80 * ratio)
        g = int(60 * (1 - ratio) + 120 * ratio)
        b = int(120 * (1 - ratio) + 220 * ratio)
        grad.fill((r, g, b), rect=pygame.Rect(0, y, ANCHO, 1))
    grad.set_alpha(220)
    pantalla.blit(grad, (0, 0))

    # Título con sombra
    titulo = "Selecciona un Mundo"
    sombra = fuente_titulo.render(titulo, True, (0,0,0))
    pantalla.blit(sombra, (ANCHO//2 - sombra.get_width()//2 + 3, 53))
    render_titulo = fuente_titulo.render(titulo, True, (255,255,255))
    pantalla.blit(render_titulo, (ANCHO//2 - render_titulo.get_width()//2, 50))

    # Caja de selección con sombra y bordes
    caja_ancho = 420
    caja_alto = 260
    caja_x = (ANCHO - caja_ancho) // 2
    caja_y = (ALTO - caja_alto) // 2
    # Sombra
    sombra_rect = pygame.Rect(caja_x-8, caja_y+8, caja_ancho+16, caja_alto+16)
    sombra_surf = pygame.Surface((caja_ancho+16, caja_alto+16), pygame.SRCALPHA)
    pygame.draw.rect(sombra_surf, (0,0,0,90), sombra_surf.get_rect(), border_radius=32)
    pantalla.blit(sombra_surf, (caja_x-8, caja_y+8))
    # Caja principal
    caja_surf = pygame.Surface((caja_ancho, caja_alto), pygame.SRCALPHA)
    pygame.draw.rect(caja_surf, (60, 80, 140, 220), caja_surf.get_rect(), border_radius=28)
    pygame.draw.rect(caja_surf, (200,220,255,80), caja_surf.get_rect(), 4, border_radius=28)
    pantalla.blit(caja_surf, (caja_x, caja_y))

    # Botones de mundos, organizados dentro de la caja
    mouse_pos = pygame.mouse.get_pos()
    espacio = 24
    alto_boton = 54
    ancho_boton = 320
    total_altura = alto_boton * len(botones_mundos) + espacio * (len(botones_mundos) - 1)
    inicio_y = caja_y + (caja_alto - total_altura) // 2
    for i, boton in enumerate(botones_mundos):
        boton.rect.width = ancho_boton
        boton.rect.height = alto_boton
        boton.rect.x = caja_x + (caja_ancho - ancho_boton)//2
        boton.rect.y = inicio_y + i * (alto_boton + espacio)
        boton.verificar_hover(mouse_pos)
        boton.dibujar(pantalla)

    # Pie de página con instrucción
    fuente_pie = pygame.font.SysFont("verdana", 20, italic=True)
    pie = fuente_pie.render("Haz clic en un mundo para continuar", True, (230,230,255))
    sombra_pie = fuente_pie.render("Haz clic en un mundo para continuar", True, (0,0,0))
    pantalla.blit(sombra_pie, (ANCHO//2 - pie.get_width()//2 + 2, caja_y + caja_alto + 22))
    pantalla.blit(pie, (ANCHO//2 - pie.get_width()//2, caja_y + caja_alto + 20))

def crear_personaje():
    global indice_piel, indice_pelo, indice_ropa
    # Fondo degradado
    grad = pygame.Surface((ANCHO, ALTO))
    for y in range(ALTO):
        ratio = y / ALTO
        r = int(40 * (1 - ratio) + 80 * ratio)
        g = int(60 * (1 - ratio) + 120 * ratio)
        b = int(120 * (1 - ratio) + 220 * ratio)
        grad.fill((r, g, b), rect=pygame.Rect(0, y, ANCHO, 1))
    grad.set_alpha(220)
    pantalla.blit(grad, (0, 0))

    # Caja central estilo Pokémon Esmeralda
    caja_ancho = 540
    caja_alto = 420
    caja_x = (ANCHO - caja_ancho) // 2
    caja_y = (ALTO - caja_alto) // 2
    sombra_rect = pygame.Rect(caja_x-12, caja_y+12, caja_ancho+24, caja_alto+24)
    sombra_surf = pygame.Surface((caja_ancho+24, caja_alto+24), pygame.SRCALPHA)
    pygame.draw.rect(sombra_surf, (0,0,0,100), sombra_surf.get_rect(), border_radius=32)
    pantalla.blit(sombra_surf, (caja_x-12, caja_y+12))
    caja_surf = pygame.Surface((caja_ancho, caja_alto), pygame.SRCALPHA)
    pygame.draw.rect(caja_surf, (60, 80, 140, 230), caja_surf.get_rect(), border_radius=22)
    pygame.draw.rect(caja_surf, (255,255,255,60), caja_surf.get_rect(), 0, border_radius=22)
    pygame.draw.rect(caja_surf, (200,220,255,120), caja_surf.get_rect(), 4, border_radius=22)
    pantalla.blit(caja_surf, (caja_x, caja_y))

    # Título con sombra
    titulo = "Crea tu Personaje"
    fuente_titulo_crea = pygame.font.SysFont("arialblack", 38, bold=True)
    sombra = fuente_titulo_crea.render(titulo, True, (0,0,0))
    pantalla.blit(sombra, (ANCHO//2 - sombra.get_width()//2 + 2, caja_y - 32))
    render_titulo = fuente_titulo_crea.render(titulo, True, (255,255,255))
    pantalla.blit(render_titulo, (ANCHO//2 - render_titulo.get_width()//2, caja_y - 36))

    # Vista previa grande del personaje (centro de la caja)
    centro_x = ANCHO // 2
    centro_y = caja_y + 120
    # Cuerpo (piel)
    pygame.draw.circle(pantalla, colores_piel[indice_piel], (centro_x, centro_y), 54)
    pygame.draw.circle(pantalla, (255,255,255), (centro_x, centro_y), 56, 3)
    # Pelo (arriba)
    pygame.draw.circle(pantalla, colores_pelo[indice_pelo], (centro_x, centro_y-38), 28)
    # Ropa (debajo)
    pygame.draw.rect(pantalla, colores_ropa[indice_ropa], (centro_x-38, centro_y+30, 76, 38), border_radius=16)
    pygame.draw.rect(pantalla, (255,255,255), (centro_x-40, centro_y+28, 80, 42), 2, border_radius=18)

    # Opciones de personalización debajo, cada una con flechas y nombre
    fuente_opc = pygame.font.SysFont("verdana", 26, bold=True)
    fuente_valor = pygame.font.SysFont("verdana", 22, bold=True)
    opciones = [
        ("Piel", colores_piel, indice_piel),
        ("Pelo", colores_pelo, indice_pelo),
        ("Ropa", colores_ropa, indice_ropa)
    ]
    mouse_pos = pygame.mouse.get_pos()
    base_y = caja_y + 220
    for idx, (nombre, lista, ind) in enumerate(opciones):
        y = base_y + idx * 54
        # Flecha izq
        flecha_color = (180,180,220)
        puntos_izq = [
            (centro_x-120, y),
            (centro_x-100, y-18),
            (centro_x-100, y+18)
        ]
        pygame.draw.polygon(pantalla, flecha_color, puntos_izq)
        # Flecha der
        puntos_der = [
            (centro_x+120, y),
            (centro_x+100, y-18),
            (centro_x+100, y+18)
        ]
        pygame.draw.polygon(pantalla, flecha_color, puntos_der)
        # Nombre de la opción
        txt = fuente_opc.render(nombre, True, (255,255,255))
        pantalla.blit(txt, txt.get_rect(center=(centro_x-60, y)))
        # Color actual (círculo o rectángulo)
        if nombre != "Ropa":
            pygame.draw.circle(pantalla, lista[ind], (centro_x+20, y), 18)
            pygame.draw.circle(pantalla, (255,255,255), (centro_x+20, y), 20, 2)
        else:
            pygame.draw.rect(pantalla, lista[ind], (centro_x+2, y-16, 36, 32), border_radius=8)
            pygame.draw.rect(pantalla, (255,255,255), (centro_x+2, y-16, 36, 32), 2, border_radius=8)

    # Botones abajo
    boton_adelante.verificar_hover(mouse_pos)
    boton_adelante.dibujar(pantalla)
    txt = fuente_valor.render("Siguiente", True, (255,255,255))
    pantalla.blit(txt, txt.get_rect(center=boton_adelante.rect.center))

    boton_atras.verificar_hover(mouse_pos)
    boton_atras.dibujar(pantalla)
    txt = fuente_valor.render("Atrás", True, (255,255,255))
    pantalla.blit(txt, txt.get_rect(center=boton_atras.rect.center))

def mostrar_introduccion():
    global linea_actual, ultimo_tiempo, estado

    # Fondo degradado vertical
    grad = pygame.Surface((ANCHO, ALTO))
    for y in range(ALTO):
        ratio = y / ALTO
        r = int(40 * (1 - ratio) + 80 * ratio)
        g = int(60 * (1 - ratio) + 120 * ratio)
        b = int(120 * (1 - ratio) + 220 * ratio)
        grad.fill((r, g, b), rect=pygame.Rect(0, y, ANCHO, 1))
    grad.set_alpha(220)
    pantalla.blit(grad, (0, 0))

    # Caja central con sombra y bordes para el texto
    caja_ancho = 700
    caja_alto = 260
    caja_x = (ANCHO - caja_ancho) // 2
    caja_y = (ALTO - caja_alto) // 2 - 30
    sombra_rect = pygame.Rect(caja_x-10, caja_y+10, caja_ancho+20, caja_alto+20)
    sombra_surf = pygame.Surface((caja_ancho+20, caja_alto+20), pygame.SRCALPHA)
    pygame.draw.rect(sombra_surf, (0,0,0,90), sombra_surf.get_rect(), border_radius=32)
    pantalla.blit(sombra_surf, (caja_x-10, caja_y+10))
    caja_surf = pygame.Surface((caja_ancho, caja_alto), pygame.SRCALPHA)
    pygame.draw.rect(caja_surf, (60, 80, 140, 220), caja_surf.get_rect(), border_radius=28)
    pygame.draw.rect(caja_surf, (200,220,255,80), caja_surf.get_rect(), 4, border_radius=28)
    pantalla.blit(caja_surf, (caja_x, caja_y))

    # Título con sombra
    titulo = "Introducción"
    sombra = fuente_titulo.render(titulo, True, (0,0,0))
    pantalla.blit(sombra, (ANCHO//2 - sombra.get_width()//2 + 3, caja_y + 13))
    render_titulo = fuente_titulo.render(titulo, True, (255,255,255))
    pantalla.blit(render_titulo, (ANCHO//2 - render_titulo.get_width()//2, caja_y + 10))

    # Texto de introducción, centrado y con efecto de "aparecer"
    tiempo_actual = pygame.time.get_ticks()
    if tiempo_actual - ultimo_tiempo > TIEMPO_ENTRE_LINEAS:
        if linea_actual < len(introduccion) - 1:
            linea_actual += 1
            ultimo_tiempo = tiempo_actual

    fuente_intro_grande = pygame.font.SysFont("timesnewroman", 28, italic=True)
    y_texto = caja_y + 80
    for i in range(linea_actual + 1):
        linea = introduccion[i]
        # Sombra de texto
        render_sombra = fuente_intro_grande.render(linea, True, (0,0,0))
        pantalla.blit(render_sombra, (ANCHO//2 - render_sombra.get_width()//2 + 2, y_texto + 2))
        render_linea = fuente_intro_grande.render(linea, True, (230,230,255))
        pantalla.blit(render_linea, (ANCHO//2 - render_linea.get_width()//2, y_texto))
        y_texto += 38

    # Pie de página con instrucción
    fuente_pie = pygame.font.SysFont("verdana", 20, italic=True)
    pie = fuente_pie.render("Presiona ESC para volver o ENTER para continuar", True, (230,230,255))
    sombra_pie = fuente_pie.render("Presiona ESC para volver o ENTER para continuar", True, (0,0,0))
    pantalla.blit(sombra_pie, (ANCHO//2 - pie.get_width()//2 + 2, caja_y + caja_alto + 22))
    pantalla.blit(pie, (ANCHO//2 - pie.get_width()//2, caja_y + caja_alto + 20))

# --- Créditos con scroll tipo Marvel ---
def mostrar_creditos():
    global estado
    creditos = [
        "SHADOWS OF SKALDHEIM",
        "",
        "Desarrollador principal: Milav",
        "Arte y diseño: Equipo Skaldheim",
        "Música: Compositor Invitado",
        "Agradecimientos: Comunidad Python",
        "",
        "¡Gracias por jugar!"
    ]
    fuente_titulo = pygame.font.SysFont("arialblack", 54, bold=True)
    fuente_credito = pygame.font.SysFont("verdana", 32, bold=True)
    fuente_normal = pygame.font.SysFont("verdana", 26, bold=True)
    clock = pygame.time.Clock()
    # Calcular altura total del bloque de créditos
    altura_lineas = []
    for i, linea in enumerate(creditos):
        if i == 0:
            altura_lineas.append(fuente_titulo.get_height())
        elif linea == "":
            altura_lineas.append(30)
        else:
            altura_lineas.append(fuente_credito.get_height() if i < 2 else fuente_normal.get_height())
    total_altura = sum(altura_lineas) + 60
    # Posición inicial (debajo de la pantalla)
    y_scroll = ALTO
    velocidad = 1.2  # Puedes ajustar la velocidad
    run = True
    while run:
        pantalla.fill((0,0,0))
        y = y_scroll
        for i, linea in enumerate(creditos):
            if i == 0:
                fuente = fuente_titulo
                color = (255, 211, 54)
            elif i < 2:
                fuente = fuente_credito
                color = (255,255,255)
            else:
                fuente = fuente_normal
                color = (255,255,255)
            render = fuente.render(linea, True, color)
            sombra = fuente.render(linea, True, (0,0,0))
            x = ANCHO//2 - render.get_width()//2
            # Sombra
            pantalla.blit(sombra, (x+2, y+2))
            pantalla.blit(render, (x, y))
            y += altura_lineas[i]
        # Pie de página
        fuente_pie = pygame.font.SysFont("verdana", 20, italic=True)
        pie = fuente_pie.render("Presiona ESC para volver", True, (200,200,200))
        pantalla.blit(pie, (ANCHO//2 - pie.get_width()//2, ALTO - 40))
        pygame.display.flip()
        clock.tick(60)
        y_scroll -= velocidad
        # Cuando termina el scroll, volver automáticamente
        if y + 20 < 0:
            run = False
            estado = MENU_PRINCIPAL
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    run = False
                    estado = MENU_PRINCIPAL

def main():

    global estado
    global indice_piel, indice_pelo, indice_ropa
    global opcion_ajustes, linea_actual
    global opcion_menu_principal

    cargar_config()
    aplicar_volumen()

    reloj = pygame.time.Clock()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                guardar_config()
                pygame.quit()
                sys.exit()


            elif evento.type == pygame.KEYDOWN:
                if estado == INTRODUCCION:
                    if evento.key == pygame.K_ESCAPE:
                        estado = MENU_PRINCIPAL
                        linea_actual = 0
                    elif evento.key == pygame.K_RETURN:
                        estado = MENU_PRINCIPAL
                        linea_actual = 0

                elif estado == AJUSTES:
                    # En ajustes la navegación es interna, la manejamos dentro de la función ajustes()
                    pass

                elif estado == CREAR_PERSONAJE:
                    if evento.key == pygame.K_ESCAPE:
                        estado = MENU_PRINCIPAL

                elif estado == CREDITOS:
                    if evento.key == pygame.K_ESCAPE:
                        estado = MENU_PRINCIPAL

                elif estado == MENU_PRINCIPAL:
                    if evento.key == pygame.K_ESCAPE:
                        guardar_config()
                        pygame.quit()
                        sys.exit()
                    elif evento.key == pygame.K_UP:
                        opcion_menu_principal = (opcion_menu_principal - 1) % len(botones_menu)
                    elif evento.key == pygame.K_DOWN:
                        opcion_menu_principal = (opcion_menu_principal + 1) % len(botones_menu)
                    elif evento.key == pygame.K_RETURN:
                        i = opcion_menu_principal
                        if i == 0:
                            estado = SELECCION_MUNDO
                        elif i == 1:
                            estado = MULTIJUGADOR
                        elif i == 2:
                            estado = TUTORIAL
                        elif i == 3:
                            estado = LOGROS
                        elif i == 4:
                            estado = CREDITOS
                        elif i == 5:
                            estado = AJUSTES


            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if estado == MENU_PRINCIPAL:
                    for i, boton in enumerate(botones_menu):
                        if boton.clic(mouse_pos):
                            opcion_menu_principal = i
                            if i == 0:
                                estado = SELECCION_MUNDO
                            elif i == 1:
                                estado = MULTIJUGADOR
                            elif i == 2:
                                estado = TUTORIAL
                            elif i == 3:
                                estado = LOGROS
                            elif i == 4:
                                estado = CREDITOS
                            elif i == 5:
                                estado = AJUSTES

                elif estado == SELECCION_MUNDO:
                    for i, boton in enumerate(botones_mundos):
                        if boton.clic(mouse_pos):
                            print(f"Mundo seleccionado: {mundos[i]}")
                            estado = CREAR_PERSONAJE

                elif estado == CREAR_PERSONAJE:
                    # Flechas piel
                    for i, flecha in enumerate(flechas_piel):
                        if flecha.clic(mouse_pos):
                            if i == 0:  # izquierda
                                indice_piel = (indice_piel - 1) % len(colores_piel)
                            else:
                                indice_piel = (indice_piel + 1) % len(colores_piel)
                    # Flechas pelo
                    for i, flecha in enumerate(flechas_pelo):
                        if flecha.clic(mouse_pos):
                            if i == 0:
                                indice_pelo = (indice_pelo - 1) % len(colores_pelo)
                            else:
                                indice_pelo = (indice_pelo + 1) % len(colores_pelo)
                    # Flechas ropa
                    for i, flecha in enumerate(flechas_ropa):
                        if flecha.clic(mouse_pos):
                            if i == 0:
                                indice_ropa = (indice_ropa - 1) % len(colores_ropa)
                            else:
                                indice_ropa = (indice_ropa + 1) % len(colores_ropa)

                    if boton_adelante.clic(mouse_pos):
                        print("Personaje creado con: piel", indice_piel, "pelo", indice_pelo, "ropa", indice_ropa)
                        estado = INTRODUCCION
                        linea_actual = 0

                    if boton_atras.clic(mouse_pos):
                        estado = SELECCION_MUNDO

        # Dibujo según estado
        if estado == MENU_PRINCIPAL:
            dibujar_menu()
        elif estado == SELECCION_MUNDO:
            seleccionar_mundo()
        elif estado == CREAR_PERSONAJE:
            crear_personaje()
        elif estado == INTRODUCCION:
            mostrar_introduccion()
        elif estado == AJUSTES:
            ajustes()
            estado = MENU_PRINCIPAL  # Volver al menú tras cerrar ajustes
        elif estado == CREDITOS:
            mostrar_creditos()

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()