# Documentación del Diagrama de Simulación - Ferretería
## Simulación de Eventos Discretos para Sistema de Colas

---

## 📋 **Introducción**

Este documento explica paso a paso el funcionamiento del diagrama de simulación evento a evento para una ferretería con múltiples servidores y colas. El objetivo es determinar cuántos empleados se necesitan para mantener los tiempos de espera bajo 10 minutos.

---

## 🚀 **1. INICIALIZACIÓN DEL SISTEMA**

### Variables Iniciales:
```
tiempo_simulacion = 0                 // Reloj de la simulación
tiempo_proxima_llegada = 0           // Próximo cliente que llega
personas_en_sistema = 0              // Personas totales en el sistema
cantidad_servidores = n              // Número de empleados/servidores
suma_tiempo_permanencia = 0          // Acumulador tiempo en sistema
suma_tiempo_atencion = 0             // Acumulador tiempo de servicio
personas_atendidas = 0               // Contador de clientes atendidos
vi = 1..n                           // Índices para cada servidor
```

### Estado Inicial:
- Sistema vacío (sin clientes)
- Todos los servidores libres
- Contadores en cero
- Listo para comenzar la simulación

---

## 🔄 **2. BUCLE PRINCIPAL DE SIMULACIÓN**

**Condición del bucle:** `tiempo_simulacion < tiempo_fin`

El bucle continúa hasta alcanzar el tiempo límite de simulación establecido.

### 2.1 **Identificación del Próximo Evento**

```
Buscar el menor tiempo_proxima_salida_i
k = argmin(TPS[1..n])
```

**Propósito:** Determinar cuál servidor terminará primero su servicio actual.

---

## 🌟 **3. DECISIÓN PRINCIPAL: ¿LLEGADA O SALIDA?**

### Condición: `tiempo_proxima_llegada <= tiempo_proxima_salida_k`

---

## 🔵 **CAMINO A: EVENTO DE LLEGADA** (SI)

### 3.1 **Actualización del Tiempo del Sistema**
```
suma_tiempo_permanencia += (tiempo_proxima_llegada - tiempo_simulacion) * personas_totales_sistema
tiempo_simulacion = tiempo_proxima_llegada
```

**Explicación:** 
- Calcula el tiempo que todas las personas actuales permanecieron en el sistema
- Avanza el reloj de simulación al momento de la llegada

### 3.2 **Generación del Próximo Cliente**
```
Generar tiempo_entre_arribos
tiempo_proxima_llegada = tiempo_simulacion + tiempo_entre_arribos
```

**Explicación:** Programa cuándo llegará el siguiente cliente (distribución uniforme discreta por turnos).

### 3.3 **Asignación de Cola**
```
Buscar en Cola del Menor cantidad de Personas
```

**Algoritmo:** El cliente elige la cola con menor número de personas esperando.

### 3.4 **Proceso de Arrepentimiento**
```
Tratar Arrepentimiento
```

**Rangos de decisión:**
- **15+ min de espera:** 20% se va (80% se queda)
- **20+ min de espera:** 45% se va (55% se queda)  
- **25+ min de espera:** 96% se va (4% se queda)

**Caminos posibles:**
- **Cliente se va:** Sale del sistema sin ser atendido
- **Cliente se queda:** Continúa al siguiente paso

### 3.5 **Incorporación al Sistema** (Solo si no se arrepiente)
```
personas_en_sistema(k) += 1
personas_totales_sistema += 1
```

### 3.6 **Decisión de Atención Inmediata**

**Condición:** `personas_en_sistema(k) = 1`

#### 🟢 **CAMINO A1: SERVIDOR LIBRE** (SI)
```
Generar tiempo_atencion
tiempo_proxima_salida(k) = tiempo_simulacion + tiempo_atencion
suma_tiempo_atencion(k) += tiempo_atencion
```

**Explicación:** 
- El cliente es atendido inmediatamente
- Se genera un tiempo de servicio aleatorio
- Se programa cuándo terminará el servicio

#### 🟡 **CAMINO A2: SERVIDOR OCUPADO** (NO)
```
// Cliente va a cola, no se asigna tiempo de servicio aún
```

**Explicación:** 
- El cliente espera en la cola
- No se genera tiempo de servicio hasta que sea su turno

---

## 🔴 **CAMINO B: EVENTO DE SALIDA** (NO)

### 3.1 **Actualización del Tiempo del Sistema**
```
suma_tiempo_permanencia += (tiempo_proxima_salida(k) - tiempo_simulacion) * personas_totales_sistema
tiempo_simulacion = tiempo_proxima_salida(k)
```

**Explicación:** 
- Calcula el tiempo de permanencia de todos los clientes actuales
- Avanza el reloj al momento de la salida

