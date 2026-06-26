# TRABAJO PRÁCTICO DE SIMULACIÓN
## Ferretería "JYL" - Optimización del Sistema de Atención al Cliente

---

### **CARÁTULA**

**Universidad:** [Nombre de la Universidad]  
**Materia:** Simulación  
**Profesores:** [Nombres de los profesores]  
**Estudiantes:** [Nombres de los estudiantes]  
**Fecha:** [Fecha de entrega]  
**Año:** 2025

---

## 📋 **1. OBJETIVOS DE LA SIMULACIÓN - FORMULACIÓN DEL PROBLEMA**

### **Escenario**

La ferretería "JYL", ubicada en Corrientes Capital, más precisamente en el barrio Sur, se dedica a la venta de artículos de ferretería, herramientas eléctricas y manuales, materiales eléctricos y productos de jardinería y sanitarios.

José, dueño de la ferretería, ha notado recientemente que durante ciertas horas del día se generan largas filas de clientes esperando para ser atendidos en el mostrador. Actualmente, la ferretería cuenta con solo un empleado encargado de asesorar a los clientes y procesar las ventas en caja.

Debido a esta situación, José está preocupado porque los tiempos largos de espera podrían estar afectando negativamente la satisfacción de sus clientes y, en consecuencia, las ventas del negocio. Por esta razón, ha decidido consultarnos con el objetivo de determinar cuántos empleados adicionales debería contratar para garantizar que ningún cliente espere más de **6 minutos**, teniendo en cuenta que por restricciones físicas la cantidad de empleados no puede ser mayor que **3**.

*Referencia: J&L Ferretería - Google Maps*

### **Objetivos de la Simulación**

Se busca determinar la **cantidad óptima de empleados** necesarios para atender a los clientes de la ferretería, con la finalidad de que el **tiempo máximo de espera** de cualquier cliente **no supere los 6 minutos**.

**Objetivos específicos:**
- Modelar el sistema de atención actual de la ferretería
- Analizar los tiempos de espera con diferentes configuraciones de empleados (1, 2, y 3 empleados)
- Identificar la configuración óptima que minimice los tiempos de espera
- Proporcionar recomendaciones basadas en evidencia estadística

---

## 🏗️ **2. DEFINICIÓN DEL SISTEMA**

El sistema de simulación abarca el **área de atención al público** de la ferretería, considerando los siguientes aspectos:

### **Componentes del Sistema:**
- **Número de empleados** disponibles para atender
- **Clientes** que llegan al local
- **Tiempo entre llegadas** de los clientes
- **Tiempo de atención** de cada cliente
- **Sistema de colas** de espera

### **Alcance Temporal:**
La información necesaria para realizar esta simulación se recolectó mediante grabaciones durante **dos turnos diarios**:
- **Turno Mañana:** 08:00 horas a 12:30 horas
- **Turno Tarde:** 16:30 a 20:30 horas

Durante los **5 días de la semana** (Lunes, Martes, Miércoles, Jueves y Viernes), registrando desde el momento en que los clientes ingresan al local hasta que son atendidos por orden de llegada, formando una **cola de espera secuencial**.

### **Suposiciones y Restricciones:**

#### **Suposiciones:**
- Los clientes se ubican en **una sola fila** de manera secuencial
- El empleado estará **disponible todo el tiempo**, sin periodos de descanso
- El **tiempo de atención no depende** del integrante del personal que lo realice
- **No se tienen en cuenta aspectos** relacionados con los productos en este modelo de simulación
- Los clientes llegan **por orden de llegada** y forman una cola FIFO (First In, First Out)

#### **Restricciones:**
- El local se considera **cerrado una vez que llega 20:30** y el mismo se encuentra sin clientes
- Si hay clientes en el sistema que llegaron **antes de las 20:30** aún siguen y serán atendidos
- Por **restricciones físicas** no podrán haber más de **3 empleados** detrás del mostrador

---

## 🔧 **3. FORMULACIÓN DEL MODELO**

### **Tipo de Modelo:**
- **Modelo de simulación de eventos discretos**
- **Sistema de colas M/M/c** (llegadas aleatorias, servicios aleatorios, c servidores)
- **Disciplina de cola:** FIFO (First In, First Out)

### **Variables del Modelo:**

#### **Variables de Estado:**
- `tiempo_simulacion`: Reloj principal de la simulación
- `personas_en_sistema(i)`: Número de clientes en cola del servidor i
- `personas_totales_sistema`: Total de clientes en todo el sistema
- `tiempo_proxima_llegada`: Momento de la próxima llegada
- `tiempo_proxima_salida(i)`: Momento de finalización del servicio en servidor i

#### **Variables de Performance:**
- `suma_tiempo_permanencia`: Acumulador de tiempo total en sistema
- `suma_tiempo_atencion(i)`: Acumulador de tiempo de servicio por servidor
- `personas_atendidas`: Contador de clientes procesados

