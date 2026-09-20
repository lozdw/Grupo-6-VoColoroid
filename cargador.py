import pygame
try:
    import cv2
except ImportError:
    cv2 = None

class CargadorRecursos:
    def inicializar_recursos(self):
        pygame.font.init()
        # Fuentes
        self.fuente_titulo = pygame.font.Font(str(self.config.archivo_fuente), 48)
        self.fuente_normal = pygame.font.Font(str(self.config.archivo_fuente), 24)
        self.fuente_mensaje = pygame.font.Font(str(self.config.archivo_fuente), 16)
        
        # Sonidos
        self.sonidos = {}
        if pygame.mixer.get_init():
            if self.config.archivo_musica.exists():
                pygame.mixer.music.load(str(self.config.archivo_musica))
                pygame.mixer.music.set_volume(self.config.volumen_musica_base)
                pygame.mixer.music.play(-1)
                self.musica_reproduciendose = True
            
            for clave, ruta in self.config.sonidos.items():
                if ruta.exists():
                    snd = pygame.mixer.Sound(str(ruta))
                    snd.set_volume(self.config.volumenes.get(clave, 0.5))
                    self.sonidos[clave] = snd
        
        self.musica_silenciada = False
        self.sonidos_sistema_silenciados = False

        # Fondos
        tam = self.pantalla.get_size()
        self.marco_menu = pygame.transform.smoothscale(pygame.image.load(self.config.dir_bg / "fondo cortado.png").convert_alpha(), tam)
        self.marco_menu.set_colorkey(self.config.colores["colorkey_marco"])
        self.fondo_menu = self.marco_menu.copy()
        self.fondo_seleccion = pygame.transform.smoothscale(pygame.image.load(self.config.dir_bg / "5 sin título.png").convert(), tam)
        self.fondo_juego = pygame.transform.smoothscale(pygame.image.load(self.config.dir_bg / "Fondo Juego Colores.png").convert_alpha(), tam)
        
        self._cargar_logos()
        self._cargar_botones_ui()
        self._cargar_elementos_juego()
        self._cargar_personajes()
        self._crear_rectangulos()
        
        self.video_fondo = cv2.VideoCapture(str(self.config.dir_bg / "e.mp4")) if cv2 is not None else None

    def _cargar_logos(self):
        logo_orig = pygame.image.load(self.config.dir_bg / "Logo VoColoroid con N.png").convert_alpha()
        h = round(logo_orig.get_height() * 400 / logo_orig.get_width())
        self.logo_inicio = pygame.transform.smoothscale(logo_orig, (400, h))
        self.logo_intro = pygame.transform.smoothscale(pygame.image.load(self.config.dir_bg / "logo redondo.png").convert_alpha(), (420, 420))
        self.rect_logo_intro = self.logo_intro.get_rect(center=self.pantalla.get_rect().center)

    def _cargar_botones_ui(self):
        dir_img = self.config.dir_img
        self.boton_creditos = pygame.transform.smoothscale(pygame.image.load(dir_img / "boton creditos.png").convert_alpha(), (72, 72))
        self.boton_settings = pygame.image.load(dir_img / "boton setting.png").convert_alpha()
        self.imagen_silencio_on = pygame.image.load(dir_img / "silencio on.png").convert_alpha()
        self.imagen_silencio_off = pygame.image.load(dir_img / "silencio off.png").convert_alpha()
        
        # Botones con estado [normal, presionado]
        self.botones_ui = {
            "reinicio": (pygame.transform.smoothscale(pygame.image.load(dir_img / "boton 1 move.png").convert_alpha(), (200, 50)),
                         pygame.transform.smoothscale(pygame.image.load(dir_img / "boton 1.png").convert_alpha(), (200, 50))),
            "volver": (pygame.transform.smoothscale(pygame.image.load(dir_img / "boton 2 move.png").convert_alpha(), (200, 50)),
                       pygame.transform.smoothscale(pygame.image.load(dir_img / "boton 2.png").convert_alpha(), (200, 50))),
            "iniciar": (pygame.transform.smoothscale(pygame.image.load(dir_img / "boton 3 move.png").convert_alpha(), (400, 70)),
                        pygame.transform.smoothscale(pygame.image.load(dir_img / "boton 3 nuevo.png").convert_alpha(), (400, 70)))
        }

    def _cargar_elementos_juego(self):
        dir_img = self.config.dir_img
        nombres_colores = {1: "rojo", 2: "azul", 3: "verde", 4: "amarillo"}
        self.imagenes_botones = {}
        for num, nom in nombres_colores.items():
            self.imagenes_botones[num] = {
                "normal": pygame.transform.smoothscale(pygame.image.load(dir_img / f"asset {nom} final.png").convert_alpha(), (300, 300)),
                "presionado": pygame.transform.smoothscale(pygame.image.load(dir_img / f"asset {nom} pressed final.png").convert_alpha(), (300, 300))
            }
        
        circ = pygame.image.load(dir_img / "circulo.png").convert_alpha()
        self.escala_circulo = 650 / 987
        self.circulo_extra = pygame.transform.smoothscale(circ, (round(circ.get_width() * self.escala_circulo), round(circ.get_height() * self.escala_circulo)))
        
        img_barras = pygame.image.load(dir_img / "Barras de tiempo.png").convert_alpha()
        recortes = {
            "Miku": pygame.Rect(0, 0, 430, 50), "Teto": pygame.Rect(435, 0, 430, 50),
            "Neru": pygame.Rect(0, 70, 430, 50), "Gumi": pygame.Rect(435, 70, 430, 50), "generico": pygame.Rect(180, 150, 435, 40)
        }
        self.marcos_barra_tiempo = {k: pygame.transform.smoothscale(img_barras.subsurface(v), (240, 21)) for k, v in recortes.items()}

    def _cargar_personajes(self):
        dir_img = self.config.dir_img
        nombres = ["Miku", "Teto", "Neru", "Gumi"]
        self.img_pj, self.img_pj_hover, self.img_chibi, self.img_chibi_grande, self.fondos_recuadro = {}, {}, {}, {}, {}
        
        archivos_cabeza = {"Miku": "Miku Pixel Cabeza.png", "Teto": "Teto Pixel Cabeza.png", "Neru": "Neru Pixel Cabeza .png", "Gumi": "Gumi Pixel Cabeza.png"}
        archivos_hover = {"Miku": "Miku Guiño.png", "Teto": "Teto Guiño.png", "Neru": "Neru Guiño.png", "Gumi": "Gumi Guiño.png"}
        archivos_chibi = {"Miku": "Miku Chibi.png", "Teto": "Teto Chibi.png", "Neru": "Neru Chibi Corregido.png", "Gumi": "Gumi Chibi.png"}
        archivos_fondos = {"Miku": "cua azul.png", "Teto": "cua rojo.png", "Neru": "cuADRO AMARILLO.png", "Gumi": "cua verde.png"}
        
        for nom in nombres:
            self.img_pj[nom] = pygame.transform.smoothscale(pygame.image.load(dir_img / archivos_cabeza[nom]).convert_alpha(), (170, 170))
            self.img_pj_hover[nom] = pygame.transform.smoothscale(pygame.image.load(dir_img / archivos_hover[nom]).convert_alpha(), (170, 170))
            self.img_chibi[nom] = pygame.transform.smoothscale(pygame.image.load(dir_img / archivos_chibi[nom]).convert_alpha(), (80, 80))
            self.img_chibi_grande[nom] = pygame.transform.smoothscale(pygame.image.load(dir_img / archivos_chibi[nom]).convert_alpha(), (350, 350))
            self.fondos_recuadro[nom] = pygame.transform.smoothscale(pygame.image.load(dir_img / archivos_fondos[nom]).convert_alpha(), (210, 210))
        
        self.imagen_burbuja_texto = pygame.image.load(dir_img / "texto.png").convert_alpha()

    def _crear_rectangulos(self):
        pr = self.pantalla.get_rect()
        cx, cy = pr.center
        
        self.rect_logo_inicio = self.logo_inicio.get_rect(center=(cx, 291))
        self.rect_boton_creditos = self.boton_creditos.get_rect(bottomright=(pr.right - 149, pr.bottom - 63))
        self.rect_boton_settings = self.boton_settings.get_rect(left=self.rect_boton_creditos.right - 20, centery=self.rect_boton_creditos.centery)
        self.rect_ajuste_musica = pygame.Rect(0, 0, 50, 50); self.rect_ajuste_musica.center = (cx - 80, 385)
        self.rect_ajuste_sistema = pygame.Rect(0, 0, 50, 50); self.rect_ajuste_sistema.center = (cx + 80, 385)
        
        ix, iy = cx - 300, cy - 300
        self.rects_botones = {
            3: pygame.Rect(ix, iy, 300, 300), 2: pygame.Rect(ix + 300, iy, 300, 300),
            4: pygame.Rect(ix, iy + 300, 300, 300), 1: pygame.Rect(ix + 300, iy + 300, 300, 300)
        }
        
        self.rect_barra_tiempo = pygame.Rect(0, 0, 240, 21); self.rect_barra_tiempo.center = (150, cy + 25)
        self.estrellita = self.crear_estrellita(84)  # Método que viene de vistas.py vía mixin
        
        self.rect_iniciar = pygame.Rect(cx - 200, cy + 51, 400, 70)
        self.rect_continuar = pygame.Rect(cx - 200, 460, 400, 70)
        
        ancho, alto, esp = 210, 210, 15
        p_ix = cx - ((ancho * 4 + esp * 3) // 2)
        p_iy = cy - 190
        self.rect_pj = {
            "Miku": pygame.Rect(p_ix, p_iy, ancho, alto), "Teto": pygame.Rect(p_ix + ancho + esp, p_iy, ancho, alto),
            "Neru": pygame.Rect(p_ix + (ancho + esp)*2, p_iy, ancho, alto), "Gumi": pygame.Rect(p_ix + (ancho + esp)*3, p_iy, ancho, alto)
        }
        self.rect_pj_confirmacion = pygame.Rect(cx - 400, 165, ancho, alto)
        
        pos_lat = pr.right - 253
        self.rect_reinicio = pygame.Rect(pos_lat, cy - 55, 200, 50)
        self.rect_volver = pygame.Rect(pos_lat, cy + 5, 200, 50)
        
        self.personaje_hover = None
        self.ventana_creditos_abierta = False
        self.ventana_settings_abierta = False