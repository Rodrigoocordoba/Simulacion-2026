import numpy as np
import math
from scipy import stats
import csv

class GeneradorMultiplicadorConstante:
    def __init__(self, semilla_inicial, multiplicador):
        self.semilla_inicial = semilla_inicial
        self.semilla = semilla_inicial
        self.multiplicador = multiplicador
    
    def generar_numero(self):
        # Y = X * a
        Y = self.semilla * self.multiplicador
        
        # Rellenar con ceros a la izquierda hasta 8 dígitos
        Y_str = str(Y).zfill(8)
        
        # Extraer los 4 dígitos centrales (índices 2, 3, 4, 5)
        self.semilla = int(Y_str[2:6])
        
        # Si la semilla llega a 0, se genera un problema porque quedará estancado en 0.
        # En la práctica, con 10,000 números puede haber degeneración.
        # Dejamos la implementación fiel al método matemático clásico.
        
        return self.semilla / 10000.0
    
    def generar_secuencia(self, n):
        numeros = []
        for _ in range(n):
            numeros.append(self.generar_numero())
        return numeros
    
    def reset(self, nueva_semilla=None):
        self.semilla = nueva_semilla if nueva_semilla else self.semilla_inicial

def prueba_media(numeros, alpha=0.05):
    """Prueba de la media"""
    n = len(numeros)
    media_muestral = np.mean(numeros)
    media_teorica = 0.5
    varianza_teorica = 1/12
    
    z_alpha_2 = stats.norm.ppf(1 - alpha/2)
    error_estandar = math.sqrt(varianza_teorica / n)
    limite_inferior = media_teorica - z_alpha_2 * error_estandar
    limite_superior = media_teorica + z_alpha_2 * error_estandar
    
    aprobada = limite_inferior <= media_muestral <= limite_superior
    return aprobada, media_muestral, limite_inferior, limite_superior

def prueba_varianza(numeros, alpha=0.05):
    """Prueba de la varianza"""
    n = len(numeros)
    varianza_muestral = np.var(numeros, ddof=1)
    varianza_teorica = 1/12
    
    chi2_obs = (n - 1) * varianza_muestral / varianza_teorica
    chi2_inferior = stats.chi2.ppf(alpha/2, n-1)
    chi2_superior = stats.chi2.ppf(1-alpha/2, n-1)
    
    aprobada = chi2_inferior <= chi2_obs <= chi2_superior
    return aprobada, varianza_muestral, chi2_obs, chi2_inferior, chi2_superior

def prueba_chi_cuadrado(numeros, k=10, alpha=0.05):
    """Prueba de chi-cuadrado"""
    n = len(numeros)
    
    intervalos = np.linspace(0, 1, k+1)
    observadas = np.histogram(numeros, bins=intervalos)[0]
    esperadas = np.full(k, n/k)
    
    chi2_obs = np.sum((observadas - esperadas)**2 / esperadas)
    chi2_critico = stats.chi2.ppf(1-alpha, k-1)
    
    aprobada = chi2_obs <= chi2_critico
    return aprobada, chi2_obs, chi2_critico

def prueba_corridas(numeros, alpha=0.05):
    """Prueba de corridas arriba-abajo"""
    n = len(numeros)
    mediana = 0.5 # A veces se usa 0.5, a veces la mediana muestral
    simbolos = ['+' if x >= mediana else '-' for x in numeros]
    
    corridas = 1
    for i in range(1, len(simbolos)):
        if simbolos[i] != simbolos[i-1]:
            corridas += 1
    
    n1 = simbolos.count('+')
    n2 = simbolos.count('-')
    
    if n1 == 0 or n2 == 0:
        return False, 0, 0
    
    mu_r = (2 * n1 * n2) / (n1 + n2) + 1
    var_r = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
    
    if var_r <= 0:
        return False, 0, 0
    
    z = (corridas - mu_r) / math.sqrt(var_r)
    z_critico = stats.norm.ppf(1 - alpha/2)
    
    aprobada = abs(z) <= z_critico
    return aprobada, z, z_critico

def generar_y_evaluar(semilla, multiplicador, n_numeros, nombre_archivo):
    print(f"\n--- Generando {n_numeros} números para {nombre_archivo} ---")
    print(f"Semilla: {semilla}, Multiplicador: {multiplicador}")
    
    generador = GeneradorMultiplicadorConstante(semilla, multiplicador)
    numeros = generador.generar_secuencia(n_numeros)
    
    print("\nResultados Pruebas Estadísticas:")
    
    # 1. Media
    aprobada, med, linf, lsup = prueba_media(numeros)
    print(f"[{'✅' if aprobada else '❌'}] Media: {med:.4f} (Intervalo: [{linf:.4f}, {lsup:.4f}])")
    
    # 2. Varianza
    aprobada, var, chi2_obs, chi2_inf, chi2_sup = prueba_varianza(numeros)
    print(f"[{'✅' if aprobada else '❌'}] Varianza: {var:.4f} (Chi2 Obs: {chi2_obs:.2f} en [{chi2_inf:.2f}, {chi2_sup:.2f}])")
    
    # 3. Chi Cuadrado
    aprobada, chi2_obs_c, chi2_critico = prueba_chi_cuadrado(numeros)
    print(f"[{'✅' if aprobada else '❌'}] Chi-Cuadrado: Obs = {chi2_obs_c:.2f}, Crítico = {chi2_critico:.2f}")
    
    # 4. Corridas
    aprobada, z, z_critico = prueba_corridas(numeros)
    print(f"[{'✅' if aprobada else '❌'}] Corridas: Z = {z:.4f}, Z_Crítico = {z_critico:.4f}")
    
    # Exportar
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["indice", "numero_pseudoaleatorio"])
        for i, numero in enumerate(numeros):
            writer.writerow([i+1, numero])
    print(f"✅ Exportado a: {nombre_archivo}")
    
    return numeros

if __name__ == "__main__":
    print("🎲 Generador de Números Pseudoaleatorios - Multiplicador Constante (Entrega Pet)")
    print("=" * 70)
    
    CANTIDAD = 10000
    
    # Demanda: Semilla = 2026, Multiplicador = 5324
    numeros_demanda = generar_y_evaluar(2026, 5324, CANTIDAD, "numeros_demanda.csv")
    
    # Lead Time: Semilla = 1754, Multiplicador = 4813
    numeros_lead_time = generar_y_evaluar(1754, 4813, CANTIDAD, "numeros_lead_time.csv")
    
    print("\nProceso finalizado.")
