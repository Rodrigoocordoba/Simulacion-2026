# 🚚 Simulador de Inventario - Entrega Pet 🐶🐱
Este repositorio contiene el desarrollo del Trabajo Práctico de Simulación para la optimización del sistema de inventario de la sucursal Resistencia de **Entrega Pet**, enfocado en el producto estrella de temporada alta: **Vital Can Premium Perro Adulto 20 kg**.

El objetivo principal es encontrar la combinación óptima de **Punto de Emisión de Pedido (PR o ROP)** y **Tamaño de Pedido (TP)** que minimice el **Costo Total de Funcionamiento (CTF)** del sistema, garantizando al mismo tiempo un excelente nivel de servicio para los clientes.

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
    *   Evaluar múltiples políticas de control de inventario `(ROP, TP)`.
    *   Determinar la política óptima que logre el mejor balance entre costos de almacenamiento, emisión de pedidos y ventas perdidas (costos de oportunidad).
    *   Obtener intervalos de confianza robustos utilizando la desigualdad de Chebyshev para la toma de decisiones.

---

## 🏗️ Definición del Sistema y Variables

### Variables Exógenas (Parámetros y Costos)
*   **Costo de Almacenamiento ($CALM$):** $\$500$ por bolsa al día (aplicado sobre el stock remanente al final del día).
*   **Costo por Venta Perdida ($CVP$):** $\$40,000$ por bolsa no entregada por falta de stock.
*   **Costo por Emisión de Pedido ($CEP$):** $\$5,000$ por cada orden de compra enviada al proveedor.
*   **Demanda Diaria ($DD$):** Variable aleatoria con distribución de **Poisson** ($\lambda = 2.05$ bolsas/día).
*   **Lead Time ($LT$):** Variable aleatoria con distribución **Uniforme Discreta** $[7, 14]$ días.

### Variables de Control (Alternativas de Decisión)
*   **Punto de Emisión de Pedido ($PR$ o $ROP$):** Nivel de stock a partir del cual se dispara una orden de reposición.
*   **Tamaño del Pedido ($TP$):** Cantidad de bolsas que se solicitan en cada orden.

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
                │ ST = 40, FLL = 1, T = 0     │
                │ Costos Acumulados = 0       │
                └──────────────┬──────────────┘
                               │
                   ┌──────────>│ T = T + 1
                   │           │
                   │     ¿T == FLL? (Llega Pedido)
                   │         ├─── [ SÍ ] ───> ST = ST + TP
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
                   │     ¿ST <= ROP y no hay pedidos pendientes (FLL <= T)?
                   │         ├─── [ SÍ ] ───> Generar Lead Time (LT) (Uniforme [7, 14])
                   │         │                FLL = T + LT
                   │         │                CTEP += CEP
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

### Simulación de Políticas y Análisis Estadístico
Para cada política de inventario `(ROP, TP)`, se ejecutan **$50$ corridas independientes** de $180$ días.
Dado que la distribución del costo total final ($CTF$) no es necesariamente normal, se calcula el intervalo de confianza del 95% ($\alpha = 0.05$) aplicando la **Desigualdad de Chebyshev**:
$$\text{Intervalo} = \text{Media} \pm \frac{S}{\sqrt{N \cdot \alpha}}$$
donde $S$ es la desviación estándar muestral y $N$ es el número de corridas ($50$).

---

## 📁 Estructura del Repositorio
*   `generador_numeros_pet.py`: Generador de números pseudoaleatorios con multiplicador constante y pruebas de bondad de ajuste.
*   `simulador_pet.py`: Motor del simulador de inventario que evalúa las diferentes políticas y exporta los archivos de validación.
*   `numeros_demanda.csv` / `numeros_lead_time.csv`: Archivos de números pseudoaleatorios generados.
*   `validacion_manual_pet.csv`: Reporte diario detallado de la simulación de validación para la mejor política elegida.
*   `numeros_usados_pet.csv`: Registro de los números pseudoaleatorios consumidos durante la corrida de validación.
*   `Generacion Numeros Pseudoaleatorios ... .xlsx`: Libros de Excel que ilustran los cálculos y la validación manual inicial.
*   `TP- EL CLAN-borrador.docx`: Borrador escrito con la documentación y teoría del trabajo práctico.

---

## 🚀 Instrucciones de Uso

1.  **Generación y Evaluación de Números Aleatorios:**
    Ejecutar el script del generador para actualizar los números pseudoaleatorios y visualizar el resultado de las pruebas estadísticas en consola:
    ```bash
    python generador_numeros_pet.py
    ```

2.  **Ejecutar el Simulador de Inventario:**
    Correr el script del simulador para evaluar las políticas, encontrar la configuración óptima de menor costo y generar los archivos de auditoría:
    ```bash
    python simulador_pet.py
    ```
