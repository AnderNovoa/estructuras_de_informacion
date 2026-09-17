"""Lista circular ordenada por prioridad para las solicitudes."""

from __future__ import annotations

from dataclasses import dataclass

from Prototipo.solicitud import Solicitud


@dataclass
class Nodo:
    dato: Solicitud
    siguiente: Nodo | None = None


class ListaPrioridadCircular:
    def __init__(self) -> None:
        self.primero: Nodo | None = None
        self.ultimo: Nodo | None = None
        self.actual: Nodo | None = None
        self.tamano = 0
        self._siguiente_id = 1
        # Para cada prioridad guarda el ID que debe recibir el próximo turno.
        self._proximo_por_prioridad: dict[int, int] = {}

    def __len__(self) -> int:
        return self.tamano

    def esta_vacia(self) -> bool:
        return self.primero is None

    def insertar(self, solicitud: Solicitud) -> int:
        """Inserta ordenado por prioridad y conserva el orden de llegada en empates."""
        if solicitud.id_solicitud is None:
            solicitud.id_solicitud = self._siguiente_id
            self._siguiente_id += 1

        nuevo = Nodo(solicitud)
        if self.esta_vacia():
            nuevo.siguiente = nuevo
            self.primero = self.ultimo = self.actual = nuevo
            self.tamano = 1
            return solicitud.id_solicitud

        assert self.primero is not None and self.ultimo is not None
        if solicitud.prioridad() > self.primero.dato.prioridad():
            nuevo.siguiente = self.primero
            self.primero = nuevo
            self.ultimo.siguiente = nuevo
        else:
            cursor = self.primero
            while cursor.siguiente is not self.primero and cursor.siguiente.dato.prioridad() >= solicitud.prioridad():
                cursor = cursor.siguiente
            nuevo.siguiente = cursor.siguiente
            cursor.siguiente = nuevo
            if cursor is self.ultimo:
                self.ultimo = nuevo

        self.tamano += 1
        # Una urgencia crítica interrumpe la rotación actual. Para las demás
        # solicitudes se conserva el orden de rotación entre los empates.
        if solicitud.es_emergencia:
            self.actual = nuevo
        else:
            self._actualizar_turno()
        return solicitud.id_solicitud

    def buscar(self, id_solicitud: int) -> Solicitud | None:
        nodo, _ = self._buscar_nodo(id_solicitud)
        return nodo.dato if nodo else None

    def actualizar(self, id_solicitud: int, **cambios: object) -> bool:
        """Valida y reinserta una solicitud para mantener el orden de prioridad."""
        solicitud = self.buscar(id_solicitud)
        if solicitud is None:
            return False
        nueva = Solicitud(
            cambios.get("municipio", solicitud.municipio),
            cambios.get("nivel_urgencia", solicitud.nivel_urgencia),
            cambios.get("vulnerable", solicitud.vulnerable),
            cambios.get("tiempo_espera", solicitud.tiempo_espera),
        )
        nueva.id_solicitud = id_solicitud
        era_turno_actual = self.actual is not None and self.actual.dato.id_solicitud == id_solicitud
        self.eliminar(id_solicitud)
        self.insertar(nueva)
        if era_turno_actual:
            self._actualizar_turno()
        return True

    def eliminar(self, id_solicitud: int) -> Solicitud | None:
        nodo, anterior = self._buscar_nodo(id_solicitud)
        if nodo is None:
            return None
        assert self.primero is not None and self.ultimo is not None
        if self.tamano == 1:
            self.primero = self.ultimo = self.actual = None
        else:
            assert anterior is not None and nodo.siguiente is not None
            anterior.siguiente = nodo.siguiente
            if nodo is self.primero:
                self.primero = nodo.siguiente
            if nodo is self.ultimo:
                self.ultimo = anterior
            self.ultimo.siguiente = self.primero
            if nodo is self.actual:
                self.actual = nodo.siguiente
        self.tamano -= 1
        nodo.siguiente = None
        self._actualizar_turno()
        return nodo.dato

    def pasar_turno(self) -> Solicitud | None:
        """Rota entre solicitudes con la prioridad máxima actual."""
        if self.actual is None:
            return None
        atendida = self.actual.dato
        siguiente = self._siguiente_con_prioridad(self.actual, atendida.prioridad())
        if siguiente is not None:
            self._proximo_por_prioridad[atendida.prioridad()] = siguiente.dato.id_solicitud
        self._actualizar_turno()
        return atendida

    def resolver_turno_actual(self) -> Solicitud | None:
        if self.actual is None:
            return None
        atendida = self.actual.dato
        siguiente = self._siguiente_con_prioridad(self.actual, atendida.prioridad())
        if siguiente is not None and siguiente is not self.actual:
            self._proximo_por_prioridad[atendida.prioridad()] = siguiente.dato.id_solicitud
        return self.eliminar(atendida.id_solicitud)

    def solicitudes(self, desde_turno_actual: bool = False) -> list[Solicitud]:
        if self.primero is None:
            return []
        if desde_turno_actual:
            return self._turnos_programados()

        inicio = self.primero
        resultado: list[Solicitud] = []
        nodo = inicio
        while True:
            resultado.append(nodo.dato)
            assert nodo.siguiente is not None
            nodo = nodo.siguiente
            if nodo is inicio:
                return resultado

    def _turnos_programados(self) -> list[Solicitud]:
        """Muestra primero toda la ronda de la prioridad que está en turno."""
        assert self.actual is not None
        resultado: list[Solicitud] = []
        ids_incluidos: set[int] = set()
        prioridad = self.actual.dato.prioridad()
        nodo = self.actual
        while True:
            resultado.append(nodo.dato)
            ids_incluidos.add(nodo.dato.id_solicitud)
            siguiente = self._siguiente_con_prioridad(nodo, prioridad)
            if siguiente is None or siguiente is self.actual:
                break
            nodo = siguiente

        # Las prioridades inferiores quedan después de completar esa ronda.
        for solicitud in self.solicitudes():
            if solicitud.id_solicitud not in ids_incluidos:
                resultado.append(solicitud)
        return resultado

    def _buscar_nodo(self, id_solicitud: int) -> tuple[Nodo | None, Nodo | None]:
        if self.primero is None:
            return None, None
        anterior = self.ultimo
        nodo = self.primero
        while True:
            if nodo.dato.id_solicitud == id_solicitud:
                return nodo, anterior
            anterior, nodo = nodo, nodo.siguiente
            assert nodo is not None
            if nodo is self.primero:
                return None, None

    def _actualizar_turno(self) -> None:
        """Selecciona el turno de mayor prioridad y respeta sus empates."""
        if self.primero is None:
            self.actual = None
            return

        prioridad_maxima = self.primero.dato.prioridad()
        id_preferido = self._proximo_por_prioridad.get(prioridad_maxima)
        if id_preferido is not None:
            nodo_preferido, _ = self._buscar_nodo(id_preferido)
            if nodo_preferido is not None and nodo_preferido.dato.prioridad() == prioridad_maxima:
                self.actual = nodo_preferido
                return

        # Al no haber un empate pendiente, inicia por el primero del grupo.
        self.actual = self.primero

    def _siguiente_con_prioridad(self, nodo_inicio: Nodo, prioridad: int) -> Nodo | None:
        """Busca, en sentido circular, el siguiente nodo de una prioridad dada."""
        if self.primero is None:
            return None
        assert nodo_inicio.siguiente is not None
        nodo = nodo_inicio.siguiente
        while True:
            if nodo.dato.prioridad() == prioridad:
                return nodo
            assert nodo.siguiente is not None
            nodo = nodo.siguiente
            if nodo is nodo_inicio:
                return None
