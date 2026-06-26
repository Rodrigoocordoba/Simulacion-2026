import scipy.stats as stats
import math
import statistics
import csv
import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

class SimuladorInventario:
    def __init__(self, archivo_demanda, archivo_lead_time):
        self.numeros_demanda = self.cargar_csv(archivo_demanda)
        self.numeros_lead_time = self.cargar_csv(archivo_lead_time)
        self.idx_demanda = 0
        self.idx_lead_time = 0
        
        # Variables exógenas de costos
        self.CALM = 500      # Costo por guardar una bolsa
        self.CVP = 40000     # Costo por venta perdida
        self.CEP = 5000      # Costo por emitir un pedido

    def cargar_csv(self, archivo):
        numeros = []
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    numeros.append(float(row['numero_pseudoaleatorio']))
        except Exception as e:
            print(f"Error al cargar {archivo}: {e}")
        return numeros

    def obtener_ri_demanda(self):
        ri = self.numeros_demanda[self.idx_demanda]
        self.idx_demanda = (self.idx_demanda + 1) % len(self.numeros_demanda)
        return ri

    def obtener_ri_lead_time(self):
        ri = self.numeros_lead_time[self.idx_lead_time]
        self.idx_lead_time = (self.idx_lead_time + 1) % len(self.numeros_lead_time)
        return ri

    def generar_demanda(self):
        ri = self.obtener_ri_demanda()
        # Transformada Inversa - Poisson lambda = 2.05
        demanda = stats.poisson.ppf(ri, 2.05)
        return int(demanda), ri

    def generar_lead_time(self):
        ri = self.obtener_ri_lead_time()
        # Transformada Inversa Uniforme Discreta [7, 14]
        return math.floor(7 + (8 * ri)), ri

    def simular_politica(self, ROP, TP, TF=180, validacion_manual=False):
        # CONDICIONES INICIALES SEGÚN DIAGRAMA
        T = 0
        FLL = 1
        ST = 40
        CTALM = 0
        CVTAP = 0
        CTEP = 0
        
        # Métricas para resumen
        demanda_total = 0
        ventas_perdidas_total = 0
        pedidos_realizados = 0
        
        datos_validacion = []
        numeros_usados_dem = []
        numeros_usados_lt = []
        
        # Bucle de incremento de tiempo constante
        for _ in range(TF):
            T += 1
            llegada_pedido = False
            
            # 1. ¿T = FLL? (Llegada de pedido)
            if T == FLL:
                ST += TP
                llegada_pedido = True
                
            # Generar Demanda
            DD, ri_dem = self.generar_demanda()
            numeros_usados_dem.append(ri_dem)
            demanda_total += DD
            
            st_anterior = ST
            vp_dia = 0
            # 2. ¿ST >= DD?
            if ST >= DD:
                ST -= DD
                CTALM += (ST * self.CALM)
            else:
                vp_dia = DD - ST
                CVTAP += (vp_dia * self.CVP)
                ST = 0
                
            ventas_perdidas_total += vp_dia
                
            # 3. Revisión de inventario
            emite_pedido = False
            lt_dia = 0
            if ST <= ROP and FLL <= T:
                lt_dia, ri_lt = self.generar_lead_time()
                numeros_usados_lt.append(ri_lt)
                FLL = T + lt_dia
                CTEP += self.CEP
                emite_pedido = True
                pedidos_realizados += 1

            if validacion_manual:
                datos_validacion.append({
                    "Dia": T,
                    "Stock_Inicial": st_anterior,
                    "Llega_Pedido": "SI" if llegada_pedido else "NO",
                    "Demanda": DD,
                    "Stock_Final": ST,
                    "Ventas_Perdidas": vp_dia,
                    "Emite_Pedido": "SI" if emite_pedido else "NO",
                    "Lead_Time": lt_dia if emite_pedido else "-",
                    "CTALM_Acumulado": CTALM,
                    "CVTAP_Acumulado": CVTAP,
                    "CTEP_Acumulado": CTEP,
                    "CTF_Acumulado": CTALM + CVTAP + CTEP
                })

        # Resultados de la corrida
        CTF = CTALM + CVTAP + CTEP
        
        if validacion_manual:
            return {
                "CTF": CTF,
                "Demanda_Total": demanda_total,
                "Ventas_Perdidas": ventas_perdidas_total,
                "Pedidos_Realizados": pedidos_realizados,
                "CTALM": CTALM,
                "CVTAP": CVTAP,
                "CTEP": CTEP,
                "Datos_Validacion": datos_validacion,
                "Numeros_Usados_Dem": numeros_usados_dem,
                "Numeros_Usados_LT": numeros_usados_lt
            }
            
        return CTF

    def ejecutar_experimento(self, ROP, TP, cant_corridas=50):
        resultados_ctf = []
        for _ in range(cant_corridas):
            ctf = self.simular_politica(ROP, TP)
            resultados_ctf.append(ctf)
            
        promedio_ctf = statistics.mean(resultados_ctf)
        desvio_ctf = statistics.stdev(resultados_ctf)
        
        # Intervalo de confianza para variables de otra distribución (Ecuación de Chebyshev / No normal)
        r = cant_corridas
        alfa = 0.05
        margen_error = desvio_ctf / math.sqrt(r * alfa)
        
        lim_inf = promedio_ctf - margen_error
        lim_sup = promedio_ctf + margen_error
        
        return promedio_ctf, lim_inf, lim_sup