#### **Parámetros del Modelo:**
- `cantidad_servidores`: Número de empleados (1, 2, o 3)
- `tiempo_fin`: Duración de la simulación

### **Eventos del Sistema:**
1. **Evento Llegada:** Un cliente ingresa al sistema
2. **Evento Salida:** Un cliente completa su servicio y abandona el sistema

---

## 📊 **4. COLECCIÓN DE DATOS**

### **Identificación de Variables**

Se definieron las siguientes variables para el análisis del sistema de atención en el local comercial:

#### **Variables Aleatorias:**
- **FDP (TeLL):** Tiempo entre Llegadas
  - Intervalo, en minutos, entre la llegada de un cliente y el siguiente
  
- **FDP (TA):** Tiempo de Atención  
  - Duración, en minutos, del proceso de atención a cada cliente, desde el pedido hasta la entrega del producto y/o comprobante

#### **Variables de Control:**
- **n:** Cantidad de empleados presentes durante el turno (registrado a efectos de control interno)

### **Recolección de Datos**

La recolección de datos se realizó mediante el **análisis de registros de cámaras de seguridad**, en el período comprendido entre el **27/05/2025 y el 14/06/2025** inclusive.

#### **Procedimiento:**

1. **Tiempo entre Llegadas (TeLL):** 
   - Se registró el horario de ingreso de cada cliente al local
   - Se calculó la diferencia, en minutos, entre cada cliente y el siguiente

2. **Tiempo de Atención (TA):** 
   - Se contabilizó desde el momento en que el cliente realizó el pedido
   - Hasta que recibió el producto, el ticket (si correspondiera), y el vuelto

**Nota:** Los valores de "TeLL" y "TA" fueron extraídos manualmente a partir de los vídeos grabados, mediante observación directa del comportamiento del cliente en el punto de atención.

*A continuación, se muestra una porción del cuadro de recolección de datos. La tabla completa puede encontrarse en el archivo anexo.*

### **Identificación de la Distribución de Probabilidad**

Con el objetivo de modelar de manera adecuada los tiempos registrados en el sistema de cámaras de la ferretería, se procedió al **análisis estadístico de los datos** utilizando la herramienta **StatFit** incluida en ProModel.

#### **Segmentación de Datos:**
Tras una primera inspección de los datos crudos, se observaron **diferencias claras** en el rango y la dispersión de los intervalos entre llegadas en turno mañana y turno tarde, por lo que se decidió **segmentar los datos** en esos dos periodos antes del ajuste de distribución.

#### **Proceso de Análisis:**
StatFit evaluó varias distribuciones candidatas (Uniforme Discreta, Geométrica, Poisson), asignando un índice de ajuste (rank) y una decisión estadística de aceptación o rechazo en función de pruebas de bondad de ajuste.

#### **Resultados:**
- **Tiempo entre llegadas turno mañana:** Distribución **Uniforme Discreta entre 1 y 14**
- **Tiempo entre llegadas turno tarde:** Distribución **Uniforme Discreta entre 4 y 20**  
- **Tiempo de atención:** Distribución **Uniforme Discreta entre 3 y 20**

En los tres casos, la **distribución uniforme fue la única no rechazada**, lo que indica que los datos están adecuadamente modelados por una distribución uniforme discreta, donde todos los valores posibles tienen igual probabilidad.

---

## 💻 **5. IMPLEMENTACIÓN DEL MODELO EN LA COMPUTADORA**

### **Generación de Valores para las Variables Aleatorias**

#### **Método Utilizado:**
Con el objetivo de generar valores que representen el comportamiento de las variables aleatorias identificadas, se aplicó el **método de la función inversa**: una técnica estándar que permite generar valores aleatorios con una distribución específica a partir de un número aleatorio uniforme `ri` en el intervalo [0,1).

#### **Fundamento Matemático:**
Para la distribución uniforme:

```
f(x) = 1/(b-a)    (función de densidad)

F(x) = (x-a)/(b-a) = ri    (función de distribución acumulada)

⇒ xi = a + (b-a)ri    (función inversa)
```

**Donde:**
- `xi` es el valor simulado de la variable aleatoria
- `a` es el mínimo de la distribución
- `b` es el máximo de la distribución  
- `ri` es un número pseudoaleatorio uniforme generado

#### **Funciones de Generación:**

```
FDP(TeLL TM) → xi = 1 + 13ri     (Turno Mañana)
FDP(TeLL TT) → xi = 4 + 16ri     (Turno Tarde)  
FDP(TA)      → xi = 3 + 17ri     (Tiempo Atención)
```

Estas funciones tienen como entrada los **números pseudoaleatorios validados**, que actúan como materia prima, los cuales, al ser transformados mediante la función correspondiente, permiten obtener valores que siguen la distribución de probabilidad identificada para cada variable, garantizando así la coherencia del modelo de simulación con el comportamiento observado en el sistema real.

### **Variables del Algoritmo**

