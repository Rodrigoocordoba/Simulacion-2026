"""Experimentacion con intervalos de confianza para el modelo Entrega Pet.

Evalua cada politica PEP/TP mediante replicas independientes de 180 dias y
estima intervalos de confianza bilaterales con distribucion t de Student.
"""

import csv
import ctypes
import math
import os
import sys
from statistics import mean, stdev
from time import perf_counter

from scipy import stats

from simulador_pet import SimuladorInventario


REPLICAS = 50
ETAPAS_REPLICAS = (10, 20, 30, 40, 50)
DIAS_POR_REPLICA = 180
CONFIANZA = 0.95
CARPETA_SALIDA = os.path.join("salidas", "intervalo_confianza")
ANCHO_TERMINAL = 78

# Selección espacial reducida: cuatro esquinas, dos puntos medios de los
# extremos y cuatro puntos interiores. Incluye la política actual (5, 20).
PARES_A_EVALUAR = [
    # Esquinas del espacio PEP/TP
    (5, 15),
    (5, 25),
    (10, 15),
    (10, 25),
    # Puntos medios sobre los extremos de PEP
    (5, 20),
    (10, 20),
    # Puntos interiores alrededor del centro (PEP 7,5 / TP 20)
    (7, 19),
    (7, 21),
    (8, 19),
    (8, 21),
]


class Color:
    RESET = "\033[0m"
    NEGRITA = "\033[1m"
    AZUL = "\033[94m"
    CIAN = "\033[96m"
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    MAGENTA = "\033[95m"
    GRIS = "\033[90m"


def configurar_terminal():
    """Habilita ANSI en Windows Terminal cuando la salida es interactiva."""
    if os.name == "nt" and sys.stdout.isatty():
        try:
            kernel32 = ctypes.windll.kernel32
            salida = kernel32.GetStdHandle(-11)
            modo = ctypes.c_uint32()
            if kernel32.GetConsoleMode(salida, ctypes.byref(modo)):
                kernel32.SetConsoleMode(salida, modo.value | 0x0004)
        except (AttributeError, OSError):
            pass


def colorear(texto, color):
    usar_color = (
        os.getenv("NO_COLOR") is None
        and (sys.stdout.isatty() or os.getenv("FORCE_COLOR") == "1")
    )
    return f"{color}{texto}{Color.RESET}" if usar_color else texto


def titulo(texto, icono=""):
    print()
    print(colorear("=" * ANCHO_TERMINAL, Color.AZUL))
    prefijo = f"{icono} " if icono else ""
    print(colorear(f"{prefijo}{texto}", Color.NEGRITA + Color.CIAN))
    print(colorear("=" * ANCHO_TERMINAL, Color.AZUL))


def subtitulo(texto, icono=""):
    print()
    prefijo = f"{icono} " if icono else ""
    print(colorear(f"{prefijo}{texto}", Color.NEGRITA + Color.MAGENTA))
    print(colorear("-" * ANCHO_TERMINAL, Color.GRIS))


def moneda(valor, decimales=2):
    texto = f"{valor:,.{decimales}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"


def numero(valor, decimales=2):
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def barra_progreso(actual, total, ancho=28):
    completado = round(ancho * actual / total)
    return "[" + "#" * completado + "." * (ancho - completado) + "]"


def intervalo_confianza_t(valores, confianza=CONFIANZA):
    """Devuelve los componentes de un IC bilateral para la media."""
    n = len(valores)
    if n < 2:
        raise ValueError("Se requieren al menos dos replicas.")

    promedio = mean(valores)
    desviacion = stdev(valores)
    error_estandar = desviacion / math.sqrt(n)
    alpha = 1.0 - confianza
    t_critico = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
    margen = t_critico * error_estandar

    return {
        "n": n,
        "media": promedio,
        "desviacion": desviacion,
        "error_estandar": error_estandar,
        "t_critico": t_critico,
        "margen": margen,
        "limite_inferior": promedio - margen,
        "limite_superior": promedio + margen,
        "shapiro_p": stats.shapiro(valores).pvalue,
    }


