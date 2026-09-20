from random import randint

class GestorSecuencia:
    def __init__(self, ruta_niveles):
        self.colores_secuencia = []
        self.colores_ingresados = []
        self.archivo_niveles = ruta_niveles
        self.asegurar_archivo_niveles()

    def asegurar_archivo_niveles(self):
        if not self.archivo_niveles.exists():
            self.archivo_niveles.write_text("1", encoding="utf-8")
            return
        actual = self.archivo_niveles.read_text(encoding="utf-8").strip()
        if not actual:
            self.archivo_niveles.write_text("1", encoding="utf-8")

    def consultar_nivel(self):
        self.asegurar_archivo_niveles()
        try:
            with self.archivo_niveles.open("r", encoding="utf-8") as archivo:
                valor = int(archivo.read().strip())
                return max(valor, 1)
        except (OSError, ValueError):
            return 1

    def avanzar_nivel(self):
        nivel = self.consultar_nivel()
        self.archivo_niveles.write_text(str(nivel + 1), encoding="utf-8")

    def reiniciar_progreso(self):
        self.archivo_niveles.write_text("1", encoding="utf-8")
        self.colores_secuencia.clear()
        self.colores_ingresados.clear()

    def calcular_longitud_secuencia(self):
        return max(1, (self.consultar_nivel() + 1) // 2)

    def iniciar_juego(self):
        self.colores_secuencia = [randint(1, 4) for _ in range(self.calcular_longitud_secuencia())]
        self.colores_ingresados.clear()
        return self.colores_secuencia

    def verificar_color(self, numero_color):
        self.colores_ingresados.append(numero_color)
        indice = len(self.colores_ingresados) - 1
        
        if self.colores_ingresados[indice] != self.colores_secuencia[indice]:
            self.colores_ingresados.clear()
            return "ERROR"
            
        if len(self.colores_ingresados) == len(self.colores_secuencia):
            self.avanzar_nivel()
            self.colores_secuencia.clear()
            self.colores_ingresados.clear()
            return "EXITO"
            
        return "CONTINUAR"

class GestorPuntuacion:
    def __init__(self): 
        self.total = 0
        
    def reset(self): 
        self.total = 0
        
    def agregar_por_ronda(self, tiempo_restante, nivel, multiplicador=1.0):
        puntos = int((max(0.0, float(tiempo_restante)) * 100 + max(1, int(nivel)) * 50) * float(multiplicador))
        self.total += puntos
        return puntos 
        
    def agregar_por_acierto(self, tiempo_restante, nivel, multiplicador=1.0):
        return self.agregar_por_ronda(tiempo_restante, nivel, multiplicador)
