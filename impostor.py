
from abc import ABC, abstractmethod
from enum import Enum
import random


# 1. FASES DEL JUEGO

class FaseJuego(Enum):
    REGISTRO = 1
    ASIGNACION = 2
    PISTAS = 3
    DEBATE = 4
    VOTACION = 5
    ULTIMA_OPORTUNIDAD = 6
    RESULTADO = 7


# 2. PALABRA SECRETA

class PalabraSecreta:

    def __init__(self, texto, categoria):
        self.texto = texto.upper()
        self.categoria = categoria

    def coincideCon(self, intento):
        return self.texto == intento.upper().strip()


# 3. CLASE ABSTRACTA ROL

class Rol(ABC):

    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def conocePalabra(self):
        pass

    @abstractmethod
    def obtenerPalabraVisible(self, palabra):
        pass


# 4. ROL CIVIL

class Civil(Rol):

    def __init__(self, palabra):
        super().__init__("Civil")
        self.palabra = palabra

    def conocePalabra(self):
        return True

    def obtenerPalabraVisible(self, palabra):
        return self.palabra.texto


# 5. ROL IMPOSTOR

class Impostor(Rol):

    def __init__(self):
        super().__init__("Impostor")

    def conocePalabra(self):
        return False

    def obtenerPalabraVisible(self, palabra):
        return "No conoces la palabra.\nCategoria: " + palabra.categoria

    def intentarAdivinar(self, palabra, intento):
        return palabra.coincideCon(intento)


# 6. JUGADOR

class Jugador:

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.rol = None
        self.eliminado = False

    def darPista(self, texto, turno):
        return Pista(self, texto, turno)

    def votar(self, jugador):
        if jugador == self or jugador.eliminado:
            raise ValueError("Voto no valido")
        return Voto(self, jugador)

    def getRol(self):
        return self.rol


# 7. PISTA

class Pista:

    def __init__(self, autor, texto, turno):
        self.autor = autor
        self.texto = texto
        self.turno = turno


# 8. VOTO

class Voto:

    def __init__(self, votante, acusado):
        self.votante = votante
        self.acusado = acusado


# 9. RONDA

class Ronda:

    def __init__(self, numero):
        self.numero = numero
        self.pistas = []
        self.votos = []
        self.fase = FaseJuego.PISTAS

    def registrarPista(self, pista):
        self.pistas.append(pista)

    def registrarVoto(self, voto):
        if any(v.votante == voto.votante for v in self.votos):
            raise ValueError("Ya has votado")
        self.votos.append(voto)

    def avanzarFase(self, fase):
        self.fase = fase


# 10. PARTIDA

class Partida:

    def __init__(self, jugadores):
        self.jugadores = jugadores
        self.rondas = []
        self.palabra = None
        self.ganador = None

    def iniciar(self, palabra):
        self.palabra = palabra
        impostor = random.choice(self.jugadores)

        for jugador in self.jugadores:
            if jugador == impostor:
                jugador.rol = Impostor()
            else:
                jugador.rol = Civil(palabra)

        self.rondas.append(Ronda(1))

    def determinarGanador(self):
        return self.ganador


# 11. FUNCION PRINCIPAL