def politicas_a_evaluar():
    """Devuelve los diez pares seleccionados para la experimentación."""
    return list(PARES_A_EVALUAR)


def ejecutar_replicas(simulador, pep, tp, replicas=REPLICAS, tf=DIAS_POR_REPLICA):
    """Ejecuta replicas con bloques no superpuestos de los flujos aleatorios."""
    simulador.reiniciar_secuencias()
    resultados = []

    for replica in range(1, replicas + 1):
        resumen = simulador.simular_politica(
            pep,
            tp,
            TF=tf,
            validacion_manual=True,
        )
        demanda = resumen["Demanda_Total"]
        ventas_perdidas = resumen["Ventas_Perdidas"]
        nivel_servicio = (
            100.0 * (demanda - ventas_perdidas) / demanda
            if demanda > 0
            else 0.0
        )

        resultados.append({
            "Replica": replica,
            "PEP": pep,
            "TP": tp,
            "CTF": resumen["CTF"],
            "CTALM": resumen["CTALM"],
            "CVTAP": resumen["CVTAP"],
            "CTEP": resumen["CTEP"],
            "Demanda_Total": demanda,
            "Ventas_Perdidas": ventas_perdidas,
            "Nivel_Servicio_Porcentaje": nivel_servicio,
            "Pedidos_Realizados": resumen["Pedidos_Realizados"],
        })

    return resultados


def resumir_politica(replicas):
    """Calcula IC 95% de las variables de salida relevantes."""
    variables = {
        "CTF": [r["CTF"] for r in replicas],
        "CTALM": [r["CTALM"] for r in replicas],
        "CVTAP": [r["CVTAP"] for r in replicas],
        "CTEP": [r["CTEP"] for r in replicas],
        "Ventas_Perdidas": [r["Ventas_Perdidas"] for r in replicas],
        "Nivel_Servicio_Porcentaje": [
            r["Nivel_Servicio_Porcentaje"] for r in replicas
        ],
        "Pedidos_Realizados": [r["Pedidos_Realizados"] for r in replicas],
    }

    resumen = {
        "PEP": replicas[0]["PEP"],
        "TP": replicas[0]["TP"],
        "Replicas": len(replicas),
        "Dias_Por_Replica": DIAS_POR_REPLICA,
        "Confianza": CONFIANZA,
    }
    for nombre, valores in variables.items():
        ic = intervalo_confianza_t(valores)
        for campo, valor in ic.items():
            if campo != "n":
                resumen[f"{nombre}_{campo}"] = valor

    return resumen


def exportar_csv(ruta, filas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)


def imprimir_resumen_politica(resumen, etiqueta, icono="📊"):
    subtitulo(
        f"{etiqueta} - PEP = {resumen['PEP']}, TP = {resumen['TP']}",
        icono,
    )
    print(f"  Réplicas ejecutadas:              {int(resumen['Replicas'])}")
    print(f"  Horizonte por réplica:            {int(resumen['Dias_Por_Replica'])} días")
    print(f"  CTF promedio:                     {moneda(resumen['CTF_media'])}")
    print(f"  Desviación estándar del CTF:      {moneda(resumen['CTF_desviacion'])}")
    print(
        "  Intervalo de confianza (95%):    "
        f"[{moneda(resumen['CTF_limite_inferior'])}; "
        f"{moneda(resumen['CTF_limite_superior'])}]"
    )
    print(f"  Costo de almacenamiento medio:    {moneda(resumen['CTALM_media'])}")
    print(f"  Costo de ventas perdidas medio:   {moneda(resumen['CVTAP_media'])}")
    print(f"  Costo de emisión medio:           {moneda(resumen['CTEP_media'])}")
    print(
        "  Nivel de servicio medio:         "
        f"{numero(resumen['Nivel_Servicio_Porcentaje_media'])}%"
    )
    print(
        "  IC 95% del nivel de servicio:    "
        f"[{numero(resumen['Nivel_Servicio_Porcentaje_limite_inferior'])}%; "
        f"{numero(resumen['Nivel_Servicio_Porcentaje_limite_superior'])}%]"
    )
    print(
        "  Ventas perdidas medias:          "
        f"{numero(resumen['Ventas_Perdidas_media'])} bolsas"
    )
    print(
        "  Pedidos realizados (promedio):   "
        f"{numero(resumen['Pedidos_Realizados_media'])}"
    )


