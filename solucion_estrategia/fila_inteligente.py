LIMITE_ESPERA = 48  # horas límite aceptable de espera (equidad territorial)


class Solicitud:
    """
    Objeto que representa la petición de un municipio.
    nivel_urgencia: 1 (baja) a 5 (crítica / salto de emergencia)
    vulnerable: True si es un municipio pequeño, vulnerable o alejado
    tiempo_espera: horas que lleva esperando la solicitud
    """
    def __init__(self, municipio, nivel_urgencia, vulnerable=False, tiempo_espera=0):
        self.municipio = municipio
        self.nivel_urgencia = nivel_urgencia
        self.vulnerable = vulnerable
        self.tiempo_espera = tiempo_espera

    def prioridad(self):
        # Bono de equidad territorial: si el municipio es vulnerable
        # y ya superó el límite de espera aceptable, sube de prioridad.
        bono = 2 if (self.vulnerable and self.tiempo_espera > LIMITE_ESPERA) else 0
        return self.nivel_urgencia + bono

    def __str__(self):
        return (f"Municipio: {self.municipio:12} | Urgencia: {self.nivel_urgencia} | "
                f"Vulnerable: {'Sí' if self.vulnerable else 'No':3} | "
                f"Espera: {self.tiempo_espera:3}h | Prioridad final: {self.prioridad()}")


class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaPrioridad:
    """
    Misma idea de la 'lista' del docente, pero insertar() ya no agrega
    al final: ubica el nodo según su prioridad, para que la fila se
    reacomode automáticamente (saltos de emergencia incluidos).
    """
    def __init__(self):
        self.primero = None

    def insertar(self, dato):
        nuevo = Nodo(dato)

        # Caso 1: fila vacía o la nueva solicitud es más urgente que la primera
        # (esto simula el "salto de emergencia" al inicio de la fila)
        if self.primero is None or dato.prioridad() > self.primero.dato.prioridad():
            nuevo.siguiente = self.primero
            self.primero = nuevo
            return

        # Caso 2: recorrer buscando el punto donde ya no hay mayor o igual prioridad
        actual = self.primero
        while actual.siguiente and actual.siguiente.dato.prioridad() >= dato.prioridad():
            actual = actual.siguiente
        nuevo.siguiente = actual.siguiente
        actual.siguiente = nuevo

    def mostrar(self):
        if self.primero is None:
            print("No hay solicitudes en la fila.")
            return
        print("=== FILA INTELIGENTE DE TURNOS - GOBERNACIÓN ===")
        actual = self.primero
        posicion = 1
        while actual:
            print(f"{posicion}. {actual.dato}")
            actual = actual.siguiente
            posicion += 1


# =========================
# Prueba del prototipo
# =========================
if __name__ == "__main__":
    fila = ListaPrioridad()

    fila.insertar(Solicitud("San José",   nivel_urgencia=2, vulnerable=True,  tiempo_espera=60))
    fila.insertar(Solicitud("La Capital",  nivel_urgencia=5, vulnerable=False, tiempo_espera=5))
    fila.insertar(Solicitud("El Retiro",   nivel_urgencia=1, vulnerable=False, tiempo_espera=10))
    fila.insertar(Solicitud("Guacarí",     nivel_urgencia=3, vulnerable=True,  tiempo_espera=50))
    fila.insertar(Solicitud("Alerta Roja", nivel_urgencia=5, vulnerable=False, tiempo_espera=0))  # salto de emergencia

    fila.mostrar()