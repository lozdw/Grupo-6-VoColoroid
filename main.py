import sys
import pygame
from app import App
from config import ConfiguracionJuego

def main():
    # Pre-inicializar el mixer con un buffer pequeño (512 en vez de 4096) para eliminar el lag o retraso de los sonidos
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    config = ConfiguracionJuego()
    juego = App(config)
    juego.ejecutar()

    pygame.mixer.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
