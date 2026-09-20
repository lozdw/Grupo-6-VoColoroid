import os
from pathlib import Path

class ConfiguracionJuego:
    def __init__(self):
        self.ancho_pantalla = 1280
        self.alto_pantalla = 720
        self.titulo = "VoColoroid"
        self.fps = 60

        # Directorios
        self.directorio_base = Path(__file__).parent
        self.dir_assets = self.directorio_base / "assets"
        self.dir_img = self.dir_assets / "images"
        self.dir_bg = self.dir_assets / "backgrounds"
        self.dir_snd = self.dir_assets / "sounds"

        # Archivos de datos
        self.archivo_niveles = self.directorio_base / "niveles.txt"
        self.archivo_fuente = self.dir_assets / "fonts" / "I-pixel-u.ttf"

        # Sonidos
        self.archivo_musica = self.dir_snd / "medicine teto.mp3"
        self.sonidos = {
            1: self.dir_snd / "sonido boton rojo.mp3",
            2: self.dir_snd / "sonido boton azul.mp3",
            3: self.dir_snd / "sonido boton verde.mp3",
            4: self.dir_snd / "sonido boton amarillo.mp3",
            "seleccion": self.dir_snd / "sonido tres.mp3",
            "iniciar": self.dir_snd / "sonido uno.mp3",
            "nivel": self.dir_snd / "sonido cuatro.mp3",
            "reinicio": self.dir_snd / "sonido dos.mp3",
            "corazon": self.dir_snd / "sonido corazon.mp3",
            "settings": self.dir_snd / "sonido tuerca.mp3",
            "uno": self.dir_snd / "sonido uno.mp3",
            "error": self.dir_snd / "rwind.mp3"
        }

        self.volumen_musica_base = 0.1
        self.volumenes = {
            1: 0.1, 2: 0.3, 3: 0.3, 4: 0.3,
            "seleccion": 1.0, "iniciar": 1.0, "nivel": 0.3,
            "reinicio": 0.3, "corazon": 0.3, "settings": 0.3,
            "uno": 0.5, "error": 0.5
        }

        # Colores
        self.colores = {
            "blanco": (255, 255, 255),
            "negro": (0, 0, 0),
            "rojo_texto": (200, 0, 0),
            "fondo_panel": (20, 20, 20, 230),
            "sombra": (0, 0, 0, 75),
            "ventana": (0, 0, 0, 190),
            "colorkey_marco": (42, 43, 46)
        }
        
        self.colores_barras = {
            "Miku": (53, 186, 199),
            "Teto": (228, 18, 53),
            "Neru": (255, 243, 156),
            "Gumi": (128, 234, 121),
            "generico": (53, 186, 199)
        }

        # Configuraciones de Tiempos (Milisegundos / Segundos)
        self.tiempos = {
            "espera_transicion": 150,
            "transicion_nivel": 3.3,
            "animacion_luces": 500,
            "click_delay": 70,
            "boton_presionado": 150,
            "intro_fade": 0.25,
            "intro_total": 1.0
        }
        
        # Textos y Mensajes Estáticos
        self.mensajes = {
            "Miku": "Al presionar el botón correcto por primera vez en la secuencia, Miku sumará 3 segundos al contador de tiempo, pudiendo exceder el límite de 10 segundos",
            "Teto": "Al presionar el botón correcto por primera vez en la secuencia, Teto aumentará el multiplicador interno de puntaje x2 veces.",
            "Neru": "Al finalizar la ejecución de la secuencia, Neru generará un escudo que va a exonerar la penalización de tiempo en tu primer error.",
            "Gumi": "Cada que cometas un error en la secuencia, Gumi reducirá la penalización de tiempo a solo 1 segundo.",
            "default": "INGRESAR AQUÍ",
        }
        
        self.instrucciones = [
            "Al iniciar el juego se reproducirá una secuencia",
            "de colores que emitirán sonidos diferentes,",
            "deberás repetir la secuencia en el orden exacto",
            "que se indicó guiandote por los colores o",
            "los sonidos, si aciertas avanzarás de nivel y",
            "aumentará la dificultad de la secuencia."
        ]

        self.creditos = [
            "Elaborado por:", "", "Luis Cardona", "",
            "Natalia Chacón", "", "Génesis Cova", "", "Javier García"
        ]
