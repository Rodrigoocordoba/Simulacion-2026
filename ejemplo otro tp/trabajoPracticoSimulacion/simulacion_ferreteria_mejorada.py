"""
Simulación Ferretería JYL - Versión Mejorada
Basada en código funcional con agregados de arrepentimiento y números validados
"""

import os
import scipy.stats as stats
import math
import statistics
import csv
from typing import List

class SimuladorFerreteria:
    def __init__(self, numeros_pseudoaleatorios: List[float]):
        """Inicializa con números pseudoaleatorios validados"""
        self.numeros = numeros_pseudoaleatorios
        self.indice_numero = 0
    
    def obtener_numero_aleatorio(self) -> float:
        """Obtiene siguiente número de la secuencia validada"""
        if self.indice_numero >= len(self.numeros):
            self.indice_numero = 0  # Reiniciar si se agotan
        
        numero = self.numeros[self.indice_numero]
        self.indice_numero += 1
        return numero
    
    def generar_TA(self) -> int:
        """Genera tiempo de atención: Uniforme[3,20]"""
        ri = self.obtener_numero_aleatorio()
        return round(3 + 17*ri)
    
    def generar_IA(self, turno_tipo: str) -> int:
        """
        Genera tiempo entre arribos según turno:
        - mañana: Uniforme[1,14] 
        - tarde: Uniforme[4,20]
        """
        ri = self.obtener_numero_aleatorio()
        if turno_tipo == "mañana":
            return round(1 + 13*ri)
        else:  # tarde
            return round(4 + 16*ri)
    
    def evaluar_arrepentimiento(self, tiempo_espera_estimado: float) -> bool:
        """
        Evalúa arrepentimiento según tiempo de espera:
        - 15+ min: 20% se va
        - 20+ min: 45% se va  
        - 25+ min: 96% se va
        """
        if tiempo_espera_estimado < 15:
            return False  # No se va
        
        ri = self.obtener_numero_aleatorio()
        
        if tiempo_espera_estimado >= 25:
            return ri <= 0.96  # 96% se va
        elif tiempo_espera_estimado >= 20:
            return ri <= 0.45  # 45% se va
        else:  # >= 15
            return ri <= 0.20  # 20% se va
    
    def estimar_tiempo_espera(self, servidor_idx: int, cant_personas_actual: List[int], 
                            t_proxima_salida: List[float], t_actual: float) -> float:
        """Estima tiempo de espera para evaluar arrepentimiento"""
        if cant_personas_actual[servidor_idx] == 0:
            return 0  # Atención inmediata
        
        # Tiempo restante del cliente actual + cola * tiempo promedio
        tiempo_restante = max(0, t_proxima_salida[servidor_idx] - t_actual)
        tiempo_cola = (cant_personas_actual[servidor_idx] - 1) * 11.5  # Promedio TA
        return tiempo_restante + tiempo_cola
    
    def buscar_menor(self, lista: List) -> int:
        """Encuentra posición del menor elemento"""
        return lista.index(min(lista))
    
    def determinar_tipo_distribucion(self, datos: List[float]) -> bool:
        """Determina si los datos siguen distribución normal"""
        _, p_value = stats.normaltest(datos)
        return p_value >= 0.05
    
    def calcular_estadistico_t(self, nivel_error: float, grados_libertad: int) -> float:
        """Calcula estadístico t para intervalo de confianza"""
        return stats.t.ppf(1 - nivel_error/2, grados_libertad)
    
    def simular(self, cant_empleados: int = 2, cant_corridas: int = 50) -> dict:
        """Ejecuta simulación completa"""
        
        # Parámetros de simulación
        HIGHVALUE = 1000000
        CANT_TURNOS = 2  # mañana y tarde
        CANT_DIAS = 20  # días hábiles por mes
        
        promedio_t_espera_total = 0
        cant_personas_diarias = 0
        promedio_t_espera_simulacion = []
        clientes_se_fueron_total = 0
        tiempo_maximo_espera_total = 0
        
        print(f"🔄 Ejecutando {cant_corridas} corridas con {cant_empleados} empleado(s)...")
        
        for corrida in range(cant_corridas):
            if (corrida + 1) % 10 == 0:
                print(f"  Corrida {corrida + 1}/{cant_corridas}")
            
            # Reiniciar índice para cada corrida
            self.indice_numero = (corrida * 2000) % len(self.numeros)
            
            promedio_t_espera_corrida = 0
            clientes_se_fueron_corrida = 0
            tiempo_maximo_espera_corrida = 0
            
            for dia in range(CANT_DIAS):
                for turno in range(CANT_TURNOS):
                    turno_tipo = "mañana" if turno == 0 else "tarde"
                    
                    # Duración según turno
                    if turno_tipo == "mañana":
                        TFINAL = 270  # 8:00-12:30 = 4.5 horas
                    else:  # tarde
                        TFINAL = 240  # 16:30-20:30 = 4 horas
                    
                    # Inicialización
                    t_proxima_llegada = self.generar_IA(turno_tipo)
                    t_actual = 0
                    t_llegada = 0
                    t_proxima_salida = [HIGHVALUE] * cant_empleados
                    cant_personas_actual = [0] * cant_empleados
                    cant_personas_total = 0
                    sum_tiempo_atencion = 0
                    sum_tiempo_permanencia = 0
                    clientes_se_fueron_turno = 0
                    tiempo_maximo_espera_turno = 0
                    
                    vaciamiento_cola = True
                    
                    while t_actual <= TFINAL or vaciamiento_cola:
                        k = self.buscar_menor(t_proxima_salida)
                        
                        if t_proxima_llegada <= t_proxima_salida[k]:
                            # EVENTO: LLEGADA
                            t_llegada = t_proxima_llegada
                            t_actual = t_proxima_llegada
                            
                            if t_actual <= TFINAL:  # Solo generar si dentro del horario
                                t_proxima_llegada = t_actual + self.generar_IA(turno_tipo)
                            else:
                                t_proxima_llegada = HIGHVALUE
                            
                            # Buscar servidor con menor cola
                            p = self.buscar_menor(cant_personas_actual)
                            
                            # Estimar tiempo de espera y evaluar arrepentimiento
                            tiempo_espera_estimado = self.estimar_tiempo_espera(
                                p, cant_personas_actual, t_proxima_salida, t_actual
                            )
                            
                            if self.evaluar_arrepentimiento(tiempo_espera_estimado):
                                # Cliente se va sin ser atendido
                                clientes_se_fueron_turno += 1
                            else:
                                # Cliente se queda
                                cant_personas_actual[p] += 1
                                cant_personas_total += 1
                                
                                # Actualizar tiempo máximo de espera
                                tiempo_maximo_espera_turno = max(tiempo_maximo_espera_turno, tiempo_espera_estimado)
                                
                                if cant_personas_actual[p] == 1:
                                    # Atención inmediata
                                    t_atencion = self.generar_TA()
                                    t_proxima_salida[p] = t_actual + t_atencion
                                    sum_tiempo_atencion += t_atencion
                                    sum_tiempo_permanencia += (t_proxima_salida[p] - t_llegada)
                                else:
                                    # Va a cola
                                    sum_tiempo_permanencia -= t_llegada
                        
                        else:
                            # EVENTO: SALIDA
                            t_actual = t_proxima_salida[k]
                            cant_personas_actual[k] -= 1
                            
                            if cant_personas_actual[k] > 0:
                                # Atender siguiente de la cola
                                t_atencion = self.generar_TA()
                                t_proxima_salida[k] = t_actual + t_atencion
                                sum_tiempo_atencion += t_atencion
                                sum_tiempo_permanencia += t_proxima_salida[k]
                            else:
                                # Servidor queda libre
                                t_proxima_salida[k] = HIGHVALUE
                        
                        # Verificar condición de vaciamiento
                        if t_actual > TFINAL:
                            vaciamiento_cola = False
                            for cant_personas in cant_personas_actual:
                                if cant_personas > 0:
                                    t_proxima_llegada = HIGHVALUE
                                    vaciamiento_cola = True
                                    break
                    
                    # Estadísticas del turno
                    if cant_personas_total > 0:
                        promedio_t_espera_turno = (sum_tiempo_permanencia - sum_tiempo_atencion) / cant_personas_total
                        promedio_t_espera_corrida += promedio_t_espera_turno
                    
                    cant_personas_diarias += cant_personas_total
                    clientes_se_fueron_corrida += clientes_se_fueron_turno
                    tiempo_maximo_espera_corrida = max(tiempo_maximo_espera_corrida, tiempo_maximo_espera_turno)
            
            # Estadísticas de la corrida
            promedio_corrida = promedio_t_espera_corrida / (CANT_DIAS * CANT_TURNOS)
            promedio_t_espera_simulacion.append(promedio_corrida)
            promedio_t_espera_total += promedio_corrida
            clientes_se_fueron_total += clientes_se_fueron_corrida
            tiempo_maximo_espera_total = max(tiempo_maximo_espera_total, tiempo_maximo_espera_corrida)
        
        # Calcular estadísticas finales
        promedio_t_espera_total /= cant_corridas
        
        # Intervalo de confianza
        dist_normal = self.determinar_tipo_distribucion(promedio_t_espera_simulacion)
        desvio_est = statistics.stdev(promedio_t_espera_simulacion)
        alfa = 0.01 # alfa del 99% cambiar en base la excperimentacion
        r = cant_corridas
        
        if dist_normal:
            estadistico = self.calcular_estadistico_t(alfa, r-1)
            lim_inf = promedio_t_espera_total - (desvio_est * estadistico) / math.sqrt(r)
            lim_sup = promedio_t_espera_total + (desvio_est * estadistico) / math.sqrt(r)
            dist_text = "La distribución de los datos es normal."
        else:
            lim_inf = promedio_t_espera_total - desvio_est / math.sqrt(r * alfa)
            lim_sup = promedio_t_espera_total + desvio_est / math.sqrt(r * alfa)
            dist_text = "La distribución de los datos no es normal."
        
        return {
            "cant_empleados": cant_empleados,
            "cant_corridas": cant_corridas,
            "promedio_tiempo_espera": promedio_t_espera_total,
            "tiempo_maximo_espera": tiempo_maximo_espera_total,
            "clientes_atendidos": cant_personas_diarias,
            "clientes_se_fueron": clientes_se_fueron_total,
            "porcentaje_perdida": (clientes_se_fueron_total / (cant_personas_diarias + clientes_se_fueron_total)) * 100,
            "cumple_objetivo": promedio_t_espera_total <= 6.0,
            "distribucion_normal": dist_normal,
            "distribucion_texto": dist_text,
            "desvio_estandar": desvio_est,
            "limite_inferior": lim_inf,
            "limite_superior": lim_sup,
            "datos_corridas": promedio_t_espera_simulacion
        }

