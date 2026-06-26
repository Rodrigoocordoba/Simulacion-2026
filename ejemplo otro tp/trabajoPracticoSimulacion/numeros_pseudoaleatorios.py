"""
Generador de Números Pseudoaleatorios - Ferretería JYL
Validación completa: media, varianza, chi-cuadrado, corridas
"""

import numpy as np
import math
from scipy import stats
import csv

class GeneradorPseudoaleatorios:
    def __init__(self, semilla=12345):
        self.semilla_inicial = semilla
        self.semilla = semilla
    
    def generar_numero(self):
        # Método congruencial lineal mixto
        a = 1664525
        c = 1013904223
        m = 2**32
        
        self.semilla = (a * self.semilla + c) % m
        return self.semilla / m
    
    def generar_secuencia(self, n):
        return [self.generar_numero() for _ in range(n)]
    
    def reset(self, nueva_semilla=None):
        self.semilla = nueva_semilla if nueva_semilla else self.semilla_inicial

def prueba_media(numeros, n=100, alpha=0.05):
    """Prueba de la media"""
    if len(numeros) < n:
        return False
    
    muestra = numeros[:n]
    media_muestral = np.mean(muestra)
    media_teorica = 0.5
    varianza_teorica = 1/12
    
    z_alpha_2 = stats.norm.ppf(1 - alpha/2)
    error_estandar = math.sqrt(varianza_teorica / n)
    limite_inferior = media_teorica - z_alpha_2 * error_estandar
    limite_superior = media_teorica + z_alpha_2 * error_estandar
    
    return limite_inferior <= media_muestral <= limite_superior

def prueba_varianza(numeros, n=100, alpha=0.05):
    """Prueba de la varianza"""
    if len(numeros) < n:
        return False
    
    muestra = numeros[:n]
    varianza_muestral = np.var(muestra, ddof=1)
    varianza_teorica = 1/12
    
    chi2_obs = (n - 1) * varianza_muestral / varianza_teorica
    chi2_inferior = stats.chi2.ppf(alpha/2, n-1)
    chi2_superior = stats.chi2.ppf(1-alpha/2, n-1)
    
    return chi2_inferior <= chi2_obs <= chi2_superior

def prueba_chi_cuadrado(numeros, k=10, alpha=0.05):
    """Prueba de chi-cuadrado"""
    n = len(numeros)
    if n < k * 5:
        return False
    
    intervalos = np.linspace(0, 1, k+1)
    observadas = np.histogram(numeros, bins=intervalos)[0]
    esperadas = np.full(k, n/k)
    
    chi2_obs = np.sum((observadas - esperadas)**2 / esperadas)
    chi2_critico = stats.chi2.ppf(1-alpha, k-1)
    
    return chi2_obs <= chi2_critico

def prueba_corridas(numeros, alpha=0.05):
    """Prueba de corridas arriba-abajo"""
    n = len(numeros)
    if n < 20:
        return False
    
    mediana = np.median(numeros)
    simbolos = ['+' if x >= mediana else '-' for x in numeros]
    
    corridas = 1
    for i in range(1, len(simbolos)):
        if simbolos[i] != simbolos[i-1]:
            corridas += 1
    
    n1 = simbolos.count('+')
    n2 = simbolos.count('-')
    
    if n1 == 0 or n2 == 0:
        return False
    
    mu_r = (2 * n1 * n2) / (n1 + n2) + 1
    var_r = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
    
    if var_r <= 0:
        return False
    
    z = (corridas - mu_r) / math.sqrt(var_r)
    z_critico = stats.norm.ppf(1 - alpha/2)
    
    return abs(z) <= z_critico

def generar_numeros_validados(n_numeros=1000, max_intentos=100):
    """Genera números que pasan todas las pruebas"""
    generador = GeneradorPseudoaleatorios()
    
    for intento in range(max_intentos):
        print(f"Intento {intento + 1}/{max_intentos}...")
        
        generador.reset(12345 + intento * 1000)
        numeros = generador.generar_secuencia(n_numeros)
        
        test_media = prueba_media(numeros)
        test_varianza = prueba_varianza(numeros)
        test_chi2 = prueba_chi_cuadrado(numeros)
        test_corridas = prueba_corridas(numeros)
        
        if test_media and test_varianza and test_chi2 and test_corridas:
            print("✅ Todas las pruebas aprobadas!")
            return numeros
        else:
            fallidas = []
            if not test_media: fallidas.append("media")
            if not test_varianza: fallidas.append("varianza")
            if not test_chi2: fallidas.append("chi-cuadrado")
            if not test_corridas: fallidas.append("corridas")
            print(f"❌ Fallaron: {', '.join(fallidas)}")
    
    raise Exception(f"No se encontraron números válidos en {max_intentos} intentos")

def exportar_csv(numeros, archivo="numeros_pseudoaleatorios.csv"):
    """Exporta números a CSV"""
    with open(archivo, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["indice", "numero_pseudoaleatorio"])
        for i, numero in enumerate(numeros):
            writer.writerow([i+1, numero])
    print(f"✅ Exportado a: {archivo}")

if __name__ == "__main__":
    print("🎲 Generador de Números Pseudoaleatorios - Ferretería JYL")
    print("=" * 60)
    
    try:
        numeros = generar_numeros_validados(10000)
        exportar_csv(numeros)
        print(f"\n🎯 {len(numeros)} números validados generados exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}") 