### 3.2 **Liberación del Cliente**
```
personas_en_sistema(k) -= 1
```

**Explicación:** Un cliente termina su servicio y sale del sistema.

### 3.3 **Decisión de Próximo Servicio**

**Condición:** `personas_en_sistema(k) >= 1`

#### 🟢 **CAMINO B1: HAY COLA** (SI)
```
Generar tiempo_atencion
tiempo_proxima_salida(k) = tiempo_simulacion + tiempo_atencion
suma_tiempo_atencion(k) += tiempo_atencion
```

**Explicación:**
- Hay clientes esperando en cola
- El siguiente cliente comienza a ser atendido inmediatamente
- Se genera un nuevo tiempo de servicio

#### 🟡 **CAMINO B2: NO HAY COLA** (NO)
```
tiempo_proxima_salida(k) = INFINITO
```

**Explicación:**
- No hay más clientes en esta cola
- El servidor queda libre
- Se marca como "sin próxima salida programada"

---

## 🏁 **4. FINALIZACIÓN DE LA SIMULACIÓN**

### Condición de Salida: `tiempo_simulacion >= tiempo_fin`

### 4.1 **Cálculo de Estadísticas Finales**
```
promedio_tiempo_permanencia = suma_tiempo_permanencia / personas_atendidas
promedio_tiempo_atencion = suma_tiempo_atencion / personas_atendidas  
porcentaje_ocupacion = suma_tiempo_atencion / tiempo_simulacion
```

### 4.2 **Métricas Clave para la Ferretería**
- **Tiempo promedio de espera:** Para evaluar si < 10 minutos
- **Porcentaje de ocupación:** Eficiencia de los empleados
- **Tiempo promedio de atención:** Duración típica del servicio

---

## 🗺️ **5. RESUMEN DE TODOS LOS CAMINOS POSIBLES**

### **Mapa de Decisiones:**

```
INICIALIZACIÓN
    ↓
┌─── BUCLE PRINCIPAL ────┐
│   ↓                    │
│   Buscar menor TPS     │
│   ↓                    │
│   ¿Llegada ≤ Salida?   │
│   ↓                    │
│ ┌─SI─┐        ┌─NO─┐   │
│ │    │        │    │   │
│ │ LLEGADA     │ SALIDA │ │
│ │    │        │    │   │
│ │ ┌─ Arrepentimiento   │ │
│ │ │  ├─Se va           │ │
│ │ │  └─Se queda        │ │
│ │ │     ↓              │ │
│ │ │  ¿Servidor libre?  │ │
│ │ │  ├─SI: Atención    │ │
│ │ │  └─NO: A cola      │ │
│ │                     │ │
│ │              ¿Hay cola? │
│ │              ├─SI: Siguiente │
│ │              └─NO: Servidor libre │
│ └─────────────────────┘ │
│   ↓                    │
│   ¿Tiempo < Fin?       │
│   ├─SI: Continuar ─────┘
│   └─NO: Finalizar
│       ↓
    ESTADÍSTICAS FINALES
```

---

## 📊 **6. ANÁLISIS DE RENDIMIENTO**

### **Indicadores Clave:**
- **Tiempo de espera < 10 min:** Objetivo principal
- **Tasa de arrepentimiento:** Pérdida de clientes
- **Utilización de servidores:** Eficiencia operativa
- **Tiempo total en sistema:** Experiencia del cliente

### **Optimización:**
El diagrama permite evaluar diferentes valores de `n` (cantidad de servidores) para encontrar el número óptimo de empleados que minimice los tiempos de espera manteniendo la eficiencia operativa.

---

## 🎯 **7. APLICACIÓN PRÁCTICA**

### **Para la Ferretería:**
1. **Ejecutar simulación** con diferentes números de empleados (n = 1, 2, 3...)
2. **Medir tiempo promedio de espera** en cada escenario
3. **Identificar el n mínimo** donde tiempo de espera < 10 minutos
4. **Considerar costos** vs beneficios de empleados adicionales
5. **Validar con datos reales** del comportamiento de clientes

---

## 🔍 **8. ANÁLISIS DETALLADO DEL FLUJO DEL DIAGRAMA MEJORADO**

### **8.1 MECANISMO DE DECISIÓN: ¿LLEGADA O SALIDA?**

#### **¿Cómo funciona la comparación de tiempos?**

```
if (tiempo_proxima_llegada ≤ tiempo_proxima_salida(k))
```

**Explicación paso a paso:**

1. **`tiempo_proxima_llegada`**: Es el momento exacto cuando llegará el próximo cliente
   - Se calcula: `tiempo_actual + tiempo_entre_arribos`
   - **Ejemplo**: Si estamos en t=45 min y el tiempo entre arribos es 3 min → próxima llegada = 48 min