def cargar_numeros_pseudoaleatorios(archivo: str = "numeros_pseudoaleatorios.csv") -> List[float]:
    """Carga números pseudoaleatorios validados"""
    numeros = []
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                numeros.append(float(row['numero_pseudoaleatorio']))
        print(f"✅ Cargados {len(numeros)} números pseudoaleatorios validados")
    except FileNotFoundError:
        print(f"❌ No se encontró {archivo}")
        print("Ejecuta primero 'numeros_pseudoaleatorios.py'")
        raise
    return numeros

def exportar_resultados(resultados_experimento: dict, archivo: str = "resultados_ferreteria.csv"):
    """Exporta resultados del experimento"""
    datos = []
    for config in [1, 2, 3]:
        if config in resultados_experimento:
            r = resultados_experimento[config]
            datos.append({
                "empleados": config,
                "tiempo_espera_promedio": round(r["promedio_tiempo_espera"], 4),
                "tiempo_espera_max": round(r["tiempo_maximo_espera"], 2),
                "clientes_atendidos": r["clientes_atendidos"],
                "clientes_perdidos": r["clientes_se_fueron"],
                "porcentaje_perdida": round(r["porcentaje_perdida"], 2),
                "cumple_objetivo_6min": r["cumple_objetivo"],
                "limite_inferior": round(r["limite_inferior"], 4),
                "limite_superior": round(r["limite_superior"], 4),
                "distribucion_normal": r["distribucion_normal"]
            })
    
    # Exportar a CSV
    with open(archivo, 'w', newline='', encoding='utf-8') as file:
        if datos:
            writer = csv.DictWriter(file, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)
    
    print(f"✅ Resultados exportados a: {archivo}")