#### **Variables de Estado del Sistema:**
| Variable | Descripción | Tipo | Rango |
|----------|-------------|------|-------|
| `tiempo_simulacion` | Reloj principal de la simulación | Real | [0, tiempo_fin] |
| `personas_en_sistema(i)` | Número de clientes en cola del servidor i | Entero | [0, ∞) |
| `personas_totales_sistema` | Total de clientes en todo el sistema | Entero | [0, ∞) |
| `tiempo_proxima_llegada` | Momento de la próxima llegada | Real | [0, ∞) |
| `tiempo_proxima_salida(i)` | Momento de finalización del servicio en servidor i | Real | [0, ∞) ∪ {∞} |

#### **Variables Acumuladoras:**
| Variable | Descripción | Tipo | Propósito |
|----------|-------------|------|-----------|
| `suma_tiempo_permanencia` | Acumulador de tiempo total en sistema | Real | Calcular tiempo promedio permanencia |
| `suma_tiempo_atencion(i)` | Acumulador de tiempo de servicio por servidor | Real | Calcular tiempo promedio atención |
| `personas_atendidas` | Contador de clientes procesados completamente | Entero | Estadísticas finales |

#### **Variables de Control:**
| Variable | Descripción | Tipo | Valores |
|----------|-------------|------|---------|
| `cantidad_servidores` | Número de empleados activos | Entero | {1, 2, 3} |
| `tiempo_fin` | Duración total de la simulación | Real | 510 min (mañana + tarde) |
| `turno_actual` | Identificador del turno en curso | String | {"mañana", "tarde"} |

#### **Variables de Entrada (Aleatorias):**
| Variable | Descripción | Distribución | Parámetros |
|----------|-------------|--------------|------------|
| `tiempo_entre_arribos` | Intervalo entre llegadas consecutivas | Uniforme Discreta | Mañana: [1,14], Tarde: [4,20] |
| `tiempo_atencion` | Duración del servicio a un cliente | Uniforme Discreta | [3,20] |

#### **Variables de Salida (Métricas):**
| Variable | Descripción | Tipo | Objetivo |
|----------|-------------|------|----------|
| `tiempo_promedio_permanencia` | Tiempo promedio que un cliente permanece en sistema | Real | Minimizar |
| `tiempo_maximo_espera` | Máximo tiempo de espera registrado | Real | ≤ 6 minutos |
| `tiempo_promedio_atencion` | Tiempo promedio de servicio | Real | Información |
| `clientes_atendidos_total` | Total de clientes procesados en la simulación | Entero | Throughput |

<!-- COMENTADO: Variables de ocupación de empleados
#### **Variables de Ocupación (Futuro):**
| Variable | Descripción | Tipo | Propósito |
|----------|-------------|------|-----------|
| `porcentaje_ocupacion(i)` | % de tiempo que servidor i está ocupado | Real | Eficiencia |
| `tiempo_ocioso(i)` | Tiempo total que servidor i está libre | Real | Análisis de recursos |
-->

---

## ✅ **6. VERIFICACIÓN**

*[Esta sección se completará con los resultados de verificación del modelo]*

---

## ✅ **7. VALIDACIÓN**

*[Esta sección se completará con los resultados de validación del modelo]*

---

## 🧪 **8. DISEÑO DE EXPERIMENTO**

### **Configuración del Experimento:**

Se realizarán simulaciones con las siguientes características:

#### **Parámetros de Simulación:**
- **Número de corridas:** 50 corridas por cada configuración de empleados
- **Duración de cada corrida:** 1 mes
- **Días hábiles por mes:** 20 días
- **Turnos por día hábil:** 2 turnos

#### **Duración de Turnos:**
- **Turno Mañana:** 270 minutos (4:30 horas)
- **Turno Tarde:** 240 minutos (4:00 horas)

#### **Configuraciones a Evaluar:**
Las sucesivas simulaciones se irán realizando incorporando **de a 1 empleado** a la vez, teniendo en cuenta la restricción física del local, hasta lograr el objetivo planteado.

**Secuencia de experimentos:**
1. **Configuración 1:** 1 empleado (situación actual)
2. **Configuración 2:** 2 empleados 
3. **Configuración 3:** 3 empleados (máximo por restricción física)

#### **Criterios de Evaluación:**
- **Objetivo principal:** Tiempo máximo de espera ≤ 6 minutos
- **Error admisible:** Hasta el 5%
- **Métricas a evaluar:**
  - Tiempo promedio de espera
  - Tiempo máximo de espera
  - Porcentaje de ocupación de empleados
  - Número de clientes atendidos por turno

---

## 🔬 **9. EXPERIMENTACIÓN**

*[Esta sección se completará con los resultados de la experimentación]*

---

## 📈 **10. INTERPRETACIÓN**

*[Esta sección se completará con el análisis e interpretación de resultados]*

---

## 📎 **ANEXOS**

- Tablas completas de recolección de datos
- Resultados detallados de StatFit
- Código de simulación
- Gráficos y análisis estadísticos

---

*Documento generado en formato Markdown para facilitar la edición y versionado del trabajo práctico.* 