2. **`tiempo_proxima_salida(k)`**: Es el momento cuando el servidor k terminará de atender
   - Se calcula: `tiempo_inicio_servicio + tiempo_atencion`
   - **Ejemplo**: Si servidor 2 empezó a atender en t=44 min con tiempo de servicio 6 min → próxima salida = 50 min

3. **La decisión**: 48 min ≤ 50 min → **SÍ** → Procesar **LLEGADA**

**¿Por qué esta lógica?**
- La simulación **siempre procesa el evento más cercano en el tiempo**
- Garantiza el orden cronológico correcto de eventos
- Si hay empate (≤), se da prioridad a las llegadas para evitar bias

---

### **8.2 CÁLCULO DE LA SUMA DE TIEMPO DE PERMANENCIA**

#### **Fórmula Completa:**
```
suma_tiempo_permanencia += (tiempo_evento - tiempo_simulacion) * personas_totales_sistema
```

**¿Qué significa cada parte?**

1. **`(tiempo_evento - tiempo_simulacion)`**: 
   - **Duración del intervalo** entre el evento anterior y el actual
   - **Ejemplo**: De t=45 min a t=48 min = 3 minutos

2. **`personas_totales_sistema`**: 
   - **Cantidad de personas** que estuvieron en el sistema durante ese intervalo
   - **Incluye**: personas siendo atendidas + personas en cola

3. **El producto**: 
   - **Tiempo total acumulado** de todas las personas en el sistema
   - **Ejemplo**: 3 min × 7 personas = 21 persona-minutos

**Ejemplo Detallado:**
```
Situación en t=45: 7 personas en sistema
Próximo evento en t=48: Nueva llegada
Cálculo: (48-45) × 7 = 21 persona-minutos se suman al acumulador
```

**¿Por qué este cálculo?**
- Permite calcular el **tiempo promedio de permanencia** al final
- Fórmula final: `tiempo_promedio = suma_tiempo_permanencia / personas_atendidas`

---

### **8.3 GENERACIÓN DE TIEMPO ENTRE ARRIBOS POR TURNOS**

#### **Rangos Uniformes Según Horario:**

```
Generar tiempo_entre_arribos:
```

**📅 TURNO MAÑANA (8:00 - 12:00)**
- **Rango**: Uniforme(1, 4) minutos
- **Justificación**: Menor affluencia, clientes espaciados
- **Comportamiento**: Llegadas más predecibles y tranquilas

**🌞 TURNO TARDE (12:00 - 18:00)**  
- **Rango**: Uniforme(0.5, 2) minutos
- **Justificación**: Hora pico, alta demanda
- **Comportamiento**: Llegadas frecuentes y concentradas

**Implementación en código:**
```pseudocode
hora_actual = tiempo_simulacion % 1440  // Convertir a minutos del día

if (hora_actual >= 480 && hora_actual < 720)      // 8:00-12:00
    tiempo_entre_arribos = Uniforme(1, 4)
else if (hora_actual >= 720 && hora_actual < 1080) // 12:00-18:00  
    tiempo_entre_arribos = Uniforme(0.5, 2)
else if (hora_actual >= 1080 && hora_actual < 1320) // 18:00-22:00
    tiempo_entre_arribos = Uniforme(2, 6)
```

---

### **8.4 SECUENCIA COMPLETA DE DECISIONES**

#### **Diagrama de Decisión Detallado:**