def limpiar_consola():
    """Limpia la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Función principal"""
    print("🏪 Simulación Ferretería JYL - Versión Mejorada")
    print("=" * 60)
    
    try:
        # Cargar números pseudoaleatorios validados
        numeros = cargar_numeros_pseudoaleatorios()
        simulador = SimuladorFerreteria(numeros)
        
        # Configuraciones a evaluar
        configuraciones = [1, 2, 3]  # empleados
        resultados_experimento = {}
        
        for cant_empleados in configuraciones:
            print(f"\n{'='*60}")
            resultados = simulador.simular(cant_empleados=cant_empleados, cant_corridas=50)
            resultados_experimento[cant_empleados] = resultados
            
            # Mostrar resultados
            print(f"\n📊 RESULTADOS CON {cant_empleados} EMPLEADO(S):")
            print(f" - Clientes atendidos: {resultados['clientes_atendidos']}")
            print(f" - Clientes perdidos (arrepentimiento): {resultados['clientes_se_fueron']}")
            print(f" - % pérdida de clientes: {resultados['porcentaje_perdida']:.2f}%")
            print(f" - Tiempo de espera promedio: {resultados['promedio_tiempo_espera']:.4f} min")
            print(f" - Tiempo máximo de espera: {resultados['tiempo_maximo_espera']:.2f} min")
            print(f" - Cumple objetivo (≤6 min): {'✅ SÍ' if resultados['cumple_objetivo'] else '❌ NO'}")
            #print(f" - {resultados['distribucion_texto']}")
            print(f" - Intervalo de Confianza (99%):")
            print(f"     - Límite Inferior: {resultados['limite_inferior']:.4f}")
            print(f"     - Límite Superior: {resultados['limite_superior']:.4f}")
        
        # Exportar resultados
        exportar_resultados(resultados_experimento)
        
        # Recomendación final
        print(f"\n🎯 RECOMENDACIÓN FINAL:")
        print("=" * 60)
        
        empleados_optimos = None
        for config in [1, 2, 3]:
            if config in resultados_experimento and resultados_experimento[config]["cumple_objetivo"]:
                empleados_optimos = config
                break
        
        if empleados_optimos:
            print(f"Se recomienda contratar {empleados_optimos} empleado(s) para cumplir el objetivo de ≤6 min.")
            resultado_optimo = resultados_experimento[empleados_optimos]
            print(f"Con {empleados_optimos} empleado(s):")
            print(f"  - Tiempo máximo de espera: {resultado_optimo['tiempo_maximo_espera']:.2f} min")
            print(f"  - Pérdida de clientes: {resultado_optimo['porcentaje_perdida']:.2f}%")
        else:
            print("❌ Ninguna configuración cumple el objetivo de ≤6 min.")
            print("Se requiere análisis adicional o considerar más de 3 empleados.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 