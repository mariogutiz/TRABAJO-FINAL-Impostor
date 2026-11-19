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
        self.palabraSecreta = palabra_secreta

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
        return palabra.coincideCon(intento)

class Jugador:
    def __init__(self, id_jugador: str, nombre: str):
        self.id = id_jugador
        self.nombre = nombre
        self.rol: Rol = None
        self.eliminado: bool = False

    def darPista(self, texto: str, numero_turno: int) -> 'Pista':
        return Pista(autor=self, texto=texto, numeroTurno=numero_turno)

    def votar(self, jugador: 'Jugador') -> 'Voto':
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

class Partida:
    def __init__(self, jugadores: list[Jugador], configuracion: dict):
        self.jugadores = jugadores
        self.rondas: list[Ronda] = []
        self.palabraSecreta: PalabraSecreta = None
        self.configuracion = configuracion

    def iniciar(self, palabra: PalabraSecreta):
        self.palabraSecreta = palabra

        indice_impostor = random.randint(0, len(self.jugadores) - 1)
        for i, jugador in enumerate(self.jugadores):
            if i == indice_impostor:
                jugador.rol = Impostor()
            else:
                jugador.rol = Civil(palabra)
                
        self.rondas.append(Ronda(numero=1))

    def nuevaRonda(self):
        siguiente_num = len(self.rondas) + 1
        self.rondas.append(Ronda(numero=siguiente_num))

    def determinarGanador(self) -> str:
        return "Partida en curso"

def iniciar_juego_interactivo():
    print("BIENVENIDOS A EL IMPOSTOR")
    
    try:
        num_jugadores = int(input("Ingrese el número de jugadores (de 3 a 10 jugadores): "))
        if num_jugadores < 3 or num_jugadores > 10:
            print("Se necesitan de 3 a 10 jugadores para poder iniciar")
            return
    except ValueError:
        print("Por favor, ingrese un número válido.")
        return

    lista_jugadores = []
    for i in range(num_jugadores):
        nombre = input(f"Ingrese el nombre del Jugador {i + 1}: ").strip()
        if not nombre:
            nombre = f"Jugador_{i + 1}"
        lista_jugadores.append(Jugador(str(i + 1), nombre))

    banco_palabras = {
        "1": {"categoria": "Animales", "palabra": "ELEFANTE"},
        "2": {"categoria": "Lugares", "palabra": "PLAYA"}
    }

    print("\nSeleccione una categoría:")
    for key, item in banco_palabras.items():
        print(f"[{key}] {item['categoria']}")

    opcion_cat = input("Ingrese el número de la categoría deseada: ").strip()
    
    if opcion_cat in banco_palabras:
        categoria_seleccionada = banco_palabras[opcion_cat]["categoria"]
        texto_palabra = banco_palabras[opcion_cat]["palabra"]
    else:
        print("Opción no válida. Se asignará por defecto la primera categoría.")
        categoria_seleccionada = banco_palabras["1"]["categoria"]
        texto_palabra = banco_palabras["1"]["palabra"]

    palabra = PalabraSecreta(texto_palabra, categoria_seleccionada)

    config = {"rondas": 1}
    partida = Partida(lista_jugadores, config)
    partida.iniciar(palabra)

    print("\n¡Roles asignados de forma aleatoria!")
    print("¡Atención! Cada jugador debe mirar su pantalla de forma privada en su turno.")
    
    for j in lista_jugadores:
        input(f"\nTurno de **{j.nombre}**. Presione ENTER para ver su rol...")
        print(f"\nINFORMACIÓN PRIVADA PARA: {j.nombre}")
        print(f"Tu rol es: {j.getRol().nombre}")
        print(f"Palabra secreta / Pista visual: {j.getRol().obtenerPalabraVisible(palabra)}")
        input("\nPresione ENTER para ocultar y pasar al siguiente jugador...")
        print("\n" * 40)

    print("¡TODOS TIENEN SU ROL! COMIENZA LA RONDA")
    
    ronda_actual = partida.rondas[0]

    for j in lista_jugadores:
        texto_pista = input(f"{j.nombre}, escribe tu pista breve sobre la palabra: ")
        pista = j.darPista(texto_pista, ronda_actual.numero)
        ronda_actual.registrarPista(pista)

    print("\nRESUMEN DE PISTAS DE LA RONDA")
    for p in ronda_actual.pistas:
        print(f" - {p.getAutor().nombre} dijo: '{p.getTexto()}'")

    print("\n¡Es hora del debate y la votación grupal!")
    
    print("\nLista de jugadores:")
    for j in lista_jugadores:
        print(f" - {j.nombre} (ID: {j.id})")
        
    acusador_nombre = input("\n¿Quién emite el voto? (Escribe el nombre): ")
    acusado_nombre = input("¿A qué jugador sospechoso acusan?: ")
    
    votante_obj = next((j for j in lista_jugadores if j.nombre.lower() == acusador_nombre.lower()), None)
    acusado_obj = next((j for j in lista_jugadores if j.nombre.lower() == acusado_nombre.lower()), None)

    if votante_obj and acusado_obj:
        try:
            voto = votante_obj.votar(acusado_obj)
            ronda_actual.registrarVoto(voto)
            print(f"\n[Voto registrado] {voto.votante.nombre} votó contra {voto.getAcusado().nombre}")
        except ValueError as e:
            print(f"Error en el voto: {e}")
    else:
        print("Nombres ingresados no válidos para la votación.")

    print("\nREVELACIÓN FINAL DE ROLES")
    for j in lista_jugadores:
        rol_real = j.getRol().nombre
        print(f" - {j.nombre} era: {rol_real}")

    print("\n¡Gracias por jugar a El Impostor!")


if __name__ == "__main__":
    iniciar_juego_interactivo()
