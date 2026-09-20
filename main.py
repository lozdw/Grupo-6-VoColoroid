import sys
import pygame
from app import App
from config import ConfiguracionJuego

def main():
    
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