def imprimir_ranking(resumenes, cantidad=5):
    subtitulo(f"{cantidad} POLÍTICAS CON MENOR CTF PROMEDIO", "🏆")
    print(
        colorear(
            f"  {'Pos.':<5}{'PEP':<6}{'TP':<6}{'CTF promedio':>18}"
            f"{'IC 95% para el CTF':>35}",
            Color.NEGRITA,
        )
    )
    for posicion, fila in enumerate(resumenes[:cantidad], start=1):
        intervalo = (
            f"[{moneda(fila['CTF_limite_inferior'], 0)}; "
            f"{moneda(fila['CTF_limite_superior'], 0)}]"
        )
        print(
            f"  {posicion:<5}{fila['PEP']:<6}{fila['TP']:<6}"
            f"{moneda(fila['CTF_media']):>18}{intervalo:>35}"
        )


def intervalos_se_superponen(primera, segunda):
    """Indica si dos intervalos individuales del CTF comparten valores."""
    return not (
        primera["CTF_limite_superior"] < segunda["CTF_limite_inferior"]
        or segunda["CTF_limite_superior"] < primera["CTF_limite_inferior"]
    )


def alternativas_solapadas(resumenes, optima):
    return [
        fila
        for fila in resumenes
        if (fila["PEP"], fila["TP"]) != (optima["PEP"], optima["TP"])
        and intervalos_se_superponen(optima, fila)
    ]


def analizar_etapas(replicas_por_politica):
    """Aplica eliminación sucesiva: solo descarta intervalos claramente peores."""
    activas = list(PARES_A_EVALUAR)
    historial = []

    subtitulo("ANÁLISIS PROGRESIVO DE SUPERPOSICIÓN", "🔎")
    print(
        "  Regla: si un IC se superpone con el mejor, continúa. "
        "Si queda totalmente por encima, se descarta."
    )

    for n in ETAPAS_REPLICAS:
        resumenes = sorted(
            (
                resumir_politica(replicas_por_politica[politica][:n])
                for politica in activas
            ),
            key=lambda fila: fila["CTF_media"],
        )
        mejor = resumenes[0]
        continúan = []
        descartadas = []

        for fila in resumenes:
            es_mejor = (fila["PEP"], fila["TP"]) == (
                mejor["PEP"],
                mejor["TP"],
            )
            se_superpone = es_mejor or intervalos_se_superponen(mejor, fila)
            estado = "CONTINÚA" if se_superpone else "DESCARTADA"
            politica = (fila["PEP"], fila["TP"])
            (continúan if se_superpone else descartadas).append(politica)
            historial.append({
                "N": n,
                "PEP": fila["PEP"],
                "TP": fila["TP"],
                "CTF_Media": fila["CTF_media"],
                "IC95_Limite_Inferior": fila["CTF_limite_inferior"],
                "IC95_Limite_Superior": fila["CTF_limite_superior"],
                "Mejor_PEP": mejor["PEP"],
                "Mejor_TP": mejor["TP"],
                "Se_Superpone_Con_Mejor": "SI" if se_superpone else "NO",
                "Estado": estado,
            })

        print()
        print(
            colorear(
                f"  N = {n}: menor media PEP {mejor['PEP']} / TP {mejor['TP']} "
                f"= {moneda(mejor['CTF_media'])}",
                Color.NEGRITA + Color.CIAN,
            )
        )
        print(
            "       IC 95%: "
            f"[{moneda(mejor['CTF_limite_inferior'])}; "
            f"{moneda(mejor['CTF_limite_superior'])}]"
        )
        print(
            f"       Continúan por superposición: {len(continúan)} "
            f"| Descartadas: {len(descartadas)}"
        )
        if descartadas:
            print(
                "       Pares descartados: "
                + ", ".join(f"({p}, {t})" for p, t in descartadas)
            )

        activas = continúan
        if len(activas) == 1:
            print(
                colorear(
                    f"       ✅ Los intervalos ya permiten seleccionar {activas[0]}.",
                    Color.VERDE,
                )
            )
            break
        if n < ETAPAS_REPLICAS[-1]:
            print(
                colorear(
                    f"       ⚠️  Hay superposición: se aumenta N a la siguiente etapa.",
                    Color.AMARILLO,
                )
            )

    return activas, historial


