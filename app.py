import pygame
try:
    import cv2
except ImportError:
    cv2 = None
from funtions import GestorSecuencia, GestorPuntuacion
from personajes import Miku, Teto, Neru, Gumi

from vistas import VistasJuego
from cargador import CargadorRecursos

class App(VistasJuego, CargadorRecursos):
    def __init__(self, config):
        self.config = config
        self.pantalla = pygame.display.set_mode((config.ancho_pantalla, config.alto_pantalla))
        pygame.display.set_caption(config.titulo)
        self.reloj = pygame.time.Clock()
        self.fps_objetivo = config.fps
        self.ejecutando = True

        self.gestor_puntuacion = GestorPuntuacion()
        self.gestor_secuencia = GestorSecuencia(config.archivo_niveles)
        self.personaje_actual = None
        self.penalizacion_error = 2.0

        self.inicializar_recursos()

        self.estado_actual = "INTRO" 
        self.tiempo_inicio_intro = pygame.time.get_ticks()
        
        self.t_total = 10.0; self.t_restante = 10.0
        self.mensaje = ""; self.texto_nivel = ""
        
        self.color_iluminado = None
        self.indice_secuencia = 0
        self.tiempo_ultimo_cambio = 0
        self.luz_encendida = False
        self.boton_presionado = None
        self.tiempo_boton_presionado = 0
        self.volver_presionado = 0; self.reinicio_presionado = 0
        self.iniciar_presionado = 0; self.continuar_presionado = 0
        self.tiempo_espera_transicion = 0; self.tiempo_transicion_nivel = 0
        self.pulsos_por_segundo_personaje = 180 / 60

    def _reproducir_sonido(self, clave):
        if not self.sonidos_sistema_silenciados and clave in self.sonidos:
            self.sonidos[clave].play()

    def preparar_juego(self):
        self.gestor_secuencia.iniciar_juego()
        self.personaje_actual.reiniciar_habilidad()
        self.penalizacion_error = self.personaje_actual.penalizacion_error
        self.t_total = 10.0; self.t_restante = 10.0
        self.texto_nivel = f"Nivel {self.gestor_secuencia.consultar_nivel()}"
        self.mensaje = ""; self.iniciar_animacion()

    def saltar_nivel(self):
        if self.personaje_actual:
            self.gestor_secuencia.avanzar_nivel(); self.preparar_juego()

    def actualizar_musica(self):
        if not self.musica_reproduciendose or not pygame.mixer.get_init(): return
        de_menu = self.estado_actual in ("INTRO", "MENU", "SELECCION", "CONFIRMACION_PERSONAJE", "GAME_OVER")
        if de_menu and not pygame.mixer.music.get_busy(): pygame.mixer.music.unpause()
        elif not de_menu and pygame.mixer.music.get_busy(): pygame.mixer.music.pause()

    def iniciar_animacion(self):
        self.estado_actual = "MOSTRANDO_SECUENCIA"
        self.indice_secuencia = 0; self.color_iluminado = None
        self.luz_encendida = False; self.tiempo_ultimo_cambio = pygame.time.get_ticks()

    def iniciar_transicion_nivel(self):
        self.estado_actual = "TRANSICION_NIVEL"
        self.tiempo_transicion_nivel = pygame.time.get_ticks()

    def iniciar_espera_transicion(self):
        self.estado_actual = "ESPERANDO_TRANSICION"
        self.tiempo_espera_transicion = pygame.time.get_ticks() + self.config.tiempos["espera_transicion"]

    def procesar_espera_transicion(self):
        if pygame.time.get_ticks() >= self.tiempo_espera_transicion: self.iniciar_transicion_nivel()

    def procesar_transicion_nivel(self):
        if (pygame.time.get_ticks() - self.tiempo_transicion_nivel) / 1000 >= self.config.tiempos["transicion_nivel"]:
            self.preparar_juego()

    def procesar_animacion(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_cambio > self.config.tiempos["animacion_luces"]: 
            self.tiempo_ultimo_cambio = ahora
            if not self.luz_encendida:
                if self.indice_secuencia < len(self.gestor_secuencia.colores_secuencia):
                    self.color_iluminado = self.gestor_secuencia.colores_secuencia[self.indice_secuencia]
                    self._reproducir_sonido(self.color_iluminado)
                    self.luz_encendida = True
                else:
                    self.color_iluminado = None; self.estado_actual = "JUGANDO"
            else:
                self.color_iluminado = None; self.luz_encendida = False; self.indice_secuencia += 1

    def ejecutar(self):
        while self.ejecutando:
            dt = self.reloj.tick(self.fps_objetivo) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    self.gestor_secuencia.reiniciar_progreso()
                    self.ejecutando = False
                    break
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.rect_volver.collidepoint(ev.pos): self.volver_presionado = pygame.time.get_ticks()
                    if self.rect_reinicio.collidepoint(ev.pos): self.reinicio_presionado = pygame.time.get_ticks()
                    if self.estado_actual == "MENU" and self.rect_iniciar.collidepoint(ev.pos): self.iniciar_presionado = pygame.time.get_ticks()
                    if self.estado_actual == "CONFIRMACION_PERSONAJE" and self.rect_continuar.collidepoint(ev.pos): self.continuar_presionado = pygame.time.get_ticks()
                    self.manejar_clic(ev.pos)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_j and self.estado_actual in ("MOSTRANDO_SECUENCIA", "JUGANDO", "TRANSICION_NIVEL", "ESPERANDO_TRANSICION"):
                    self.saltar_nivel()
                if ev.type == pygame.MOUSEMOTION and self.estado_actual == "SELECCION":
                    self.actualizar_personaje_hover(ev.pos)

            if self.estado_actual == "JUGANDO":
                self.t_restante -= dt
                if self.t_restante <= 0: self.t_restante = 0; self.estado_actual = "GAME_OVER"

            if self.estado_actual == "MOSTRANDO_SECUENCIA": self.procesar_animacion()
            if self.estado_actual == "TRANSICION_NIVEL": self.procesar_transicion_nivel()
            if self.estado_actual == "ESPERANDO_TRANSICION": self.procesar_espera_transicion()

            ahora = pygame.time.get_ticks(); delay = self.config.tiempos["click_delay"]
            if self.boton_presionado and ahora >= self.tiempo_boton_presionado: self.boton_presionado = None
            if self.iniciar_presionado and ahora >= self.iniciar_presionado + delay: self.iniciar_presionado = 0; self.estado_actual = "SELECCION"
            if self.continuar_presionado and ahora >= self.continuar_presionado + delay: self.continuar_presionado = 0; self.preparar_juego()
            
            if self.volver_presionado and ahora >= self.volver_presionado + delay:
                self.gestor_secuencia.reiniciar_progreso(); self.gestor_puntuacion.reset()
                self.volver_presionado = 0; self.estado_actual = "MENU"
            if self.reinicio_presionado and ahora >= self.reinicio_presionado + delay:
                self.gestor_secuencia.reiniciar_progreso(); self.gestor_puntuacion.reset()
                self.reinicio_presionado = 0; self.estado_actual = "SELECCION"

            self.actualizar_musica(); self.dibujar(); pygame.display.flip()

        if self.video_fondo: self.video_fondo.release()

    def error_debe_penalizar(self):
        if getattr(self.personaje_actual, "nombre", "") == "Neru":
            esc = getattr(self, "bloquear_penalizacion", False) or getattr(self, "primer_error_protegido", False) or getattr(self, "escudo_activo", False)
            if esc:
                self.bloquear_penalizacion = self.primer_error_protegido = self.escudo_activo = self.personaje_actual.escudo_activo = False
                self.mensaje = "Escudo de Neru activado"; return False
        return True

    def manejar_clic(self, pos):
        if self.estado_actual == "MENU":
            if self.rect_boton_settings.collidepoint(pos):
                self._reproducir_sonido("settings")
                self.ventana_settings_abierta = not self.ventana_settings_abierta; self.ventana_creditos_abierta = False
            elif self.ventana_settings_abierta and self.rect_ajuste_musica.collidepoint(pos):
                self.musica_silenciada = not self.musica_silenciada
                if pygame.mixer.get_init(): pygame.mixer.music.set_volume(0.0 if self.musica_silenciada else self.config.volumen_musica_base)
            elif self.ventana_settings_abierta and self.rect_ajuste_sistema.collidepoint(pos):
                self.sonidos_sistema_silenciados = not self.sonidos_sistema_silenciados
            elif self.rect_boton_creditos.collidepoint(pos):
                self._reproducir_sonido("corazon")
                self.ventana_creditos_abierta = not self.ventana_creditos_abierta; self.ventana_settings_abierta = False
            elif self.ventana_settings_abierta or self.ventana_creditos_abierta:
                self.ventana_settings_abierta = self.ventana_creditos_abierta = False
            elif self.rect_iniciar.collidepoint(pos): self._reproducir_sonido("iniciar")
            
        elif self.estado_actual == "SELECCION":
            for nom, rect in self.rect_pj.items():
                if rect.collidepoint(pos):
                    self._reproducir_sonido("seleccion")
                    clases = {"Miku": Miku, "Teto": Teto, "Neru": Neru, "Gumi": Gumi}
                    self.personaje_actual = clases[nom]()
                    self.personaje_hover = None; self.estado_actual = "CONFIRMACION_PERSONAJE"
                    break

        elif self.estado_actual == "CONFIRMACION_PERSONAJE":
            if self.rect_continuar.collidepoint(pos): self._reproducir_sonido("uno")

        elif self.estado_actual == "JUGANDO":
            self.personaje_actual.aplicar_habilidad(self)
            for num, rect in self.rects_botones.items():
                if rect.collidepoint(pos):
                    self.boton_presionado = num
                    self.tiempo_boton_presionado = pygame.time.get_ticks() + self.config.tiempos["boton_presionado"]
                    self._reproducir_sonido(num)
                    
                    resultado = self.gestor_secuencia.verificar_color(num)
                    if resultado == "ERROR":
                        self._reproducir_sonido("error")
                        if self.error_debe_penalizar():
                            self.t_restante -= self.penalizacion_error
                            if self.t_restante <= 0: self.estado_actual = "GAME_OVER"
                            else: self.mensaje = f"¡Error! Repitiendo (-{self.penalizacion_error:g}s)"; self.iniciar_animacion()
                        else: self.mensaje = "¡Escudo de Neru!"; self.iniciar_animacion()
                    elif resultado == "EXITO":
                        self._reproducir_sonido("nivel")
                        self.gestor_puntuacion.agregar_por_acierto(self.t_restante, self.gestor_secuencia.consultar_nivel() - 1, self.personaje_actual.multiplicador_puntaje)
                        self.mensaje = "¡¡Siguiente nivel!!"; self.iniciar_espera_transicion()
                    elif resultado == "CONTINUAR":
                        self.gestor_puntuacion.agregar_por_acierto(self.t_restante, self.gestor_secuencia.consultar_nivel(), self.personaje_actual.multiplicador_puntaje)
                    break
            if self.rect_reinicio.collidepoint(pos) or self.rect_volver.collidepoint(pos): self._reproducir_sonido("settings")

        elif self.estado_actual == "GAME_OVER":
            if self.rect_reinicio.collidepoint(pos) or self.rect_volver.collidepoint(pos): self._reproducir_sonido("settings")

    def actualizar_personaje_hover(self, pos):
        self.personaje_hover = next((nom for nom, rect in self.rect_pj.items() if rect.collidepoint(pos)), None)