```
┌─────────────────────────────────────────────────────────────┐
│                    INICIO DE ITERACIÓN                      │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Buscar k = argmin(tiempo_proxima_salida[1..n])     │
│  Resultado: k = servidor con menor tiempo de salida         │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: Comparar tiempo_proxima_llegada ≤ tiempo_proxima_  │
│          salida(k)                                          │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
              ┌───────────────┐
              │ ¿Llegada ≤    │
              │ Salida(k)?    │
              └─────┬─────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
    ┌───────┐               ┌───────┐
    │  SÍ   │               │  NO   │
    │LLEGADA│               │SALIDA │
    └───┬───┘               └───┬───┘
        │                       │
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ RAMA LLEGADA:    │    │ RAMA SALIDA:     │
│                  │    │                  │
│ 1. Actualizar    │    │ 1. Actualizar    │
│    suma_tiempo_  │    │    suma_tiempo_  │
│    permanencia   │    │    permanencia   │
│                  │    │                  │
│ 2. Avanzar reloj │    │ 2. Avanzar reloj │
│    tiempo_sim =  │    │    tiempo_sim =  │
│    tiempo_prox_  │    │    tiempo_prox_  │
│    llegada       │    │    salida(k)     │
│                  │    │                  │
│ 3. Generar nuevo │    │ 3. Liberar       │
│    tiempo_entre_ │    │    cliente:      │
│    arribos       │    │    personas_en_  │
│    (por turno)   │    │    sistema(k)--  │
│                  │    │                  │
│ 4. Asignar cola  │    │ 4. ¿Hay cola?    │
│    menor cantidad│    │    ┌─SÍ─┐ ┌─NO─┐ │
│                  │    │    │    │ │    │ │
│ 5. Arrepentimi-  │    │    ▼    │ ▼    │ │
│    ento (15+,    │    │ Atender │ TPS= │ │
│    20+, 25+ min) │    │ próximo │ ∞    │ │
│                  │    │         │      │ │
│ 6. ¿Se queda?    │    │         │      │ │
│    ┌─SÍ─┐ ┌─NO─┐ │    │         │      │ │
│    │    │ │Sale│ │    │         │      │ │
│    ▼    │ │sin │ │    │         │      │ │
│ Personas│ │aten│ │    │         │      │ │
│ _en_sis-│ │der │ │    │         │      │ │
│ tema(k)+│ │    │ │    │         │      │ │
│         │ │    │ │    │         │      │ │
│ 7. ¿Serv│ │    │ │    │         │      │ │
│    libre?│    │ │    │         │      │ │
│ ┌─SÍ─┐  │ │    │ │    │         │      │ │
│ │    │  │ │    │ │    │         │      │ │
│ ▼    │  │ │    │ │    │         │      │ │
│Aten- │  │ │    │ │    │         │      │ │
│ción  │  │ │    │ │    │         │      │ │
│inme- │  │ │    │ │    │         │      │ │
│diata │  │ │    │ │    │         │      │ │
│      │  │ │    │ │    │         │      │ │
│ ┌─NO─┐  │ │    │ │    │         │      │ │
│ │    │  │ │    │ │    │         │      │ │ 
│ ▼    │  │ │    │ │    │         │      │ │
│A cola│  │ │    │ │    │         │      │ │
└──────┼──┼─┼────┼─┘    └─────────┼──────┼─┘
       │  │ │    │                │      │
       └──┴─┴────┴────────────────┴──────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  ¿tiempo_simulacion <       │
        │   tiempo_fin?               │
        └─────────────┬───────────────┘
                      │
              ┌───────┴────────┐
              ▼                ▼
          ┌───────┐        ┌───────┐
          │  SÍ   │        │  NO   │
          │CONTI- │        │TERMI- │
          │NUAR   │        │NAR    │
          └───┬───┘        └───┬───┘
              │                │
              │                ▼
              │      ┌──────────────────┐
              │      │ ESTADÍSTICAS     │
              │      │ FINALES          │
              │      └──────────────────┘
              │
              └──────────────┐
                             │
              ┌──────────────┴──────────────┐
              │     REGRESA AL INICIO       │
              │    (Nueva iteración)        │
              └─────────────────────────────┘
```

---

### **8.5 CASOS ESPECÍFICOS Y EJEMPLOS**

#### **Ejemplo 1: Procesamiento de Llegada**
```
Estado inicial:
- tiempo_simulacion = 120 min
- tiempo_proxima_llegada = 125 min  
- tiempo_proxima_salida(1) = 130 min
- tiempo_proxima_salida(2) = 128 min
- personas_totales_sistema = 5

Paso 1: k = argmin([130, 128]) = 2
Paso 2: 125 ≤ 128 → SÍ → EVENTO LLEGADA

Ejecución:
1. suma_tiempo_permanencia += (125-120) × 5 = 25
2. tiempo_simulacion = 125
3. Generar tiempo_entre_arribos según turno
4. Si turno tarde: Uniforme(0.5, 2) → suponer 1.5 min
5. tiempo_proxima_llegada = 125 + 1.5 = 126.5
6. Asignar a cola con menos gente
7. Evaluar arrepentimiento...
```

#### **Ejemplo 2: Procesamiento de Salida**
```
Estado inicial:
- tiempo_simulacion = 125 min
- tiempo_proxima_llegada = 126.5 min
- tiempo_proxima_salida(1) = 130 min  
- tiempo_proxima_salida(2) = 126 min
- personas_en_sistema(2) = 3

Paso 1: k = argmin([130, 126]) = 2
Paso 2: 126.5 ≤ 126 → NO → EVENTO SALIDA

Ejecución:
1. suma_tiempo_permanencia += (126-125) × 6 = 6
2. tiempo_simulacion = 126
3. personas_en_sistema(2) = 3 - 1 = 2
4. Como personas_en_sistema(2) ≥ 1 → Hay cola
5. Generar nuevo tiempo_atencion → suponer 4 min
6. tiempo_proxima_salida(2) = 126 + 4 = 130
```

---

*Esta sección proporciona el entendimiento completo del flujo lógico del diagrama mejorado, permitiendo implementar correctamente la simulación y comprender cada decisión del algoritmo.* 