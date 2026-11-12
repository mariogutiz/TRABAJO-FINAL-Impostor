from abc import ABC, abstractmethod
from enum import Enum
import random

class FaseJuego(Enum):
    REGISTRO = 1
    ASIGNACION = 2
    PISTAS = 3
    DEBATE = 4
    VOTACION = 5
    ULTIMA_OPORTUNIDAD = 6
    RESULTADO = 7

class PalabraSecreta:
    def __init__(self, texto: str, categoria: str):
        self.texto = texto.upper().strip()
        self.categoria = categoria

    def coincideCon(self, texto: str) -> bool:
        """Verifica si el texto ingresado coincide con la palabra secreta."""
        return self.texto == texto.upper().strip()

class Rol(ABC):
    def __init__(self, nombre: str):
        self.nombre = nombre

    @abstractmethod
    def conocePalabra(self) -> bool:
        pass

    @abstractmethod
    def obtenerPalabraVisible(self, palabra_secreta: PalabraSecreta = None) -> str:
        pass

class Civil(Rol):
    def __init__(self, palabra_secreta: PalabraSecreta):
        super().__init__("Civil")
        self.palabraSecreta = palabra_secreta  # Atributo exclusivo de Civil

    def conocePalabra(self) -> bool:
        return True

    def obtenerPalabraVisible(self, palabra_secreta: PalabraSecreta = None) -> str:
        return self.palabraSecreta.texto


class Impostor(Rol):
    def __init__(self):
        super().__init__("Impostor")

    def conocePalabra(self) -> bool:
        return False

    def obtenerPalabraVisible(self, palabra_secreta: PalabraSecreta = None) -> str:
        return "??? (Eres el Impostor)"

    def intentarAdivinar(self, palabra: PalabraSecreta, intento: str) -> bool:
        """Método exclusivo del Impostor para intentar adivinar la palabra secreta."""
        return palabra.coincideCon(intento)

class Jugador:
    def __init__(self, id_jugador: str, nombre: str):
        self.id = id_jugador
        self.nombre = nombre
        self.rol: Rol = None
        self.eliminado: bool = False

    def darPista(self, texto: str, numero_turno: int) -> 'Pista':
        """Permite al jugador registrar una pista en su turno."""
        return Pista(autor=self, texto=texto, numeroTurno=numero_turno)

    def votar(self, jugador: 'Jugador') -> 'Voto':
        """Permite emitir un voto hacia otro jugador."""
        if self == jugador:
            raise ValueError("Un jugador no puede votarse a sí mismo.")
        if jugador.eliminado:
            raise ValueError("No se puede votar a un jugador eliminado.")
        return Voto(votante=self, acusado=jugador)

    def getRol(self) -> Rol:
        return self.rol

class Pista:
    def __init__(self, autor: Jugador, texto: str, numeroTurno: int):
        self.autor = autor
        self.texto = texto
        self.numeroTurno = numeroTurno

    def getTexto(self) -> str:
        return self.texto

    def getAutor(self) -> Jugador:
        return self.autor

class Voto:
    def __init__(self, votante: Jugador, acusado: Jugador):
        self.votante = votante
        self.acusado = acusado

    def getAcusado(self) -> Jugador:
        return self.acusado

class Ronda:
    def __init__(self, numero: int):
        self.numero = numero
        self.pistas: list[Pista] = []
        self.votos: list[Voto] = []
        self.fase: FaseJuego = FaseJuego.PISTAS

    def registrarPista(self, pista: Pista):
        self.pistas.append(pista)

    def registrarVoto(self, voto: Voto):
        self.votos.append(voto)

    def avanzarFase(self, nueva_fase: FaseJuego):
        self.fase = nueva_fase