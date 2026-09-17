from Prototipo.estructura import ListaPrioridadCircular
from Prototipo.solicitud import Solicitud


def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    while True:
        try:
            valor = int(input(mensaje).strip())
            if minimo is not None and valor < minimo:
                raise ValueError
            if maximo is not None and valor > maximo:
                raise ValueError
            return valor
        except ValueError:
            rango = f" entre {minimo} y {maximo}" if maximo is not None else f" mayor o igual a {minimo}"
            print(f"Ingrese un número entero{rango}.")


def leer_booleano(mensaje: str) -> bool:
    while True:
        respuesta = input(f"{mensaje} (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Responda s o n.")


def registrar(fila: ListaPrioridadCircular) -> None:
    municipio = input("Municipio: ").strip()
    urgencia = leer_entero("Nivel de urgencia (1-5): ", 1, 5)
    vulnerable = leer_booleano("¿Es vulnerable?")
    espera = leer_entero("Tiempo de espera (horas): ", 0)
    try:
        identificador = fila.insertar(Solicitud(municipio, urgencia, vulnerable, espera))
        print(f"Solicitud registrada con ID {identificador}.")
    except ValueError as error:
        print(f"No se registró la solicitud: {error}")


def mostrar(fila: ListaPrioridadCircular, desde_turno: bool = False) -> None:
    solicitudes = fila.solicitudes(desde_turno)
    if not solicitudes:
        print("No hay solicitudes registradas.")
        return
    titulo = "TURNOS PROGRAMADOS DESDE EL ACTUAL" if desde_turno else "SOLICITUDES POR PRIORIDAD"
    print(f"\n=== {titulo} ({len(fila)} solicitudes) ===")
    for posicion, solicitud in enumerate(solicitudes, 1):
        turno = "  ← TURNO ACTUAL" if solicitud is fila.actual.dato else ""
        print(f"{posicion}. {solicitud}{turno}")


def editar(fila: ListaPrioridadCircular) -> None:
    identificador = leer_entero("ID de la solicitud a editar: ", 1)
    solicitud = fila.buscar(identificador)
    if solicitud is None:
        print("No existe una solicitud con ese ID.")
        return
    print("Deje vacío un campo para conservar su valor actual.")
    municipio = input(f"Municipio [{solicitud.municipio}]: ").strip() or solicitud.municipio
    urgencia_texto = input(f"Urgencia [{solicitud.nivel_urgencia}]: ").strip()
    espera_texto = input(f"Horas de espera [{solicitud.tiempo_espera}]: ").strip()
    vulnerable_texto = input(f"¿Vulnerable? (s/n) [{'s' if solicitud.vulnerable else 'n'}]: ").strip().lower()
    try:
        urgencia = solicitud.nivel_urgencia if not urgencia_texto else int(urgencia_texto)
        espera = solicitud.tiempo_espera if not espera_texto else int(espera_texto)
        if vulnerable_texto not in ("", "s", "si", "sí", "n", "no"):
            raise ValueError("El valor vulnerable debe ser s o n.")
        vulnerable = solicitud.vulnerable if not vulnerable_texto else vulnerable_texto in ("s", "si", "sí")
        fila.actualizar(identificador, municipio=municipio, nivel_urgencia=urgencia,
                       vulnerable=vulnerable, tiempo_espera=espera)
        print("Solicitud actualizada.")
    except ValueError as error:
        print(f"No se realizaron cambios: {error}")


def pasar_turno(fila: ListaPrioridadCircular) -> None:
    atendida = fila.pasar_turno()
    if atendida is None:
        print("No hay solicitudes para atender.")
        return
    print(f"Turno atendido temporalmente: {atendida.municipio} (ID {atendida.id_solicitud}).")
    if fila.actual:
        print(f"Siguiente turno: {fila.actual.dato.municipio}.")


def resolver(fila: ListaPrioridadCircular) -> None:
    resuelta = fila.resolver_turno_actual()
    if resuelta is None:
        print("No hay solicitudes para resolver.")
    else:
        print(f"Solicitud resuelta y retirada: {resuelta.municipio} (ID {resuelta.id_solicitud}).")


def cancelar(fila: ListaPrioridadCircular) -> None:
    identificador = leer_entero("ID de la solicitud a cancelar: ", 1)
    eliminada = fila.eliminar(identificador)
    print("Solicitud cancelada." if eliminada else "No existe una solicitud con ese ID.")


def ejecutar() -> None:
    fila = ListaPrioridadCircular()
    opciones = {
        "1": lambda: registrar(fila), "2": lambda: mostrar(fila),
        "3": lambda: mostrar(fila, desde_turno=True), "4": lambda: pasar_turno(fila),
        "5": lambda: resolver(fila), "6": lambda: editar(fila), "7": lambda: cancelar(fila),
    }
    while True:
        print("\n=== SISTEMA DE TURNOS MUNICIPALES ===")
        print("1. Registrar solicitud\n2. Ver solicitudes por prioridad\n3. Ver turnos programados")
        print("4. Atender y pasar turno\n5. Resolver turno actual\n6. Editar solicitud\n7. Cancelar solicitud\n0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("Hasta luego.")
            return
        accion = opciones.get(opcion)
        if accion:
            accion()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    ejecutar()