def iniciar_juego_interactivo():

    print("\n===== EL IMPOSTOR =====")

    # REGISTRO DE JUGADORES

    while True:
        try:
            cantidad = int(input("\nNumero de jugadores (3-10): "))
            if 3 <= cantidad <= 10:
                break
            print("Debe ingresar entre 3 y 10 jugadores.")
        except ValueError:
            print("Ingrese un numero valido.")

    jugadores = []

    for i in range(cantidad):
        while True:
            nombre = input(f"Nombre del jugador {i+1}: ").strip()

            if not nombre:
                print("El nombre no puede estar vacio.")
            elif any(j.nombre.lower() == nombre.lower() for j in jugadores):
                print("Ese nombre ya existe.")
            else:
                jugadores.append(Jugador(str(i+1), nombre))
                break

    # SELECCION DE CATEGORIA

    categorias = {
        "1": ("Animales", "ELEFANTE"),
        "2": ("Lugares", "PLAYA")
    }

    print("\n===== CATEGORIAS =====")
    print("[1] Animales")
    print("[2] Lugares")

    while True:
        opcion = input("Seleccione una categoria: ").strip()
        if opcion in categorias:
            break
        print("Seleccione 1 o 2.")

    categoria, texto = categorias[opcion]
    palabra = PalabraSecreta(texto, categoria)

    # INICIO DE PARTIDA

    partida = Partida(jugadores)
    partida.iniciar(palabra)
    ronda = partida.rondas[0]

    # ASIGNACION PRIVADA DE ROLES

    print("\n===== ASIGNACION DE ROLES =====")

    for jugador in jugadores:
        input(f"\nTurno de {jugador.nombre}. ENTER para ver su rol.")

        print("\nJugador:", jugador.nombre)
        print("Rol:", jugador.rol.nombre)
        print(jugador.rol.obtenerPalabraVisible(palabra))

        input("\nENTER para ocultar la informacion.")
        print("\n" * 30)

    # FASE DE PISTAS

    ronda.avanzarFase(FaseJuego.PISTAS)
    print("\n===== RONDA DE PISTAS =====")

    for jugador in jugadores:
        while True:
            pista = input(f"{jugador.nombre}, escribe tu pista: ").strip()
            if pista:
                ronda.registrarPista(jugador.darPista(pista, 1))
                break
            print("La pista no puede estar vacia.")

    print("\n===== PISTAS REGISTRADAS =====")

    for pista in ronda.pistas:
        print(pista.autor.nombre + ": " + pista.texto)

    # FASE DE DEBATE

    ronda.avanzarFase(FaseJuego.DEBATE)
    input("\nDebatan entre ustedes. ENTER para continuar a la votacion.")

    # FASE DE VOTACION

    ronda.avanzarFase(FaseJuego.VOTACION)
    print("\n===== VOTACION =====")

    for votante in jugadores:
        disponibles = [j for j in jugadores if j != votante and not j.eliminado]

        print(f"\nTurno de {votante.nombre}:")

        for jugador in disponibles:
            print(f"[{jugador.id}] {jugador.nombre}")

        while True:
            id_voto = input("ID del jugador que desea votar: ").strip()
            acusado = next((j for j in disponibles if j.id == id_voto), None)

            if acusado:
                ronda.registrarVoto(votante.votar(acusado))
                break
            print("ID no valido. Intente nuevamente.")

    # CONTEO DE VOTOS

    print("\n===== RESULTADO DE VOTACION =====")

    conteo = {}

    for voto in ronda.votos:
        nombre = voto.acusado.nombre
        conteo[nombre] = conteo.get(nombre, 0) + 1

    for nombre, votos in conteo.items():
        print(nombre, ":", votos, "voto(s)")

    max_votos = max(conteo.values())

    mas_votados = [
        j for j in jugadores
        if conteo.get(j.nombre, 0) == max_votos
    ]

    # DETERMINAR GANADOR

    if len(mas_votados) > 1:
        print("\nEmpate. El impostor gana.")
        partida.ganador = "Impostor"

    else:
        eliminado = mas_votados[0]
        eliminado.eliminado = True

        print("\nJugador eliminado:", eliminado.nombre)

        if isinstance(eliminado.rol, Impostor):

            ronda.avanzarFase(FaseJuego.ULTIMA_OPORTUNIDAD)
            print("\n¡Descubrieron al impostor!")
            intento = input("Impostor, adivina la palabra secreta: ")

            if eliminado.rol.intentarAdivinar(palabra, intento):
                print("\n¡El impostor adivino la palabra y gano!")
                partida.ganador = "Impostor"
            else:
                print("\n¡El impostor fallo!")
                partida.ganador = "Civiles"

        else:
            print("\nEliminaron a un civil. ¡Gana el impostor!")
            partida.ganador = "Impostor"

    # RESULTADO FINAL

    ronda.avanzarFase(FaseJuego.RESULTADO)

    print("\n===== RESULTADO FINAL =====")
    print("Palabra secreta:", palabra.texto)
    print("Categoria:", palabra.categoria)

    print("\n===== ROLES =====")

    for jugador in jugadores:
        estado = "Eliminado" if jugador.eliminado else "Activo"
        print(jugador.nombre, "-", jugador.rol.nombre, "-", estado)

    print("\n===== GANADOR =====")
    print(partida.determinarGanador().upper())
    print("\n¡GRACIAS POR JUGAR!")


# 12. EJECUCION

if __name__ == "__main__":
    iniciar_juego_interactivo()