def imprimir_recomendacion(optima, inicial, solapadas):
    ahorro = inicial["CTF_media"] - optima["CTF_media"]
    ahorro_porcentual = 100.0 * ahorro / inicial["CTF_media"]
    mejora_servicio = (
        optima["Nivel_Servicio_Porcentaje_media"]
        - inicial["Nivel_Servicio_Porcentaje_media"]
    )
    reduccion_ventas = (
        inicial["Ventas_Perdidas_media"] - optima["Ventas_Perdidas_media"]
    )

    titulo(
        "CONCLUSIÓN CON 50 CORRIDAS"
        if solapadas
        else "RECOMENDACIÓN FINAL",
        "🎯",
    )
    print(
        colorear(
            f"El menor CTF medio corresponde provisionalmente a PEP = "
            f"{optima['PEP']} y TP = {optima['TP']}.",
            Color.NEGRITA + (Color.AMARILLO if solapadas else Color.VERDE),
        )
    )
    print()
    print(f"  💰 Ahorro promedio frente a PEP 5 / TP 20: {moneda(ahorro)}")
    print(f"  📉 Reducción estimada del CTF:              {numero(ahorro_porcentual)}%")
    print(f"  📈 Mejora del nivel de servicio:            {numero(mejora_servicio)} puntos")
    print(f"  📦 Reducción de ventas perdidas:             {numero(reduccion_ventas)} bolsas")
    print(
        "  📐 IC 95% del CTF con menor media:          "
        f"[{moneda(optima['CTF_limite_inferior'])}; "
        f"{moneda(optima['CTF_limite_superior'])}]"
    )
    if solapadas:
        print()
        print(
            colorear(
                f"⚠️  Su intervalo se superpone con {len(solapadas)} alternativa(s):",
                Color.NEGRITA + Color.AMARILLO,
            )
        )
        for fila in solapadas:
            print(
                f"     - PEP {fila['PEP']} / TP {fila['TP']}: "
                f"[{moneda(fila['CTF_limite_inferior'])}; "
                f"{moneda(fila['CTF_limite_superior'])}]"
            )
        print()
        print(
            colorear(
                "Con 50 corridas no puede afirmarse cuál de esos pares minimiza "
                "definitivamente el costo. Según el criterio del profesor, el siguiente "
                "paso es aumentar N solamente para estas alternativas.",
                Color.AMARILLO,
            )
        )
    else:
        print()
        print(
            colorear(
                "El intervalo de la alternativa seleccionada no se superpone con los "
                "restantes; puede recomendarse como el menor costo dentro del conjunto.",
                Color.VERDE,
            )
        )


