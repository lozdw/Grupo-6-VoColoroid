import math
import pygame
try:
    import cv2
except ImportError:
    cv2 = None
from score import GestorPuntuacion
from funtions import GestorSecuencia
from personajes import Miku, Teto, Neru, Gumi

class App:
    def __init__(self, config):
        self.pantalla = pygame.display.set_mode((config.ancho_pantalla, config.alto_pantalla))
        pygame.display.set_caption(config.titulo)
        self.reloj = pygame.time.Clock()
        self.fps_objetivo = config.fps
        self.ejecutando = True

        self.gestor_puntuacion = GestorPuntuacion()
        self.gestor_secuencia = GestorSecuencia(config.archivo_niveles)
        self.personaje_actual = None
        self.penalizacion_error = 2.0

        pygame.font.init()
        self.fuente_titulo = pygame.font.Font(str(config.archivo_fuente), 48)
        self.fuente_normal = pygame.font.Font(str(config.archivo_fuente), 24)
        self.fuente_mensaje = pygame.font.Font(str(config.archivo_fuente), 16)
        self.musica_reproduciendose = False
        self.musica_silenciada = False
        self.volumen_musica = 0.1
        if pygame.mixer.get_init() and config.archivo_musica.exists():
            pygame.mixer.music.load(str(config.archivo_musica))
            pygame.mixer.music.set_volume(self.volumen_musica)
            pygame.mixer.music.play(-1)
            self.musica_reproduciendose = True
        self.sonido_boton_rojo = None
        if pygame.mixer.get_init() and config.archivo_sonido_rojo.exists():
            self.sonido_boton_rojo = pygame.mixer.Sound(str(config.archivo_sonido_rojo))
            self.sonido_boton_rojo.set_volume(0.1)
        self.sonido_boton_azul = None
        if pygame.mixer.get_init() and config.archivo_sonido_azul.exists():
            self.sonido_boton_azul = pygame.mixer.Sound(str(config.archivo_sonido_azul))
            self.sonido_boton_azul.set_volume(0.3)
        self.sonido_boton_verde = None
        if pygame.mixer.get_init() and config.archivo_sonido_verde.exists():
            self.sonido_boton_verde = pygame.mixer.Sound(str(config.archivo_sonido_verde))
            self.sonido_boton_verde.set_volume(0.3)
        self.sonido_boton_amarillo = None
        if pygame.mixer.get_init() and config.archivo_sonido_amarillo.exists():
            self.sonido_boton_amarillo = pygame.mixer.Sound(str(config.archivo_sonido_amarillo))
            self.sonido_boton_amarillo.set_volume(0.3)
        self.sonido_seleccion_personaje = None
        if pygame.mixer.get_init() and config.archivo_sonido_seleccion_personaje.exists():
            self.sonido_seleccion_personaje = pygame.mixer.Sound(
                str(config.archivo_sonido_seleccion_personaje)
            )
            self.sonido_seleccion_personaje.set_volume(1.0)
        self.sonido_iniciar = None
        if pygame.mixer.get_init() and config.archivo_sonido_iniciar.exists():
            self.sonido_iniciar = pygame.mixer.Sound(str(config.archivo_sonido_iniciar))
            self.sonido_iniciar.set_volume(1.0)
        self.sonido_nivel = None
        if pygame.mixer.get_init() and config.archivo_sonido_nivel.exists():
            self.sonido_nivel = pygame.mixer.Sound(str(config.archivo_sonido_nivel))
            self.sonido_nivel.set_volume(0.3)
        self.sonido_reinicio = None
        if pygame.mixer.get_init() and config.archivo_sonido_reinicio.exists():
            self.sonido_reinicio = pygame.mixer.Sound(str(config.archivo_sonido_reinicio))
            self.sonido_reinicio.set_volume(0.3)
        self.sonido_corazon = None
        if pygame.mixer.get_init() and config.archivo_sonido_corazon.exists():
            self.sonido_corazon = pygame.mixer.Sound(str(config.archivo_sonido_corazon))
            self.sonido_corazon.set_volume(0.3)
        self.sonido_settings = None
        if pygame.mixer.get_init() and config.archivo_sonido_settings.exists():
            self.sonido_settings = pygame.mixer.Sound(str(config.archivo_sonido_settings))
            self.sonido_settings.set_volume(0.3)

        directorio_imagenes = config.directorio_base / "assets" / "images"
        directorio_fondos = config.directorio_base / "assets" / "backgrounds"
        self.marco_menu = pygame.transform.smoothscale(
            pygame.image.load(directorio_fondos / "fondo cortado.png").convert_alpha(),
            self.pantalla.get_size(),
        )
        self.marco_menu.set_colorkey((42, 43, 46))
        self.fondo_menu = self.marco_menu.copy()
        self.fondo_seleccion = pygame.transform.smoothscale(
            pygame.image.load(directorio_fondos / "5 sin título.png").convert(),
            self.pantalla.get_size(),
        )
        self.fondo_juego = pygame.transform.smoothscale(
            pygame.image.load(directorio_fondos / "Fondo Juego Colores.png").convert_alpha(),
            self.pantalla.get_size(),
        )
        logo_inicio_original = pygame.image.load(
            directorio_fondos / "Logo VoColoroid con N.png"
        ).convert_alpha()
        ancho_logo_inicio = 400
        alto_logo_inicio = round(
            logo_inicio_original.get_height()
            * ancho_logo_inicio
            / logo_inicio_original.get_width()
        )
        self.logo_inicio = pygame.transform.smoothscale(
            logo_inicio_original,
            (ancho_logo_inicio, alto_logo_inicio),
        )
        desplazamiento_inicio = 86
        self.rect_logo_inicio = self.logo_inicio.get_rect(
            center=(self.pantalla.get_rect().centerx, 205 + desplazamiento_inicio)
        )
        imagen_boton_creditos = pygame.image.load(
            directorio_imagenes / "boton creditos.png"
        ).convert_alpha()
        self.boton_creditos = pygame.transform.smoothscale(imagen_boton_creditos, (72, 72))
        self.rect_boton_creditos = self.boton_creditos.get_rect(
            bottomright=(self.pantalla.get_rect().right - 149, self.pantalla.get_rect().bottom - 63)
        )
        imagen_boton_settings = pygame.image.load(
            directorio_imagenes / "boton setting.png"
        ).convert_alpha()
        self.boton_settings = imagen_boton_settings
        self.rect_boton_settings = self.boton_settings.get_rect(
            left=self.rect_boton_creditos.right - 20,
            centery=self.rect_boton_creditos.centery,
        )
        self.tiempo_boton_creditos_presionado = 0
        self.ventana_creditos_abierta = False
        self.ventana_settings_abierta = False
        self.sonidos_sistema_silenciados = False
        self.rect_ajuste_musica = pygame.Rect(0, 0, 360, 42)
        self.rect_ajuste_musica.center = (self.pantalla.get_rect().centerx, 365)
        self.rect_ajuste_sistema = self.rect_ajuste_musica.move(0, 58)
        self.video_fondo = None
        if cv2 is not None:
            self.video_fondo = cv2.VideoCapture(str(directorio_fondos / "e.mp4"))
        nombres_colores = {
            1: "rojo",
            2: "azul",
            3: "verde",
            4: "amarillo",
        }
        tamano_boton_juego = 300
        self.imagenes_botones = {
            numero: {
                "normal": pygame.transform.smoothscale(
                    pygame.image.load(
                        directorio_imagenes / f"asset {nombre} final.png"
                    ).convert_alpha(),
                    (tamano_boton_juego, tamano_boton_juego),
                ),
                "presionado": pygame.transform.smoothscale(
                    pygame.image.load(
                        directorio_imagenes / f"asset {nombre} pressed final.png"
                    ).convert_alpha(),
                    (tamano_boton_juego, tamano_boton_juego),
                ),
            }
            for numero, nombre in nombres_colores.items()
        }
        circulo_extra_original = pygame.image.load(
            directorio_imagenes / "circulo.png"
        ).convert_alpha()
        self.escala_circulo_extra = 650 / 987
        self.circulo_extra = pygame.transform.smoothscale(
            circulo_extra_original,
            (
            round(circulo_extra_original.get_width() * self.escala_circulo_extra),
            round(circulo_extra_original.get_height() * self.escala_circulo_extra),
            ),
        )
        self.logo_intro = pygame.image.load(directorio_fondos / "logo redondo.png").convert_alpha()
        self.logo_intro = pygame.transform.smoothscale(self.logo_intro, (420, 420))
        self.rect_logo_intro = self.logo_intro.get_rect(center=self.pantalla.get_rect().center)

        tamano_imagen_personaje = 170
        nombres_imagenes_personajes = {
            "Miku": "Miku Pixel Cabeza.png",
            "Teto": "Teto Pixel Cabeza.png",
            "Neru": "Neru Pixel Cabeza .png",
            "Gumi": "Gumi Pixel Cabeza.png",
        }
        self.imagenes_personajes = {
            nombre: pygame.transform.smoothscale(
                pygame.image.load(directorio_imagenes / archivo).convert_alpha(),
                (tamano_imagen_personaje, tamano_imagen_personaje),
            )
            for nombre, archivo in nombres_imagenes_personajes.items()
        }
        nombres_imagenes_personajes_hover = {
            "Miku": "Miku Guiño.png",
            "Teto": "Teto Guiño.png",
            "Neru": "Neru Guiño.png",
            "Gumi": "Gumi Guiño.png",
        }
        self.imagenes_personajes_hover = {
            nombre: pygame.transform.smoothscale(
                pygame.image.load(directorio_imagenes / archivo).convert_alpha(),
                (tamano_imagen_personaje, tamano_imagen_personaje),
            )
            for nombre, archivo in nombres_imagenes_personajes_hover.items()
        }
        self.fondo_recuadro_neru = pygame.transform.smoothscale(
            pygame.image.load(directorio_imagenes / "cuADRO AMARILLO.png").convert_alpha(),
            (210, 210),
        )
        self.fondo_recuadro_teto = pygame.transform.smoothscale(
            pygame.image.load(directorio_imagenes / "cua rojo.png").convert_alpha(),
            (210, 210),
        )
        self.fondo_recuadro_gumi = pygame.transform.smoothscale(
            pygame.image.load(directorio_imagenes / "cua verde.png").convert_alpha(),
            (210, 210),
        )
        self.fondo_recuadro_miku = pygame.transform.smoothscale(
            pygame.image.load(directorio_imagenes / "cua azul.png").convert_alpha(),
            (210, 210),
        )
        imagen_marcos_tiempo = pygame.image.load(
            directorio_imagenes / "Barras de tiempo.png"
        ).convert_alpha()
        recortes_marcos_tiempo = {
            "Miku": pygame.Rect(0, 0, 430, 50),
            "Teto": pygame.Rect(435, 0, 430, 50),
            "Neru": pygame.Rect(0, 70, 430, 50),
            "Gumi": pygame.Rect(435, 70, 430, 50),
            "generico": pygame.Rect(180, 150, 435, 40),
        }
        tamano_marco_tiempo = (240, 21)
        self.marcos_barra_tiempo = {
            nombre: pygame.transform.smoothscale(
                imagen_marcos_tiempo.subsurface(recorte),
                tamano_marco_tiempo,
            )
            for nombre, recorte in recortes_marcos_tiempo.items()
        }

        self.estado_actual = "INTRO" # INTRO, MENU, SELECCION, TRANSICION_NIVEL, MOSTRANDO_SECUENCIA, JUGANDO, GAME_OVER
        self.tiempo_inicio_intro = pygame.time.get_ticks()
        
        # Colores (1: Rojo, 2: Azul, 3: Verde, 4: Amarillo - Basado en tu Tkinter)
        self.colores_base = {
            1: (150, 0, 0),    
            2: (0, 0, 150),    
            3: (0, 150, 0),    
            4: (150, 150, 0)   
        }
        self.colores_brillantes = {
            1: (255, 50, 50),
            2: (50, 50, 255),
            3: (50, 255, 50),
            4: (255, 255, 50)
        }
        
        centro_juego = self.pantalla.get_rect().center
        inicio_juego_x = centro_juego[0] - 300
        inicio_juego_y = centro_juego[1] - 300
        self.rects_botones = {
            3: pygame.Rect(inicio_juego_x, inicio_juego_y, 300, 300), # Verde (Arriba izquierda)
            2: pygame.Rect(inicio_juego_x + 300, inicio_juego_y, 300, 300), # Azul (Arriba derecha)
            4: pygame.Rect(inicio_juego_x, inicio_juego_y + 300, 300, 300), # Amarillo (Abajo izquierda)
            1: pygame.Rect(inicio_juego_x + 300, inicio_juego_y + 300, 300, 300), # Rojo (Abajo derecha)
        }
        
        self.rect_barra_tiempo = pygame.Rect(0, 0, *tamano_marco_tiempo)
        self.rect_barra_tiempo.center = (150, centro_juego[1] + 25)
        self.estrellita = self.crear_estrellita(84)
        
        centro_x = self.pantalla.get_rect().centerx
        centro_y = self.pantalla.get_rect().centery
        desplazamiento_inicio = 86
        self.rect_iniciar = pygame.Rect(
            centro_x - 200,
            centro_y - 35 + desplazamiento_inicio,
            400,
            70,
        )
        ancho_boton_personaje = 210
        alto_boton_personaje = 210
        espacio_boton_personaje = 15
        inicio_x = centro_x - (
            (ancho_boton_personaje * 4 + espacio_boton_personaje * 3) // 2
        )
        inicio_y = centro_y - 190
        self.rect_miku = pygame.Rect(inicio_x, inicio_y, ancho_boton_personaje, alto_boton_personaje)
        self.rect_teto = pygame.Rect(
            inicio_x + ancho_boton_personaje + espacio_boton_personaje,
            inicio_y,
            ancho_boton_personaje,
            alto_boton_personaje,
        )
        self.rect_neru = pygame.Rect(
            inicio_x + (ancho_boton_personaje + espacio_boton_personaje) * 2,
            inicio_y,
            ancho_boton_personaje,
            alto_boton_personaje,
        )
        self.rect_gumi = pygame.Rect(
            inicio_x + (ancho_boton_personaje + espacio_boton_personaje) * 3,
            inicio_y,
            ancho_boton_personaje,
            alto_boton_personaje,
        )
        self.rect_personaje_confirmacion = pygame.Rect(
            centro_x - ancho_boton_personaje // 2,
            165,
            ancho_boton_personaje,
            alto_boton_personaje,
        )
        self.rect_continuar = pygame.Rect(centro_x - 200, 500, 400, 70)
        self.personaje_hover = None
        posicion_lateral_x = self.pantalla.get_rect().right - 253
        self.rect_reinicio = pygame.Rect(posicion_lateral_x, centro_y - 55, 200, 50)
        self.rect_volver = pygame.Rect(posicion_lateral_x, centro_y + 5, 200, 50)

        self.t_total = 10.0
        self.t_restante = 10.0
        self.mensaje = "Listo"
        
        # Variables para la animación de parpadeo de secuencia
        self.color_iluminado = None
        self.indice_secuencia = 0
        self.tiempo_ultimo_cambio = 0
        self.luz_encendida = False
        self.boton_presionado = None
        self.tiempo_boton_presionado = 0
        self.tiempo_espera_transicion = 0
        self.tiempo_transicion_nivel = 0
        self.pulsos_por_segundo_personaje = 180 / 60

    def preparar_juego(self):
        self.gestor_secuencia.iniciar_juego()
        self.personaje_actual.reiniciar_habilidad()
        self.penalizacion_error = self.personaje_actual.penalizacion_error
        self.t_total = 10.0
        self.t_restante = 10.0
        self.mensaje = f"Nivel {self.gestor_secuencia.consultar_nivel()}"
        self.iniciar_animacion()

    def saltar_nivel(self):
        if self.personaje_actual is None:
            return

        self.gestor_secuencia.avanzar_nivel()
        self.preparar_juego()

    def actualizar_musica(self):
        if not self.musica_reproduciendose or not pygame.mixer.get_init():
            return

        musica_de_menu = self.estado_actual in ("INTRO", "MENU", "SELECCION", "CONFIRMACION_PERSONAJE")
        if musica_de_menu and pygame.mixer.music.get_busy() is False:
            pygame.mixer.music.unpause()
        elif not musica_de_menu and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def iniciar_animacion(self):
        self.estado_actual = "MOSTRANDO_SECUENCIA"
        self.indice_secuencia = 0
        self.color_iluminado = None
        self.luz_encendida = False
        self.tiempo_ultimo_cambio = pygame.time.get_ticks()

    def iniciar_transicion_nivel(self):
        self.estado_actual = "TRANSICION_NIVEL"
        self.tiempo_transicion_nivel = pygame.time.get_ticks()

    def iniciar_espera_transicion(self):
        self.estado_actual = "ESPERANDO_TRANSICION"
        self.tiempo_espera_transicion = pygame.time.get_ticks() + 150

    def procesar_espera_transicion(self):
        if pygame.time.get_ticks() >= self.tiempo_espera_transicion:
            self.iniciar_transicion_nivel()

    def procesar_transicion_nivel(self):
        tiempo_transcurrido = (pygame.time.get_ticks() - self.tiempo_transicion_nivel) / 1000
        if tiempo_transcurrido >= 3.3:
            self.preparar_juego()

    def procesar_animacion(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_cambio > 500: # 0.5s por parpadeo
            self.tiempo_ultimo_cambio = ahora
            
            if not self.luz_encendida:
                if self.indice_secuencia < len(self.gestor_secuencia.colores_secuencia):
                    self.color_iluminado = self.gestor_secuencia.colores_secuencia[self.indice_secuencia]
                    if self.color_iluminado == 1 and self.sonido_boton_rojo is not None:
                        self.sonido_boton_rojo.play()
                    elif self.color_iluminado == 2 and self.sonido_boton_azul is not None:
                        self.sonido_boton_azul.play()
                    elif self.color_iluminado == 3 and self.sonido_boton_verde is not None:
                        self.sonido_boton_verde.play()
                    elif self.color_iluminado == 4 and self.sonido_boton_amarillo is not None:
                        self.sonido_boton_amarillo.play()
                    self.luz_encendida = True
                else:
                    self.color_iluminado = None
                    self.estado_actual = "JUGANDO"
            else:
                self.color_iluminado = None
                self.luz_encendida = False
                self.indice_secuencia += 1

    def ejecutar(self):
        while self.ejecutando:
            dt = self.reloj.tick(self.fps_objetivo) / 1000.0
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.gestor_secuencia.reiniciar_progreso()
                    self.ejecutando = False
                
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.manejar_clic(evento.pos)

                if (
                    evento.type == pygame.KEYDOWN
                    and evento.key == pygame.K_j
                    and self.estado_actual in (
                        "MOSTRANDO_SECUENCIA",
                        "JUGANDO",
                        "TRANSICION_NIVEL",
                        "ESPERANDO_TRANSICION",
                    )
                ):
                    self.saltar_nivel()

                if evento.type == pygame.MOUSEMOTION and self.estado_actual == "SELECCION":
                    self.actualizar_personaje_hover(evento.pos)

            # Restar tiempo solo si el jugador tiene el control
            if self.estado_actual == "JUGANDO":
                self.t_restante -= dt
                if self.t_restante <= 0:
                    self.t_restante = 0
                    self.estado_actual = "GAME_OVER"

            if self.estado_actual == "MOSTRANDO_SECUENCIA":
                self.procesar_animacion()

            if self.estado_actual == "TRANSICION_NIVEL":
                self.procesar_transicion_nivel()

            if self.estado_actual == "ESPERANDO_TRANSICION":
                self.procesar_espera_transicion()

            if self.boton_presionado is not None and pygame.time.get_ticks() >= self.tiempo_boton_presionado:
                self.boton_presionado = None

            self.actualizar_musica()
            
            self.dibujar()
            pygame.display.flip()

        if self.video_fondo is not None:
            self.video_fondo.release()

    def actualizar_fondo_menu(self):
        if self.video_fondo is None:
            return

        lectura_correcta, fotograma = self.video_fondo.read()
        if not lectura_correcta:
            self.video_fondo.set(cv2.CAP_PROP_POS_FRAMES, 0)
            lectura_correcta, fotograma = self.video_fondo.read()
        if not lectura_correcta:
            return

        fotograma = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
        fotograma = cv2.resize(fotograma, self.pantalla.get_size())
        self.fondo_menu = pygame.image.frombuffer(
            fotograma.tobytes(), self.pantalla.get_size(), "RGB"
        ).convert()

    def error_debe_penalizar(self):
        if not hasattr(self, "personaje_actual") or self.personaje_actual is None:
            return True

        if getattr(self.personaje_actual, "nombre", "") == "Neru":
            escudo_activo = getattr(self, "bloquear_penalizacion", False) or getattr(self, "primer_error_protegido", False) or getattr(self, "escudo_activo", False)
            if escudo_activo:
                self.bloquear_penalizacion = False
                self.primer_error_protegido = False
                self.escudo_activo = False
                self.personaje_actual.escudo_activo = False
                self.mensaje = "Escudo de Neru activado"
                return False

        return True

    def reproducir_sonido_seleccion_personaje(self):
        if (
            self.sonido_seleccion_personaje is not None
            and not self.sonidos_sistema_silenciados
        ):
            self.sonido_seleccion_personaje.play()

    def manejar_clic(self, pos):
        if self.estado_actual == "MENU":
            if self.rect_boton_settings.collidepoint(pos):
                if self.sonido_settings is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_settings.play()
                self.ventana_settings_abierta = not self.ventana_settings_abierta
                self.ventana_creditos_abierta = False
            elif self.ventana_settings_abierta and self.rect_ajuste_musica.collidepoint(pos):
                self.musica_silenciada = not self.musica_silenciada
                if pygame.mixer.get_init():
                    pygame.mixer.music.set_volume(
                        0.0 if self.musica_silenciada else self.volumen_musica
                    )
            elif self.ventana_settings_abierta and self.rect_ajuste_sistema.collidepoint(pos):
                self.sonidos_sistema_silenciados = not self.sonidos_sistema_silenciados
            elif self.rect_boton_creditos.collidepoint(pos):
                self.tiempo_boton_creditos_presionado = pygame.time.get_ticks() + 150
                if self.sonido_corazon is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_corazon.play()
                self.ventana_creditos_abierta = not self.ventana_creditos_abierta
                self.ventana_settings_abierta = False
            elif self.ventana_settings_abierta:
                self.ventana_settings_abierta = False
            elif self.ventana_creditos_abierta:
                self.ventana_creditos_abierta = False
            elif self.rect_iniciar.collidepoint(pos):
                if self.sonido_iniciar is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_iniciar.play()
                self.estado_actual = "SELECCION"
            
        elif self.estado_actual == "SELECCION":
            if self.rect_miku.collidepoint(pos):
                self.reproducir_sonido_seleccion_personaje()
                self.personaje_actual = Miku()
                self.personaje_hover = None
                self.estado_actual = "CONFIRMACION_PERSONAJE"
            elif self.rect_teto.collidepoint(pos):
                self.reproducir_sonido_seleccion_personaje()
                self.personaje_actual = Teto()
                self.personaje_hover = None
                self.estado_actual = "CONFIRMACION_PERSONAJE"
            elif self.rect_neru.collidepoint(pos):
                self.reproducir_sonido_seleccion_personaje()
                self.personaje_actual = Neru()
                self.personaje_hover = None
                self.estado_actual = "CONFIRMACION_PERSONAJE"
            elif self.rect_gumi.collidepoint(pos):
                self.reproducir_sonido_seleccion_personaje()
                self.personaje_actual = Gumi()
                self.personaje_hover = None
                self.estado_actual = "CONFIRMACION_PERSONAJE"

        elif self.estado_actual == "CONFIRMACION_PERSONAJE":
            if self.rect_continuar.collidepoint(pos):
                self.preparar_juego()

        elif self.estado_actual == "JUGANDO":
            self.personaje_actual.aplicar_habilidad(self)
            
            for numero, rect in self.rects_botones.items():
                if rect.collidepoint(pos):
                    self.boton_presionado = numero
                    self.tiempo_boton_presionado = pygame.time.get_ticks() + 150
                    if numero == 1 and self.sonido_boton_rojo is not None:
                        self.sonido_boton_rojo.play()
                    elif numero == 2 and self.sonido_boton_azul is not None:
                        self.sonido_boton_azul.play()
                    elif numero == 3 and self.sonido_boton_verde is not None:
                        self.sonido_boton_verde.play()
                    elif numero == 4 and self.sonido_boton_amarillo is not None:
                        self.sonido_boton_amarillo.play()
                    resultado = self.gestor_secuencia.verificar_color(numero)
                    if resultado == "ERROR":
                        if self.error_debe_penalizar():
                            self.t_restante -= self.penalizacion_error
                            if self.t_restante <= 0:
                                self.estado_actual = "GAME_OVER"
                            else:
                                self.mensaje = f"¡Error! Repitiendo (-{self.penalizacion_error:g}s)"
                                self.iniciar_animacion()
                        else:
                            self.mensaje = "¡Escudo de Neru!"
                            self.iniciar_animacion()
                    elif resultado == "EXITO":
                        if self.sonido_nivel is not None and not self.sonidos_sistema_silenciados:
                            self.sonido_nivel.play()
                        self.gestor_puntuacion.agregar_por_acierto(
                            self.t_restante, 
                            self.gestor_secuencia.consultar_nivel() - 1, 
                            self.personaje_actual.multiplicador_puntaje
                        )
                        self.mensaje = "¡¡Siguiente nivel!!"
                        self.iniciar_espera_transicion()
                    elif resultado == "CONTINUAR":
                        self.gestor_puntuacion.agregar_por_acierto(
                            self.t_restante,
                            self.gestor_secuencia.consultar_nivel(),
                            self.personaje_actual.multiplicador_puntaje,
                        )
                    break

            if self.rect_reinicio.collidepoint(pos):
                if self.sonido_settings is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_settings.play()
                self.gestor_secuencia.reiniciar_progreso()
                self.estado_actual = "SELECCION"
            elif self.rect_volver.collidepoint(pos):
                if self.sonido_settings is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_settings.play()
                self.gestor_secuencia.reiniciar_progreso()
                self.gestor_puntuacion.reset()
                self.estado_actual = "MENU"

        elif self.estado_actual == "GAME_OVER":
            if self.rect_reinicio.collidepoint(pos):
                if self.sonido_settings is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_settings.play()
                self.gestor_secuencia.reiniciar_progreso()
                self.gestor_puntuacion.reset()
                self.estado_actual = "SELECCION"
            elif self.rect_volver.collidepoint(pos):
                if self.sonido_settings is not None and not self.sonidos_sistema_silenciados:
                    self.sonido_settings.play()
                self.gestor_secuencia.reiniciar_progreso()
                self.gestor_puntuacion.reset()
                self.estado_actual = "MENU"

    def actualizar_personaje_hover(self, pos):
        self.personaje_hover = next(
            (
                nombre
                for rect, nombre in (
                    (self.rect_miku, "Miku"),
                    (self.rect_teto, "Teto"),
                    (self.rect_neru, "Neru"),
                    (self.rect_gumi, "Gumi"),
                )
                if rect.collidepoint(pos)
            ),
            None,
        )

    def dibujar_texto_centrado(self, texto, fuente, color, centro):
        superficie = fuente.render(texto, True, color)
        rect_texto = superficie.get_rect(center=centro)
        self.pantalla.blit(superficie, rect_texto)

    def dibujar_boton(self, rect, texto, color_fondo=(255, 255, 255), color_texto=(0, 0, 0)):
        pygame.draw.rect(self.pantalla, color_fondo, rect)
        pygame.draw.rect(self.pantalla, (0, 0, 0), rect, 2)
        self.dibujar_texto_centrado(texto, self.fuente_normal, color_texto, rect.center)

    def dibujar_personaje(self, rect, nombre):
        if nombre not in ("Neru", "Teto", "Gumi", "Miku"):
            sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(sombra, (0, 0, 0, 75), sombra.get_rect())
            self.pantalla.blit(sombra, rect.move(6, 6))
        if nombre == "Neru":
            self.pantalla.blit(self.fondo_recuadro_neru, rect)
        elif nombre == "Teto":
            self.pantalla.blit(self.fondo_recuadro_teto, rect)
        elif nombre == "Gumi":
            self.pantalla.blit(self.fondo_recuadro_gumi, rect)
        elif nombre == "Miku":
            self.pantalla.blit(self.fondo_recuadro_miku, rect)
        else:
            pygame.draw.rect(self.pantalla, (255, 255, 255), rect)
            pygame.draw.rect(self.pantalla, (0, 0, 0), rect, 2)
        imagenes = self.imagenes_personajes_hover if nombre == self.personaje_hover else self.imagenes_personajes
        imagen = imagenes[nombre]
        self.pantalla.blit(imagen, imagen.get_rect(center=(rect.centerx, rect.top + 95)))
        self.dibujar_texto_centrado(nombre, self.fuente_normal, (0, 0, 0), (rect.centerx, rect.bottom - 28))

    def dibujar_mensaje_ingresar(self, rect, nombre):
        mensajes = {
            "Miku": "Al presionar el botón correcto por primera vez en la secuencia, Miku sumará 3 segundos al contador de tiempo, pudiendo exceder el límite de 10 segundos",
            "Teto": "Al presionar el botón correcto por primera vez en la secuencia, Teto aumentará el multiplicador interno de puntaje x2 veces.",
            "Neru": "Al finalizar la ejecución de la secuencia, Neru generará un escudo que va a exonerar la penalización de tiempo en tu primer error.",
            "Gumi": "Cada que cometas un error en la secuencia, Gumi reducirá la penalización de tiempo a solo 1 segundo.",
            "default": "INGRESAR AQUÍ",
        }
        texto = mensajes.get(nombre, mensajes["default"])
        ancho_mensaje = rect.width
        ancho_texto = ancho_mensaje - 16
        lineas = []
        linea_actual = ""
        for palabra in texto.split():
            linea_prueba = f"{linea_actual} {palabra}".strip()
            if self.fuente_mensaje.size(linea_prueba)[0] <= ancho_texto:
                linea_actual = linea_prueba
            else:
                lineas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas.append(linea_actual)

        alto_mensaje = len(lineas) * 20 + 12
        rect_mensaje = pygame.Rect(0, rect.bottom + 12, ancho_mensaje, alto_mensaje)
        rect_mensaje.centerx = rect.centerx
        sombra = pygame.Surface(rect_mensaje.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 75), sombra.get_rect())
        self.pantalla.blit(sombra, rect_mensaje.move(6, 6))
        pygame.draw.rect(self.pantalla, (255, 255, 255), rect_mensaje)
        pygame.draw.rect(self.pantalla, (0, 0, 0), rect_mensaje, 2)
        for indice, linea in enumerate(lineas):
            self.dibujar_texto_centrado(
                linea,
                self.fuente_mensaje,
                (0, 0, 0),
                (rect_mensaje.centerx, rect_mensaje.top + 10 + indice * 20),
            )

    def dibujar_ventana_creditos(self):
        rect_ventana = pygame.Rect(0, 0, 430, 300)
        rect_ventana.center = self.pantalla.get_rect().center
        ventana = pygame.Surface(rect_ventana.size, pygame.SRCALPHA)
        ventana.fill((0, 0, 0, 190))
        self.pantalla.blit(ventana, rect_ventana)
        lineas = (
            "Elaborado por:",
            "",
            "Luis Cardona",
            "",
            "Natalia Chacón",
            "",
            "Génesis Cova",
            "",
            "Javier García",
        )
        alto_linea = 28
        inicio_y = rect_ventana.centery - (len(lineas) - 1) * alto_linea // 2
        for indice, linea in enumerate(lineas):
            if linea:
                self.dibujar_texto_centrado(
                    linea,
                    self.fuente_normal,
                    (255, 255, 255),
                    (rect_ventana.centerx, inicio_y + indice * alto_linea),
                )

    def dibujar_ventana_settings(self):
        rect_ventana = pygame.Rect(0, 0, 430, 220)
        rect_ventana.center = self.pantalla.get_rect().center
        ventana = pygame.Surface(rect_ventana.size, pygame.SRCALPHA)
        ventana.fill((0, 0, 0, 190))
        self.pantalla.blit(ventana, rect_ventana)
        self.dibujar_texto_centrado(
            "AJUSTES",
            self.fuente_titulo,
            (255, 255, 255),
            (rect_ventana.centerx, rect_ventana.top + 65),
        )
        texto_musica = "MÚSICA: SILENCIADA" if self.musica_silenciada else "MÚSICA: ACTIVADA"
        texto_sistema = (
            "SONIDOS SISTEMA: SILENCIADOS"
            if self.sonidos_sistema_silenciados
            else "SONIDOS SISTEMA: ACTIVADOS"
        )
        self.dibujar_boton(self.rect_ajuste_musica, texto_musica, (255, 255, 255), (0, 0, 0))
        self.dibujar_boton(self.rect_ajuste_sistema, texto_sistema, (255, 255, 255), (0, 0, 0))

    def dibujar_texto_lateral(self, texto, fuente, color, y, lado):
        superficie = fuente.render(texto, True, color)
        if lado == "izquierda":
            rect_texto = superficie.get_rect(topleft=(30, y))
        else:
            rect_texto = superficie.get_rect(topright=(self.pantalla.get_rect().right - 53, y))
        self.pantalla.blit(superficie, rect_texto)

    def crear_estrellita(self, tamano):
        superficie = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
        centro = tamano / 2
        puntos = []
        for indice in range(10):
            angulo = math.radians(-90 + indice * 36)
            radio = tamano * (0.48 if indice % 2 == 0 else 0.21)
            puntos.append((centro + math.cos(angulo) * radio, centro + math.sin(angulo) * radio))
        pygame.draw.polygon(superficie, (255, 255, 255, 255), puntos)
        return superficie

    def dibujar_estrellita(self):
        centro_estrellita = (
            self.pantalla.get_rect().centerx,
            self.pantalla.get_rect().centery,
        )
        rect_estrella = self.estrellita.get_rect(center=centro_estrellita)
        self.pantalla.blit(self.estrellita, rect_estrella)

    def dibujar_personaje_jugando(self):
        if self.personaje_actual is None:
            return

        imagen = self.imagenes_personajes[self.personaje_actual.nombre]
        imagen = pygame.transform.smoothscale(imagen, (144, 144))
        tiempo_pulso = 1000 / self.pulsos_por_segundo_personaje
        indice_pulso = int(pygame.time.get_ticks() / tiempo_pulso)
        angulos_animacion = (45, 0, -45, 0)
        angulo = angulos_animacion[indice_pulso % len(angulos_animacion)]
        imagen_inclinada = pygame.transform.rotate(imagen, angulo)
        rect_imagen = imagen_inclinada.get_rect(center=(85, 190))
        self.pantalla.blit(imagen_inclinada, rect_imagen)

    def dibujar_barra_tiempo(self):
        tiempo_total = max(0.0, float(self.t_total))
        tiempo_restante = max(0.0, float(self.t_restante))
        progreso = min(1.0, tiempo_restante / tiempo_total) if tiempo_total else 0.0
        habilidad_activa = (
            self.personaje_actual is not None
            and self.personaje_actual.habilidad_aplicada
        )
        nombre_marco = (
            self.personaje_actual.nombre
            if habilidad_activa
            else "generico"
        )
        rect_marco = self.rect_barra_tiempo
        rect_relleno = rect_marco.inflate(-16, -6)
        rect_relleno.width = round(rect_relleno.width * progreso)
        colores_barras_personajes = {
            "Miku": (53, 186, 199),
            "Teto": (228, 18, 53),
            "Neru": (255, 243, 156),
            "Gumi": (128, 234, 121),
        }
        color_relleno = (
            colores_barras_personajes[self.personaje_actual.nombre]
            if habilidad_activa
            else (53, 186, 199)
        )
        pygame.draw.rect(self.pantalla, color_relleno, rect_relleno)
        self.pantalla.blit(self.marcos_barra_tiempo[nombre_marco], rect_marco)

    def dibujar_transicion_nivel(self):
        tiempo_transcurrido = (pygame.time.get_ticks() - self.tiempo_transicion_nivel) / 1000
        panel = pygame.Surface((460, 190), pygame.SRCALPHA)
        panel.fill((20, 20, 20, 230))
        rect_panel = panel.get_rect(center=self.pantalla.get_rect().center)
        self.pantalla.blit(panel, rect_panel)

        if tiempo_transcurrido < 1:
            texto = "¡¡Siguiente nivel!!"
            fuente = self.fuente_normal
        elif tiempo_transcurrido < 2.5:
            texto = str(3 - int((tiempo_transcurrido - 1) / 0.5))
            fuente = self.fuente_titulo
        else:
            texto = "¡¡VAMOS!!"
            fuente = self.fuente_titulo

        self.dibujar_texto_centrado(texto, fuente, (255, 255, 255), rect_panel.center)

    def dibujar_intro(self):
        self.pantalla.fill((0, 0, 0))
        tiempo_transcurrido = (pygame.time.get_ticks() - self.tiempo_inicio_intro) / 1000.0

        if tiempo_transcurrido < 1.0:
            self.pantalla.blit(self.logo_intro, self.rect_logo_intro)
            return

        duracion_fade = 0.25
        if tiempo_transcurrido < 1.0 + duracion_fade:
            self.pantalla.blit(self.logo_intro, self.rect_logo_intro)
            progreso_fade = (tiempo_transcurrido - 1.0) / duracion_fade
            capa_negra = pygame.Surface(self.pantalla.get_size(), pygame.SRCALPHA)
            capa_negra.fill((0, 0, 0, round(255 * progreso_fade)))
            self.pantalla.blit(capa_negra, (0, 0))
            return

        self.estado_actual = "MENU"
        self.tiempo_inicio_intro = pygame.time.get_ticks()

    def dibujar(self):
        if self.estado_actual == "INTRO":
            self.dibujar_intro()
            return

        self.pantalla.fill((0, 0, 0))
        
        if self.estado_actual in ["MOSTRANDO_SECUENCIA", "JUGANDO", "TRANSICION_NIVEL", "ESPERANDO_TRANSICION", "GAME_OVER"]:
            self.pantalla.blit(self.fondo_juego, (0, 0))
        
        if self.estado_actual == "MENU":
            self.actualizar_fondo_menu()
            self.pantalla.blit(self.fondo_menu, (0, 0))
            self.pantalla.blit(self.marco_menu, (0, 0))
            centro_x = self.pantalla.get_rect().centerx
            centro_y = self.pantalla.get_rect().centery
            self.pantalla.blit(self.logo_inicio, self.rect_logo_inicio)
            self.dibujar_boton(self.rect_iniciar, "Haz clic para iniciar", (255, 255, 255), (50, 50, 50))
            rect_creditos = self.rect_boton_creditos
            self.pantalla.blit(self.boton_creditos, rect_creditos)
            self.pantalla.blit(self.boton_settings, self.rect_boton_settings)
            if self.ventana_settings_abierta:
                self.dibujar_ventana_settings()
            if self.ventana_creditos_abierta:
                self.dibujar_ventana_creditos()
            
        elif self.estado_actual == "SELECCION":
            self.pantalla.blit(self.fondo_seleccion, (0, 0))
            centro_x = self.pantalla.get_rect().centerx
            centro_y = self.pantalla.get_rect().centery
            self.actualizar_personaje_hover(pygame.mouse.get_pos())
            self.dibujar_texto_centrado("ELEGIR PERSONAJE", self.fuente_titulo, (0, 0, 0), (centro_x, 93))
            personajes = (
                (self.rect_miku, "Miku"),
                (self.rect_teto, "Teto"),
                (self.rect_neru, "Neru"),
                (self.rect_gumi, "Gumi"),
            )
            for rect, nombre in personajes:
                self.dibujar_personaje(rect, nombre)
                if nombre == self.personaje_hover:
                    self.dibujar_mensaje_ingresar(rect, nombre)
            if self.gestor_puntuacion.total > 0 and self.personaje_hover is None:
                limite_inferior_botones = max(
                    rect.bottom for rect in (self.rect_miku, self.rect_teto, self.rect_neru, self.rect_gumi)
                )
                self.dibujar_texto_centrado(
                    f"Último Puntaje: {self.gestor_puntuacion.total}",
                    self.fuente_normal,
                    (0, 0, 0),
                    (centro_x, limite_inferior_botones + 79),
                )

        elif self.estado_actual == "CONFIRMACION_PERSONAJE":
            self.pantalla.blit(self.fondo_seleccion, (0, 0))
            centro_x = self.pantalla.get_rect().centerx
            self.dibujar_texto_centrado(
                "PERSONAJE SELECCIONADO",
                self.fuente_titulo,
                (0, 0, 0),
                (centro_x, 93),
            )
            self.personaje_hover = None
            self.dibujar_personaje(
                self.rect_personaje_confirmacion,
                self.personaje_actual.nombre,
            )
            self.dibujar_boton(
                self.rect_continuar,
                "CONTINUAR",
                (255, 255, 255),
                (50, 50, 50),
            )

        elif self.estado_actual in ["MOSTRANDO_SECUENCIA", "JUGANDO"]:
            centro_rueda = (
                self.pantalla.get_rect().centerx,
                self.rects_botones[3].top + self.rects_botones[3].height,
            )
            rect_circulo_extra = self.circulo_extra.get_rect(
                topleft=(
                    round(centro_rueda[0] - 961.5 * self.escala_circulo_extra),
                    round(centro_rueda[1] - 539.5 * self.escala_circulo_extra),
                )
            )
            self.pantalla.blit(self.circulo_extra, rect_circulo_extra)
            self.dibujar_texto_lateral(
                f"Puntaje: {self.gestor_puntuacion.total}",
                self.fuente_normal,
                (0, 0, 0),
                30,
                "izquierda",
            )
            self.dibujar_texto_centrado(
                f"Tiempo: {max(0, self.t_restante):.1f}s",
                self.fuente_normal,
                (0, 0, 0),
                (self.rect_barra_tiempo.centerx, self.rect_barra_tiempo.top - 35),
            )
            self.dibujar_texto_lateral(self.mensaje, self.fuente_normal, (0, 100, 0), 30, "derecha")
            for numero, rect in self.rects_botones.items():
                esta_presionado = (
                    self.color_iluminado == numero
                    or self.boton_presionado == numero
                )
                tipo_imagen = "presionado" if esta_presionado else "normal"
                self.pantalla.blit(self.imagenes_botones[numero][tipo_imagen], rect)
            self.dibujar_estrellita()
            self.dibujar_barra_tiempo()
            if self.estado_actual == "JUGANDO":
                self.dibujar_personaje_jugando()

            pygame.draw.rect(self.pantalla, (0,0,0), self.rect_reinicio)
            self.dibujar_texto_centrado("REINICIAR", self.fuente_normal, (255, 255, 255), self.rect_reinicio.center)
            pygame.draw.rect(self.pantalla, (0,0,0), self.rect_volver)
            self.dibujar_texto_centrado("VOLVER", self.fuente_normal, (255, 255, 255), self.rect_volver.center)

        elif self.estado_actual == "TRANSICION_NIVEL":
            centro_rueda = (
                self.pantalla.get_rect().centerx,
                self.rects_botones[3].top + self.rects_botones[3].height,
            )
            rect_circulo_extra = self.circulo_extra.get_rect(
                topleft=(
                    round(centro_rueda[0] - 961.5 * self.escala_circulo_extra),
                    round(centro_rueda[1] - 539.5 * self.escala_circulo_extra),
                )
            )
            self.pantalla.blit(self.circulo_extra, rect_circulo_extra)
            
            for numero, rect in self.rects_botones.items():
                tipo_imagen = "presionado" if self.color_iluminado == numero else "normal"
                self.pantalla.blit(self.imagenes_botones[numero][tipo_imagen], rect)
            self.dibujar_estrellita()
            self.dibujar_transicion_nivel()

        elif self.estado_actual == "ESPERANDO_TRANSICION":
            centro_rueda = (
                self.pantalla.get_rect().centerx,
                self.rects_botones[3].top + self.rects_botones[3].height,
            )
            rect_circulo_extra = self.circulo_extra.get_rect(
                topleft=(
                    round(centro_rueda[0] - 961.5 * self.escala_circulo_extra),
                    round(centro_rueda[1] - 539.5 * self.escala_circulo_extra),
                )
            )
            self.pantalla.blit(self.circulo_extra, rect_circulo_extra)
            
            for numero, rect in self.rects_botones.items():
                tipo_imagen = "presionado" if self.boton_presionado == numero else "normal"
                self.pantalla.blit(self.imagenes_botones[numero][tipo_imagen], rect)
            self.dibujar_estrellita()

        elif self.estado_actual == "GAME_OVER":
            centro_x = self.pantalla.get_rect().centerx
            self.dibujar_texto_centrado("GAME OVER", self.fuente_titulo, (200, 0, 0), (centro_x, 200))
            self.dibujar_texto_lateral(
                f"Puntaje Final: {self.gestor_puntuacion.total}",
                self.fuente_normal,
                (0, 0, 0),
                300,
                "derecha",
            )
            pygame.draw.rect(self.pantalla, (0,0,0), self.rect_reinicio)
            self.dibujar_texto_centrado("REINICIAR", self.fuente_normal, (255, 255, 255), self.rect_reinicio.center)
            pygame.draw.rect(self.pantalla, (0,0,0), self.rect_volver)
            self.dibujar_texto_centrado("VOLVER", self.fuente_normal, (255, 255, 255), self.rect_volver.center)
