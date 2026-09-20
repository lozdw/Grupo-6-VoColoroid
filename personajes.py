from abc import ABC, abstractmethod

class Personaje(ABC):
    def __init__(self, nombre, multiplicador=1.0):
        self.nombre = nombre
        self.habilidad_aplicada = False
        self._multiplicador_base = float(multiplicador)
        self.multiplicador_puntaje = float(multiplicador)
        self.escudo_activo = False
        self.penalizacion_error = 2.0

    def aplicar_habilidad(self, estado_juego):
        if self.habilidad_aplicada: return
        self._aplicar_habilidad(estado_juego)
        self.habilidad_aplicada = True

    def reiniciar_habilidad(self, estado_juego=None):
        self.habilidad_aplicada = False
        self.multiplicador_puntaje = self._multiplicador_base
        self.escudo_activo = False

        if estado_juego is not None:
            aliases = ("escudo", "escudo_activo", "shield", "proteccion", "bloquear_penalizacion", "primer_error_protegido", "primer_error", "error_actual")
            for alias in aliases:
                try: setattr(estado_juego, alias, False)
                except Exception: pass

    def _activar_escudo(self, estado_juego):
        self.escudo_activo = True
        aliases = ("escudo", "escudo_activo", "shield", "proteccion", "bloquear_penalizacion", "primer_error_protegido")
        for alias in aliases:
            try: setattr(estado_juego, alias, True)
            except Exception: pass

    def _sumar_tiempo(self, estado_juego, valor):
        if hasattr(estado_juego, "t_total"): estado_juego.t_total = getattr(estado_juego, "t_total") + valor
        if hasattr(estado_juego, "t_restante"): estado_juego.t_restante = getattr(estado_juego, "t_restante") + valor

    @abstractmethod
    def _aplicar_habilidad(self, estado_juego): pass

class Miku(Personaje):
    def __init__(self): super().__init__("Miku")
    def _aplicar_habilidad(self, estado_juego): self._sumar_tiempo(estado_juego, 5.0)

class Teto(Personaje):
    def __init__(self): super().__init__("Teto", multiplicador=2.0)
    def _aplicar_habilidad(self, estado_juego): self.multiplicador_puntaje = 2.0

class Neru(Personaje):
    def __init__(self): super().__init__("Neru")
    def _aplicar_habilidad(self, estado_juego):
        self._activar_escudo(estado_juego)
        for attr in ("error_actual", "primer_error"):
            if hasattr(estado_juego, attr): setattr(estado_juego, attr, False)
        if hasattr(estado_juego, "bloquear_penalizacion"): estado_juego.bloquear_penalizacion = True
        try: setattr(estado_juego, "primer_error_protegido", True)
        except Exception: pass

class Gumi(Personaje):
    def __init__(self):
        super().__init__("Gumi", multiplicador=1.2)
        self.penalizacion_error = 1.0

    def _aplicar_habilidad(self, estado_juego):
        pass