def dar_formato_excel(filepath):
    try:
        wb = openpyxl.load_workbook(filepath)
        sheet = wb.active
        
        # Estilos visuales premium (Azul oscuro elegante)
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Segoe UI", size=10)
        align_center = Alignment(horizontal="center", vertical="center")
        thin_side = Side(border_style="thin", color="D3D3D3")
        border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        
        # Dar formato a la cabecera
        for col in range(1, sheet.max_column + 1):
            cell = sheet.cell(row=1, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = align_center
            cell.border = border_all
            
        # Dar formato a los datos de la tabla
        for row in range(2, sheet.max_row + 1):
            for col in range(1, sheet.max_column + 1):
                cell = sheet.cell(row=row, column=col)
                cell.font = data_font
                cell.alignment = align_center
                cell.border = border_all
                
                # Detectar columnas con dinero acumulado y aplicar formato moneda en pesos sin centavos
                header_name = sheet.cell(row=1, column=col).value
                if header_name and "Acumulado" in header_name:
                    cell.number_format = "$#,##0"
                elif header_name and header_name in ["Dia", "Stock_Inicial", "Demanda", "Stock_Final", "Ventas_Perdidas", "Lead_Time"]:
                    cell.number_format = "#,##0"
                    
        # Autoajuste de ancho de columnas
        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
            
        wb.save(filepath)
    except Exception as e:
        print(f"Error al dar formato al Excel {filepath}: {e}")

def exportar_resumen_validacion(resumen, archivo_csv="validacion_manual_pet.csv", archivo_num="numeros_usados_pet.csv"):
    # Exportar datos diarios a CSV
    if resumen["Datos_Validacion"]:
        keys = resumen["Datos_Validacion"][0].keys()
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(resumen["Datos_Validacion"])
        print(f"Exportado a CSV: {archivo_csv}")
            
        # Exportar a Excel en dos archivos separados
        try:
            df = pd.DataFrame(resumen["Datos_Validacion"])
            
            # 1. Excel de Demanda Diaria
            cols_demanda = ["Dia", "Stock_Inicial", "Llega_Pedido", "Demanda", "Stock_Final", "Ventas_Perdidas", "CTALM_Acumulado", "CVTAP_Acumulado", "CTF_Acumulado"]
            df_demanda = df[cols_demanda]
            excel_demanda = "Demanda diaria salida.xlsx"
            df_demanda.to_excel(excel_demanda, index=False)
            dar_formato_excel(excel_demanda)
            print(f"Exportado a Excel de Demanda: {excel_demanda}")
            
            # 2. Excel de Tiempo de Espera del Proveedor (Lead Time)
            cols_proveedor = ["Dia", "Stock_Inicial", "Stock_Final", "Emite_Pedido", "Lead_Time", "Llega_Pedido", "CTEP_Acumulado", "CTF_Acumulado"]
            df_proveedor = df[cols_proveedor]
            excel_proveedor = "Tiempo de espera del proveedor salida.xlsx"
            df_proveedor.to_excel(excel_proveedor, index=False)
            dar_formato_excel(excel_proveedor)
            print(f"Exportado a Excel de Proveedor: {excel_proveedor}")
            
        except Exception as e:
            print(f"Error al generar los Excels de simulación: {e}")
            
    # Exportar números usados
    with open(archivo_num, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Tipo", "Numero_Pseudoaleatorio"])
        for n in resumen["Numeros_Usados_Dem"]:
            writer.writerow(["Demanda", n])
        for n in resumen["Numeros_Usados_LT"]:
            writer.writerow(["Lead_Time", n])

if __name__ == "__main__":
    print("Simulador de Inventario - Entrega Pet")
    print("=" * 75)
    
    simulador = SimuladorInventario("numeros_demanda.csv", "numeros_lead_time.csv")
    
    politicas = [(10, 30), (15, 30), (20, 40), (25, 50), (30, 50), (20, 60), (15, 50)]
    
    mejor_ctf = float('inf')
    mejor_politica = None
    
    print(f"{'ROP':<5} | {'TP':<5} | {'CTF Promedio ($)':<18} | {'IC 95% Inferior':<18} | {'IC 95% Superior':<18}")
    print("-" * 75)
    
    for rop, tp in politicas:
        ctf_prom, lim_inf, lim_sup = simulador.ejecutar_experimento(rop, tp, cant_corridas=50)
        print(f"{rop:<5} | {tp:<5} | ${ctf_prom:<17,.2f} | ${lim_inf:<17,.2f} | ${lim_sup:<17,.2f}")
        
        if ctf_prom < mejor_ctf:
            mejor_ctf = ctf_prom
            mejor_politica = (rop, tp)
            
    print("=" * 75)
    print(f"LA MEJOR POLÍTICA ES: ROP = {mejor_politica[0]}, Tamaño Pedido = {mejor_politica[1]}")
    print(f"   Costo Promedio (CTF): ${mejor_ctf:,.2f}")
    
    print("\n" + "=" * 75)
    print("GENERANDO RESUMEN DE VALIDACIÓN PARA LA MEJOR POLÍTICA (1 CORRIDA DE 180 DÍAS)")
    print("=" * 75)
    
    resumen = simulador.simular_politica(mejor_politica[0], mejor_politica[1], TF=180, validacion_manual=True)
    exportar_resumen_validacion(resumen)
    
    total_numeros_usados = len(resumen['Numeros_Usados_Dem']) + len(resumen['Numeros_Usados_LT'])
    
    nivel_servicio = 0
    if resumen['Demanda_Total'] > 0:
        ventas_concretadas = resumen['Demanda_Total'] - resumen['Ventas_Perdidas']
        nivel_servicio = (ventas_concretadas / resumen['Demanda_Total']) * 100
    
    print("RESUMEN DE LA SIMULACIÓN:")
    print(f"- Política Evaluada: ROP = {mejor_politica[0]}, TP = {mejor_politica[1]}")
    print(f"- Días Simulados: 180")
    print(f"- Demanda Total: {resumen['Demanda_Total']} bolsas")
    print(f"- Ventas Perdidas: {resumen['Ventas_Perdidas']} bolsas")
    print(f"- Nivel de Servicio: {nivel_servicio:.2f}%")
    print(f"- Pedidos Realizados al Proveedor: {resumen['Pedidos_Realizados']}")
    print(f"- Números pseudoaleatorios usados (Demanda): {len(resumen['Numeros_Usados_Dem'])}")
    print(f"- Números pseudoaleatorios usados (Lead Time): {len(resumen['Numeros_Usados_LT'])}")
    print(f"- Costo de Almacenamiento: ${resumen['CTALM']:,.2f}")
    print(f"- Costo de Venta Perdida: ${resumen['CVTAP']:,.2f}")
    print(f"- Costo de Emisión de Pedidos: ${resumen['CTEP']:,.2f}")
    print(f"- COSTO TOTAL DE FUNCIONAMIENTO (CTF): ${resumen['CTF']:,.2f}")
    print("\nDatos de validación exportados a: validacion_manual_pet.csv")
    print(f"   Total de registros (días): 180")
    print("Números pseudoaleatorios usados exportados a: numeros_usados_pet.csv")
    print(f"   Total de números usados: {total_numeros_usados}")
    print("=" * 75)
