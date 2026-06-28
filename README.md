# 🚚 Simulador de Inventario - Entrega Pet 🐶🐱
Este repositorio contiene el desarrollo del Trabajo Práctico de Simulación para la optimización del sistema de inventario de la sucursal Resistencia de **Entrega Pet**, enfocado en el producto estrella de temporada alta: **Vital Can Premium Perro Adulto 20 kg**.

El objetivo principal es comparar múltiples combinaciones de **Punto de Emisión de Pedido (PEP)** y **Tamaño de Pedido (TP)** para encontrar la de menor **Costo Total de Funcionamiento (CTF)**. La primera alternativa es la indicada en la planilla de referencia: `(PEP = 5, TP = 20)`.

---

## 📋 Contenidos
1. [Objetivos de la Simulación](#-objetivos-de-la-simulación)
2. [Definición del Sistema y Variables](#-definición-del-sistema-y-variables)
3. [Generador de Números Pseudoaleatorios (Multiplicador Constante)](#-generador-de-números-pseudoaleatorios-multiplicador-constante)
4. [Lógica y Estructura del Simulador](#-lógica-y-estructura-del-simulador)
5. [Experimentación e intervalo de confianza](#-experimentación-e-intervalo-de-confianza-del-95)
6. [Estructura del Repositorio](#-estructura-del-repositorio)
7. [Instrucciones de Uso](#-instrucciones-de-uso)

---

## 🎯 Objetivos de la Simulación
*   **Objetivo Principal:** Minimizar el Costo Total de Funcionamiento (CTF) del sistema de inventario para bolsas de 20 kg de Vital Can Premium Perro Adulto.
*   **Objetivos Específicos:**
    *   Modelar el comportamiento de la demanda diaria y los tiempos de entrega del proveedor mediante variables aleatorias.
    *   Evaluar distintas políticas de control de inventario, comenzando por `(PEP = 5, TP = 20)`.
    *   Encontrar el mejor balance entre costos de almacenamiento, emisión de pedidos y ventas perdidas (costos de oportunidad).
    *   Comparar estadísticamente el costo total mediante 50 corridas de 180 días para cada combinación PEP/TP seleccionada.

---

## 🏗️ Definición del Sistema y Variables

### Variables Exógenas (Parámetros y Costos)
*   **Costo de Almacenamiento ($CALM$):** $\$500$ por bolsa al día (aplicado sobre el stock remanente al final del día).
*   **Costo por Venta Perdida ($CVP$):** $\$10,000$ por bolsa no entregada por falta de stock, según el ejemplo del Excel (5 ventas perdidas = $50.000).
*   **Costo por Emisión de Pedido ($CEP$):** $\$5,000$ por cada orden de compra enviada al proveedor.
*   **Demanda Diaria ($DD$):** Variable aleatoria con distribución de **Poisson** ($\lambda = 2.05$ bolsas/día).
*   **Lead Time ($LT$):** Variable aleatoria con distribución **Uniforme Discreta** $[7, 14]$ días.

### Variables de Control (Alternativas de Decisión)
*   **Punto de Emisión de Pedido ($PEP$):** Nivel bajo de stock a partir del cual se dispara una orden de reposición.
*   **Tamaño del Pedido ($TP$):** Cantidad de bolsas que se solicitan en cada orden.
*   **Pares evaluados:** 10 combinaciones elegidas para cubrir extremos, puntos medios e interiores: `(5,15)`, `(5,25)`, `(10,15)`, `(10,25)`, `(5,20)`, `(10,20)`, `(7,19)`, `(7,21)`, `(8,19)` y `(8,21)`.

### Variables Endógenas (De Estado y Salida)
*   **$T$:** Reloj de simulación en días.
*   **$ST$:** Stock físico disponible de bolsas en el día $T$.
*   **$FLL$:** Fecha de llegada programada del próximo pedido al depósito (si $FLL \le T$, significa que no hay pedidos pendientes en tránsito).
*   **$CTALM$, $CVTAP$, $CTEP$:** Costos acumulados de almacenamiento, ventas perdidas y emisión de pedidos respectivamente.
*   **$CTF$:** Costo Total de Funcionamiento acumulado ($CTF = CTALM + CVTAP + CTEP$).
*   **$NS$ (Nivel de Servicio):** Porcentaje de la demanda de los clientes que pudo ser satisfecha directamente del stock.

---

## 🎲 Generador de Números Pseudoaleatorios (Multiplicador Constante)
El generador se implementa en [generador_numeros_pet.py](file:///C:/Users/rodri/OneDrive/Desktop/simu%20tpi/Simulacion-2026/generador_numeros_pet.py) utilizando el **Método del Multiplicador Constante** de 4 dígitos.

### Algoritmo del Generador
1. Se toma una semilla inicial $X_i$ y una constante multiplicadora $a$.
2. Se calcula el producto $Y = X_i \times a$.
3. Se rellena $Y$ con ceros a la izquierda hasta completar $8$ dígitos en formato de texto.
4. Se extraen los $4$ dígitos centrales (índices 2 a 5 inclusive) para conformar la nueva semilla $X_{i+1}$.
5. El número pseudoaleatorio resultante en el intervalo $[0, 1)$ es $R_i = X_{i+1} / 10000.0$.

### Configuración del Generador
*   **Demanda Diaria ($DD$):** Semilla $X_0 = 2026$, Multiplicador $a = 5324$ (Genera `numeros_demanda.csv`).
*   **Lead Time ($LT$):** Semilla $X_0 = 1754$, Multiplicador $a = 4813$ (Genera `numeros_lead_time.csv`).

### Pruebas de Validación Estadística
Cada secuencia de 10,000 números generada se somete a validación estadística con un nivel de significación del 5% ($\alpha = 0.05$):
*   **Prueba de la Media:** Valida si el valor medio se aproxima a $0.5$.
*   **Prueba de la Varianza:** Valida si la varianza es cercana a $1/12 \approx 0.0833$.
*   **Prueba de Chi-Cuadrado ($\chi^2$):** Valida la hipótesis de distribución uniforme en 10 intervalos equiprobables.
*   **Prueba de Corridas (Arriba y Abajo):** Evalúa la independencia de la secuencia.

---

## 💻 Lógica y Estructura del Simulador
El simulador funciona bajo el método de **Incremento de Tiempo Constante** ($\Delta T = 1$ día) durante un período de **$TF = 180$ días**. Su flujo se detalla en [simulador_pet.py](file:///C:/Users/rodri/OneDrive/Desktop/simu%20tpi/Simulacion-2026/simulador_pet.py):

```
                   [ Inicio de la Simulación ]
                               │
                ┌──────────────┴──────────────┐
                │    Condiciones Iniciales    │
                │ ST = 0, FLL = 1, PP = True  │
                │ T = 0                        │
                │ Costos Acumulados = 0       │
                └──────────────┬──────────────┘
                               │
                   ┌──────────>│ T = T + 1
                   │           │
                   │     ¿T == FLL? (Llega Pedido)
                   │         ├─── [ SÍ ] ───> ST = ST + TP
                   │         │                PP = False
                   │         └─── [ NO ] ───┐
                   │                        │
                   │       ┌────────────────┘
                   │       │
                   │  Generar Demanda Diaria (DD)
                   │  (Poisson por Transformada Inversa)
                   │       │
                   │     ¿ST >= DD?
                   │         ├─── [ SÍ ] ───> ST = ST - DD
                   │         │                CTALM += ST * CALM
                   │         │
                   │         └─── [ NO ] ───> VP = DD - ST
                   │                          CVTAP += VP * CVP
                   │                          ST = 0
                   │       ┌────────────────┘
                   │       │
                   │     ¿ST <= PEP y PP = False?
                   │         ├─── [ SÍ ] ───> Generar Lead Time uniforme [7, 14]
                   │         │                FLL = T + LT
                   │         │                CTEP += CEP
                   │         │                PP = True
                   │         └─── [ NO ] ───┐
                   │                        │
                   │       ┌────────────────┘
                   │       │
                   └───── ¿T < TF?
                             │ [ NO ]
                             │
                ┌────────────┴────────────┐
                │ Calcular Costo Total    │
                │ CTF = CTALM+CVTAP+CTEP  │
                └────────────┬────────────┘
                             │
                         [ Fin ]
```

### Simulación de Políticas
Para cada uno de los 10 pares `(PEP, TP)` se ejecutan **50 corridas de 180 días**. Todas las políticas reciben los mismos escenarios pseudoaleatorios para que la comparación dependa de la decisión evaluada. `simulador_pet.py` muestra en la terminal el análisis completo y crea un único libro Excel con las hojas `Resumen IC`, `Evolución IC`, `Réplicas` y una hoja diaria por cada par.

---

## 📊 Experimentación e intervalo de confianza del 95%

El archivo `experimento_intervalo_confianza.py` complementa la comparación inicial con un análisis estadístico de las variables de salida. El experimento reducido evalúa **10 pares PEP/TP** y genera hasta **50 réplicas de 180 días por cada par**, para un máximo de 500 simulaciones. La selección cubre los extremos y el centro del espacio de decisión: las cuatro esquinas `(5,15)`, `(5,25)`, `(10,15)` y `(10,25)`; los puntos medios `(5,20)` y `(10,20)`; y cuatro puntos interiores `(7,19)`, `(7,21)`, `(8,19)` y `(8,21)`.

La comparación se realiza progresivamente con $N \in \{10,20,30,40,50\}$. En cada etapa se identifica el menor CTF medio. Los pares cuyo IC del 95% se superpone con el mejor permanecen en evaluación y pasan a la siguiente etapa; solamente se descartan aquellos cuyo intervalo queda completamente por encima del intervalo del mejor costo.

Las réplicas de una política consumen bloques no superpuestos de los números pseudoaleatorios y, al comenzar la siguiente política, las secuencias se reinician para aplicar los mismos escenarios (números aleatorios comunes) a todas las alternativas.

Para cada variable se estima un intervalo bilateral para la media mediante la distribución t de Student:

$$IC_{95\%}=\bar{x}\pm t_{0.975;\,r-1}\frac{s}{\sqrt{r}}$$

donde $r$ es la cantidad de réplicas acumuladas en la etapa analizada, $\bar{x}$ es la media muestral y $s$ es la desviación estándar muestral. La variable principal de decisión es el **Costo Total de Funcionamiento (CTF)**; también se informan intervalos para el nivel de servicio, las ventas perdidas, los pedidos y cada componente del costo.

Con las secuencias actualmente guardadas en el repositorio, la política con menor CTF medio observado es `(PEP = 10, TP = 25)`. En 50 réplicas se obtuvo un CTF medio de **$2.021.600**, con IC 95% **[$1.988.087,78; $2.055.112,22]**, y un nivel de servicio medio de **69,67%**, con IC 95% **[68,68%; 70,65%]**. Su intervalo todavía se superpone con el de `(PEP = 10, TP = 20)`, por lo que ambos permanecen como candidatos y el resultado es **provisional**. Para una selección definitiva deben generarse más de 50 corridas para esos dos pares.

---

## 📁 Estructura del Repositorio
*   `generador_numeros_pet.py`: Generador de números pseudoaleatorios con multiplicador constante y pruebas de bondad de ajuste. Ahora genera automáticamente los archivos CSV y Excel detallados.
*   `simulador_pet.py`: Ejecuta la experimentación completa, presenta los intervalos y descartes en la terminal y genera un único libro consolidado.
*   `experimento_intervalo_confianza.py`: Ejecuta hasta 50 réplicas para cada uno de los 10 pares seleccionados, calcula los IC del 95% y aplica descarte progresivo por superposición.
*   `salidas/intervalo_confianza/`: Contiene los CSV intermedios con el resumen, la evolución por etapa y las 500 réplicas.
*   `salidas/corridas/corrida_FECHA_HORA/Simulacion_Entrega_Pet_10_pares.xlsx`: Único Excel de cada ejecución, con 13 hojas y el detalle diario de los 10 pares.
*   `numeros_demanda.csv` / `numeros_lead_time.csv`: Archivos de números pseudoaleatorios generados.
*   `Generacion Numeros Pseudoaleatorios para Demanda salida.xlsx`: Archivo Excel detallado paso a paso con las semillas iniciales, productos, centros y números resultantes de la demanda diaria, además del resumen de pruebas y desglose de Chi-Cuadrado.
*   `Generacion Numeros Pseudoaleatorios  llegada del proveedor salida.xlsx`: Archivo Excel detallado para la generación del tiempo de entrega del proveedor, estructurado análogamente al de demanda.
*   `Demanda diaria.xlsx`: Detalle diario de demanda, stock y costos.
*   `Tiempo de entrega del proveedor.xlsx`: Detalle de pedidos y tiempos de entrega.
*   `Validación manual.csv`: Reporte diario en UTF-8 compatible con Excel en Windows.
*   `Números utilizados.csv`: Registro de los números pseudoaleatorios consumidos durante la corrida.
*   `Generacion Numeros Pseudoaleatorios ... .xlsx`: Libros de Excel que ilustran los cálculos y la validación manual inicial (ejemplos previos).
*   `TP- EL CLAN-borrador.docx`: Borrador escrito con la documentación y teoría del trabajo práctico.

---

## 🚀 Instrucciones de Uso

1.  **Generación y Evaluación de Números Aleatorios:**
    Ejecutar el script del generador para actualizar los números pseudoaleatorios y generar automáticamente las planillas Excel detalladas de salida:
    ```bash
    python generador_numeros_pet.py
    ```

2.  **Ejecutar el Simulador de Inventario:**
    Correr el script para ejecutar las 50 corridas de los 10 pares, mostrar el análisis estadístico en la terminal y generar el único Excel consolidado:
    ```bash
    python simulador_pet.py
    ```

3.  **Calcular solo los intervalos de confianza del 95% y los CSV intermedios (opcional):**
    ```bash
    python experimento_intervalo_confianza.py
    ```