def main():
    configurar_terminal()
    inicio = perf_counter()
    simulador = SimuladorInventario(
        "numeros_demanda.csv",
        "numeros_lead_time.csv",
    )
    politicas = politicas_a_evaluar()
    resumenes = []
    replicas_por_politica = {}
    todas_las_replicas = []

    titulo("SIMULACIÓN ENTREGA PET - EXPERIMENTACIÓN ESTADÍSTICA", "🐶")
    print(colorear("  Producto: Vital Can Premium Perro Adulto 20 kg", Color.NEGRITA))
    print("  Objetivo: minimizar el Costo Total de Funcionamiento (CTF)")
    print(
        f"  Experimento: {len(politicas)} políticas PEP/TP, {REPLICAS} réplicas "
        f"de {DIAS_POR_REPLICA} días"
    )
    print("  Nivel de confianza: 95% - distribución t de Student")
    print()
    print(
        colorear(
            f"✅ Cargados {len(simulador.numeros_demanda):,} números "
            "pseudoaleatorios para demanda",
            Color.VERDE,
        )
    )
    print(
        colorear(
            f"✅ Cargados {len(simulador.numeros_lead_time):,} números "
            "pseudoaleatorios para lead time",
            Color.VERDE,
        )
    )

    subtitulo(
        f"EJECUTANDO {REPLICAS} RÉPLICAS PARA {len(politicas)} POLÍTICAS...",
        "🔄",
    )
    print(
        "  Cada política utiliza los mismos escenarios de demanda para permitir "
        "una comparación homogénea."
    )

    for indice, (pep, tp) in enumerate(politicas, start=1):
        replicas = ejecutar_replicas(simulador, pep, tp)
        resumenes.append(resumir_politica(replicas))
        replicas_por_politica[(pep, tp)] = replicas
        todas_las_replicas.extend(replicas)
        if indice % 10 == 0 or indice == len(politicas):
            progreso = barra_progreso(indice, len(politicas))
            print(
                colorear(
                    f"  {progreso} {indice:>2}/{len(politicas)} políticas completadas",
                    Color.CIAN,
                )
            )

    activas, historial_etapas = analizar_etapas(replicas_por_politica)

    resumenes.sort(key=lambda fila: fila["CTF_media"])
    resumenes_activas = [
        fila for fila in resumenes if (fila["PEP"], fila["TP"]) in activas
    ]
    optima = min(resumenes_activas, key=lambda fila: fila["CTF_media"])
    inicial = next(
        fila for fila in resumenes if fila["PEP"] == 5 and fila["TP"] == 20
    )
    solapadas = alternativas_solapadas(resumenes_activas, optima)
    replicas_optima = replicas_por_politica[(optima["PEP"], optima["TP"])]

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    exportar_csv(
        os.path.join(CARPETA_SALIDA, "resumen_politicas_ic95.csv"),
        resumenes,
    )
    exportar_csv(
        os.path.join(CARPETA_SALIDA, "replicas_mejor_media_observada.csv"),
        replicas_optima,
    )
    exportar_csv(
        os.path.join(CARPETA_SALIDA, "evolucion_intervalos_por_etapa.csv"),
        historial_etapas,
    )
    exportar_csv(
        os.path.join(CARPETA_SALIDA, "replicas_todos_los_pares.csv"),
        todas_las_replicas,
    )

    imprimir_resumen_politica(inicial, "RESULTADOS DE LA POLÍTICA INICIAL", "📋")
    imprimir_ranking(resumenes)
    imprimir_resumen_politica(
        optima,
        "RESULTADOS DE LA MEJOR MEDIA OBSERVADA"
        if solapadas
        else "RESULTADOS DE LA POLÍTICA RECOMENDADA",
        "📊",
    )
    imprimir_recomendacion(optima, inicial, solapadas)

    duracion = perf_counter() - inicio
    print()
    print(
        colorear(
            f"💾 Resultados exportados en: {CARPETA_SALIDA}",
            Color.VERDE,
        )
    )
    print(colorear(f"⏱️  Tiempo total: {duracion:.2f} segundos", Color.GRIS))
    print(colorear("=" * ANCHO_TERMINAL, Color.AZUL))


if __name__ == "__main__":
    main()
