# 🚚 Simulador de Inventario - Entrega Pet 🐶🐱
Este repositorio contiene el desarrollo del Trabajo Práctico de Simulación para la optimización del sistema de inventario de la sucursal Resistencia de **Entrega Pet**, enfocado en el producto estrella de temporada alta: **Vital Can Premium Perro Adulto 20 kg**.

El objetivo principal es comparar múltiples combinaciones de **Punto de Emisión de Pedido (PEP)** y **Tamaño de Pedido (TP)** para encontrar la de menor **Costo Total de Funcionamiento (CTF)**. La primera alternativa es la indicada en la planilla de referencia: `(PEP = 5, TP = 20)`.

---

## 📋 Contenidos
1. [Objetivos de la Simulación](#-objetivos-de-la-simulación)
2. [Definición del Sistema y Variables](#-definición-del-sistema-y-variables)
3. [Generador de Números Pseudoaleatorios (Multiplicador Constante)](#-generador-de-números-pseudoaleatorios-multiplicador-constante)
4. [Lógica y Estructura del Simulador](#-lógica-y-estructura-del-simulador)
5. [Estructura del Repositorio](#-estructura-del-repositorio)
6. [Instrucciones de Uso](#-instrucciones-de-uso)

---

## 🎯 Objetivos de la Simulación
*   **Objetivo Principal:** Minimizar el Costo Total de Funcionamiento (CTF) del sistema de inventario para bolsas de 20 kg de Vital Can Premium Perro Adulto.
*   **Objetivos Específicos:**
    *   Modelar el comportamiento de la demanda diaria y los tiempos de entrega del proveedor mediante variables aleatorias.
    *   Evaluar distintas políticas de control de inventario, comenzando por `(PEP = 5, TP = 20)`.
    *   Encontrar el mejor balance entre costos de almacenamiento, emisión de pedidos y ventas perdidas (costos de oportunidad).
    *   Comparar el costo total obtenido en una corrida de 180 días para cada combinación PEP/TP.

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
*   **Grilla evaluada:** $PEP \in \{5,6,\ldots,10\}$ y todos los tamaños enteros $TP \in \{15,16,\ldots,25\}$, para un total de 66 alternativas. La grilla se puede ampliar desde `simulador_pet.py`.

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
Para cada una de las 66 combinaciones `(PEP, TP)` se ejecuta **una corrida de 180 días**. Todas comienzan desde las mismas condiciones y secuencias pseudoaleatorias para que la comparación dependa de la política evaluada. Cada corrida se exporta a su propio Excel dentro de `Corridas por combinación`.

---

## 📁 Estructura del Repositorio
*   `generador_numeros_pet.py`: Generador de números pseudoaleatorios con multiplicador constante y pruebas de bondad de ajuste. Ahora genera automáticamente los archivos CSV y Excel detallados.
*   `simulador_pet.py`: Motor que compara múltiples políticas y exporta la validación de la alternativa óptima.
*   `salidas/corridas/corrida_FECHA_HORA/`: Carpeta única creada en cada ejecución para conservar el historial sin sobrescribir resultados anteriores.
*   `Corridas por combinación/`: Contiene 66 Excel individuales, uno por cada par `(PEP, TP)`, con sus 180 días completos.
*   `Simulación de inventario.xlsx`: Incluye el ranking de políticas y la corrida completa de 180 días para la mejor alternativa, con las mismas 19 columnas y convenciones de la planilla de referencia.
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
    Correr el script del simulador para comparar las políticas, identificar la de menor costo y generar automáticamente el ranking y la corrida diaria de la mejor alternativa:
    ```bash
    python simulador_pet.py
    ```
