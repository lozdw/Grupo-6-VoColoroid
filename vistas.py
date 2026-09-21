import pygame
import math
try:
    import cv2
except ImportError:
    cv2 = None

class VistasJuego:
    def actualizar_fondo_menu(self):
        if not self.video_fondo: return
        ret, frame = self.video_fondo.read()
        if not ret:
            self.video_fondo.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_fondo.read()
        if not ret: return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, self.pantalla.get_size())
        self.fondo_menu = pygame.image.frombuffer(frame.tobytes(), self.pantalla.get_size(), "RGB").convert()

    def dibujar_texto_centrado(self, texto, fuente, color, centro):
        surf = fuente.render(texto, True, color)
        self.pantalla.blit(surf, surf.get_rect(center=centro))

    def dibujar_personaje(self, rect, nombre):
        colores = self.config.colores
        sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra, colores["sombra"], sombra.get_rect())
        self.pantalla.blit(sombra, rect.move(6, 6))
        
        if nombre not in self.fondos_recuadro:
            pygame.draw.rect(self.pantalla, colores["blanco"], rect)
            pygame.draw.rect(self.pantalla, colores["negro"], rect, 2)
        else:
            self.pantalla.blit(self.fondos_recuadro[nombre], rect)
            
        img = self.img_pj_hover[nombre] if nombre == self.personaje_hover else self.img_pj[nombre]
        self.pantalla.blit(img, img.get_rect(center=(rect.centerx, rect.top + 95)))
        self.dibujar_texto_centrado(nombre, self.fuente_normal, colores["negro"], (rect.centerx, rect.bottom - 28))

    def dibujar_mensaje_ingresar(self, rect, nombre):
        texto = self.config.mensajes.get(nombre, self.config.mensajes["default"])
        ancho_texto = rect.width - 16
        lineas, linea_actual = [], ""
        for pal in texto.split():
            prueba = f"{linea_actual} {pal}".strip()
            if self.fuente_mensaje.size(prueba)[0] <= ancho_texto: linea_actual = prueba
            else: lineas.append(linea_actual); linea_actual = pal
        if linea_actual: lineas.append(linea_actual)

        alto = len(lineas) * 20 + 12
        rm = pygame.Rect(0, rect.bottom + 12, rect.width, alto)
        rm.centerx = rect.centerx
        sombra = pygame.Surface(rm.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra, self.config.colores["sombra"], sombra.get_rect())
        self.pantalla.blit(sombra, rm.move(6, 6))
        pygame.draw.rect(self.pantalla, self.config.colores["blanco"], rm)
        pygame.draw.rect(self.pantalla, self.config.colores["negro"], rm, 2)
        for i, l in enumerate(lineas):
            self.dibujar_texto_centrado(l, self.fuente_mensaje, self.config.colores["negro"], (rm.centerx, rm.top + 10 + i * 20))

    def dibujar_ventana_creditos(self):
        rect = pygame.Rect(0, 0, 430, 300); rect.center = self.pantalla.get_rect().center
        ven = pygame.Surface(rect.size, pygame.SRCALPHA); ven.fill(self.config.colores["ventana"])
        self.pantalla.blit(ven, rect)
        inicio_y = rect.centery - (len(self.config.creditos) - 1) * 28 // 2
        for i, linea in enumerate(self.config.creditos):
            if linea: self.dibujar_texto_centrado(linea, self.fuente_normal, self.config.colores["blanco"], (rect.centerx, inicio_y + i * 28))

    def dibujar_ventana_settings(self):
        rect = pygame.Rect(0, 0, 350, 220); rect.center = self.pantalla.get_rect().center
        ven = pygame.Surface(rect.size, pygame.SRCALPHA); ven.fill(self.config.colores["ventana"])
        self.pantalla.blit(ven, rect)
        blanco = self.config.colores["blanco"]
        self.dibujar_texto_centrado("AJUSTES", self.fuente_titulo, blanco, (rect.centerx, rect.top + 50))
        self.dibujar_texto_centrado("Música", self.fuente_normal, blanco, (self.rect_ajuste_musica.centerx, self.rect_ajuste_musica.top - 22))
        self.dibujar_texto_centrado("Sonidos", self.fuente_normal, blanco, (self.rect_ajuste_sistema.centerx, self.rect_ajuste_sistema.top - 22))
        self.pantalla.blit(self.imagen_silencio_on if self.musica_silenciada else self.imagen_silencio_off, self.rect_ajuste_musica)
        self.pantalla.blit(self.imagen_silencio_on if self.sonidos_sistema_silenciados else self.imagen_silencio_off, self.rect_ajuste_sistema)

    def dibujar_texto_lateral(self, texto, fuente, color, y, lado):
        surf = fuente.render(texto, True, color)
        rect = surf.get_rect(topleft=(30, y)) if lado == "izquierda" else surf.get_rect(topright=(self.pantalla.get_rect().right - 53, y))
        self.pantalla.blit(surf, rect)

    def crear_estrellita(self, tamano):
        surf = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
        c = tamano / 2
        puntos = [(c + math.cos(math.radians(-90 + i * 36)) * (tamano * (0.48 if i % 2 == 0 else 0.21)), 
                   c + math.sin(math.radians(-90 + i * 36)) * (tamano * (0.48 if i % 2 == 0 else 0.21))) for i in range(10)]
        pygame.draw.polygon(surf, (255, 255, 255, 255), puntos)
        return surf

    def dibujar_estrellita(self):
        self.pantalla.blit(self.estrellita, self.estrellita.get_rect(center=self.pantalla.get_rect().center))

    def dibujar_personaje_jugando(self):
        if not self.personaje_actual: return
        img = pygame.transform.smoothscale(self.img_pj[self.personaje_actual.nombre], (144, 144))
        indice = int(pygame.time.get_ticks() / (1000 / self.pulsos_por_segundo_personaje))
        angulos = (45, 0, -45, 0)
        img_rot = pygame.transform.rotate(img, angulos[indice % 4])
        self.pantalla.blit(img_rot, img_rot.get_rect(center=(145, 190)))

    def dibujar_barra_tiempo(self):
        tt, tr = max(0.0, float(self.t_total)), max(0.0, float(self.t_restante))
        prog = min(1.0, tr / tt) if tt else 0.0
        hab_activa = self.personaje_actual and self.personaje_actual.habilidad_aplicada
        nom_marco = self.personaje_actual.nombre if hab_activa else "generico"
        relleno = self.rect_barra_tiempo.inflate(-16, -6)
        relleno.width = round(relleno.width * prog)
        color = self.config.colores_barras[self.personaje_actual.nombre] if hab_activa else self.config.colores_barras["generico"]
        pygame.draw.rect(self.pantalla, color, relleno)
        self.pantalla.blit(self.marcos_barra_tiempo[nom_marco], self.rect_barra_tiempo)

    def dibujar_transicion_nivel(self):
        t = (pygame.time.get_ticks() - self.tiempo_transicion_nivel) / 1000
        panel = pygame.Surface((460, 190), pygame.SRCALPHA); panel.fill(self.config.colores["fondo_panel"])
        rp = panel.get_rect(center=self.pantalla.get_rect().center)
        self.pantalla.blit(panel, rp)
        if t < 1: txt, fnt = "¡¡Siguiente nivel!!", self.fuente_normal
        elif t < 2.5: txt, fnt = str(3 - int((t - 1) / 0.5)), self.fuente_titulo
        else: txt, fnt = "¡¡VAMOS!!", self.fuente_titulo
        self.dibujar_texto_centrado(txt, fnt, self.config.colores["blanco"], rp.center)

    def dibujar_intro(self):
        self.pantalla.fill(self.config.colores["negro"])
        t = (pygame.time.get_ticks() - self.tiempo_inicio_intro) / 1000.0
        if t < self.config.tiempos["intro_total"]: self.pantalla.blit(self.logo_intro, self.rect_logo_intro); return
        
        fade = self.config.tiempos["intro_fade"]
        if t < self.config.tiempos["intro_total"] + fade:
            self.pantalla.blit(self.logo_intro, self.rect_logo_intro)
            prog = (t - self.config.tiempos["intro_total"]) / fade
            capa = pygame.Surface(self.pantalla.get_size(), pygame.SRCALPHA)
            capa.fill((0, 0, 0, round(255 * prog)))
            self.pantalla.blit(capa, (0, 0))
            return
        self.estado_actual, self.tiempo_inicio_intro = "MENU", pygame.time.get_ticks()

    def _dibujar_botones_laterales(self):
        blanco = self.config.colores["blanco"]
        self.pantalla.blit(self.botones_ui["reinicio"][1 if self.reinicio_presionado else 0], self.rect_reinicio)
        self.dibujar_texto_centrado("REINICIAR", self.fuente_normal, blanco, self.rect_reinicio.center)
        self.pantalla.blit(self.botones_ui["volver"][1 if self.volver_presionado else 0], self.rect_volver)
        self.dibujar_texto_centrado("VOLVER", self.fuente_normal, blanco, self.rect_volver.center)

    def dibujar(self):
        colores = self.config.colores
        if self.estado_actual == "INTRO": self.dibujar_intro(); return
        self.pantalla.fill(colores["negro"])
        if self.estado_actual in ["MOSTRANDO_SECUENCIA", "JUGANDO", "TRANSICION_NIVEL", "ESPERANDO_TRANSICION", "GAME_OVER"]:
            self.pantalla.blit(self.fondo_juego, (0, 0))
        
        cx = self.pantalla.get_rect().centerx
        if self.estado_actual == "MENU":
            self.actualizar_fondo_menu()
            self.pantalla.blit(self.fondo_menu, (0, 0)); self.pantalla.blit(self.marco_menu, (0, 0))
            self.pantalla.blit(self.logo_inicio, self.rect_logo_inicio)
            self.pantalla.blit(self.botones_ui["iniciar"][1 if self.iniciar_presionado else 0], self.rect_iniciar)
            self.dibujar_texto_centrado("Haz click para iniciar", self.fuente_normal, colores["blanco"], self.rect_iniciar.center)
            self.pantalla.blit(self.boton_creditos, self.rect_boton_creditos)
            self.pantalla.blit(self.boton_settings, self.rect_boton_settings)
            if self.ventana_settings_abierta: self.dibujar_ventana_settings()
            if self.ventana_creditos_abierta: self.dibujar_ventana_creditos()
            
        elif self.estado_actual == "SELECCION":
            self.pantalla.blit(self.fondo_seleccion, (0, 0))
            self.actualizar_personaje_hover(pygame.mouse.get_pos())
            self.dibujar_texto_centrado("ELEGIR PERSONAJE", self.fuente_titulo, colores["negro"], (cx, 93))
            for nom, rect in self.rect_pj.items():
                self.dibujar_personaje(rect, nom)
                if nom == self.personaje_hover: self.dibujar_mensaje_ingresar(rect, nom)
            if self.gestor_puntuacion.total > 0 and not self.personaje_hover:
                self.dibujar_texto_centrado(f"Último Puntaje: {self.gestor_puntuacion.total}", self.fuente_normal, colores["negro"], (cx, max(r.bottom for r in self.rect_pj.values()) + 79))
                
        elif self.estado_actual == "CONFIRMACION_PERSONAJE":
            self.pantalla.blit(self.fondo_seleccion, (0, 0))
            self.dibujar_texto_centrado("¿Cómo Jugar?", self.fuente_titulo, colores["negro"], (cx, 93))
            self.personaje_hover = None
            self.dibujar_personaje(self.rect_pj_confirmacion, self.personaje_actual.nombre)
            y_txt = 180
            for linea in self.config.instrucciones:
                self.dibujar_texto_centrado(linea, self.fuente_normal, colores["negro"], (cx + 150, y_txt)); y_txt += 35
            self.pantalla.blit(self.botones_ui["iniciar"][1 if self.continuar_presionado else 0], self.rect_continuar)
            self.dibujar_texto_centrado("CONTINUAR", self.fuente_normal, colores["blanco"], self.rect_continuar.center)
            
        elif self.estado_actual in ["MOSTRANDO_SECUENCIA", "JUGANDO", "TRANSICION_NIVEL", "ESPERANDO_TRANSICION", "GAME_OVER"]:
            if self.estado_actual != "GAME_OVER":
                cx_rueda = cx; cy_rueda = self.rects_botones[3].bottom
                rx, ry = round(cx_rueda - 961.5 * self.escala_circulo), round(cy_rueda - 539.5 * self.escala_circulo)
                self.pantalla.blit(self.circulo_extra, self.circulo_extra.get_rect(topleft=(rx, ry)))
                
                if self.estado_actual in ["MOSTRANDO_SECUENCIA", "JUGANDO"]:
                    self.dibujar_texto_lateral(f"Puntaje: {self.gestor_puntuacion.total}", self.fuente_normal, colores["negro"], 30, "izquierda")
                    self.dibujar_texto_centrado(f"Tiempo: {max(0, self.t_restante):.1f}s", self.fuente_normal, colores["negro"], (self.rect_barra_tiempo.centerx, self.rect_barra_tiempo.top - 35))
                    if self.texto_nivel: self.dibujar_texto_centrado(self.texto_nivel, self.fuente_normal, colores["negro"], (self.pantalla.get_rect().right - 185, 30))
                    if self.personaje_actual and self.mensaje:
                        chibi = self.img_chibi.get(self.personaje_actual.nombre)
                        if chibi:
                            bw = max(200, self.fuente_normal.size(self.mensaje)[0] + 40); bh = 60
                            gx = (self.pantalla.get_rect().right - 185) - (70 + bw - 15) // 2
                            bx = gx + 70 - 15
                            self.pantalla.blit(pygame.transform.smoothscale(chibi, (70, 70)), (gx, 60))
                            self.pantalla.blit(pygame.transform.smoothscale(self.imagen_burbuja_texto, (bw, bh)), (bx, 60))
                            self.dibujar_texto_centrado(self.mensaje, self.fuente_normal, colores["negro"], (bx + bw // 2, 60 + bh // 2))

                for num, rect in self.rects_botones.items():
                    presionado = False
                    if self.estado_actual in ["MOSTRANDO_SECUENCIA", "TRANSICION_NIVEL"]:
                        presionado = self.color_iluminado == num or self.boton_presionado == num
                    if self.estado_actual in ["JUGANDO", "ESPERANDO_TRANSICION"]:
                        if self.boton_presionado == num or self.color_iluminado == num: presionado = True
                    self.pantalla.blit(self.imagenes_botones[num]["presionado" if presionado else "normal"], rect)
                
                self.dibujar_estrellita()
                
                if self.estado_actual in ["MOSTRANDO_SECUENCIA", "JUGANDO"]:
                    self.dibujar_barra_tiempo()
                    if self.estado_actual == "JUGANDO": self.dibujar_personaje_jugando()
                    self._dibujar_botones_laterales()
                elif self.estado_actual == "TRANSICION_NIVEL":
                    self.dibujar_transicion_nivel()
                    
            else: # GAME_OVER
                self.dibujar_texto_centrado("GAME OVER", self.fuente_titulo, colores["rojo_texto"], (cx, 200))
                self.dibujar_texto_centrado(f"Puntaje Final: {self.gestor_puntuacion.total}", self.fuente_normal, colores["negro"], (cx, 300))
                if self.personaje_actual and self.personaje_actual.nombre in self.img_chibi_grande:
                    self.pantalla.blit(self.img_chibi_grande[self.personaje_actual.nombre], self.img_chibi_grande[self.personaje_actual.nombre].get_rect(center=(cx, 500)))
                self._dibujar_botones_laterales()