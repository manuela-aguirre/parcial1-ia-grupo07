"""
analisis.py
Grupo 07 - Primer Parcial de Inteligencia Artificial
Cartago, Valle del Cauca - Analisis de recoleccion de residuos solidos

Flujo del script:
  1. Cargar el CSV asignado (grupo_07.csv).
  2. Mostrar las primeras 5 filas y el numero total de registros.
  3. Detectar y documentar problemas de calidad de datos.
  4. Calcular estadisticas descriptivas con NumPy (version cruda vs version
     depurada) sobre la variable numerica principal: cantidad_kg.
  5. Generar 2 graficos con Matplotlib y guardarlos como PNG.
"""

import csv
import numpy as np
import matplotlib.pyplot as plt

RUTA_CSV = "grupo_07.csv"
COLUMNA_PRINCIPAL = "cantidad_kg"


# ---------------------------------------------------------------------
# 1. CARGA DE DATOS
# ---------------------------------------------------------------------
def cargar_datos(ruta_archivo):
    """Lee el CSV y retorna una lista de diccionarios (una fila = un dict)."""
    with open(ruta_archivo, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        datos = [dict(fila) for fila in lector]
    return datos


def mostrar_primeras_filas(datos, n=5):
    print("=" * 70)
    print(f"PRIMERAS {n} FILAS DEL ARCHIVO '{RUTA_CSV}'")
    print("=" * 70)
    for i, fila in enumerate(datos[:n], start=1):
        print(f"{i}. {fila}")
    print(f"\nNumero total de registros: {len(datos)}")


# ---------------------------------------------------------------------
# 2. CALIDAD DE DATOS
# ---------------------------------------------------------------------
def detectar_problemas_calidad(datos):
    """
    Detecta y reporta 3 problemas de calidad de datos encontrados en el
    dataset, siguiendo las categorias sugeridas en el enunciado (valores
    atipicos, datos faltantes, duplicados, inconsistencias de formato,
    unidades inconsistentes, filas de resumen).
    """
    print("\n" + "=" * 70)
    print("PROBLEMAS DE CALIDAD DE DATOS DETECTADOS")
    print("=" * 70)

    # --- Problema 1: datos faltantes ---------------------------------
    faltantes = [f for f in datos if f[COLUMNA_PRINCIPAL].strip() == ""]
    print(f"\n[1] DATOS FALTANTES: {len(faltantes)} registro(s) sin valor en "
          f"'{COLUMNA_PRINCIPAL}'.")
    for f in faltantes:
        print(f"    -> {f}")
    print("    Deteccion: se recorrio la columna buscando celdas vacias.")
    print("    Decision: excluir el registro del calculo estadistico (no se "
          "inventa un valor). Se documenta y se deja visible en el CSV original.")

    # --- Problema 2: valor atipico / inconsistencia de unidad --------
    valores_organico = [(i, f) for i, f in enumerate(datos)
                         if f["tipo_residuo"] == "Orgánico" and f[COLUMNA_PRINCIPAL].strip() != ""]
    print(f"\n[2] VALOR ATIPICO / POSIBLE INCONSISTENCIA DE UNIDAD:")
    for i, f in valores_organico:
        print(f"    -> fila {i}: Organico = {f[COLUMNA_PRINCIPAL]} kg")
    print("    Deteccion: comparando los 3 registros de 'Organico / Lunes / Centro' "
          "(450, 480 y 0.45), el ultimo rompe el orden de magnitud (~1000 veces "
          "menor). Es muy probable que sea un error de captura (falto un cero, "
          "o se registro en toneladas en vez de kg).")
    print("    Decision: no se corrige adivinando el valor real; se marca como "
          "atipico y se excluye del calculo estadistico principal, mostrando "
          "ademas el efecto de incluirlo/excluirlo sobre el promedio.")

    # --- Problema 3: duplicados / falta de columna temporal ----------
    combinaciones = {}
    for f in datos:
        clave = (f["tipo_residuo"], f["dia_recoleccion"], f["zona"])
        combinaciones[clave] = combinaciones.get(clave, 0) + 1
    repetidas = {k: v for k, v in combinaciones.items() if v > 1}
    print(f"\n[3] REGISTROS 'CUASI-DUPLICADOS' (misma combinacion tipo/dia/zona, "
          f"sin diferenciador temporal): {len(repetidas)} combinaciones repetidas.")
    for k, v in repetidas.items():
        print(f"    -> {k} aparece {v} veces")
    print("    Deteccion: se agruparon las filas por (tipo_residuo, dia_recoleccion, "
          "zona) y se conto cuantas veces se repite cada combinacion.")
    print("    Decision: no se eliminan (probablemente son mediciones de semanas "
          "distintas), pero se documenta como limitacion: el dataset no tiene "
          "columna de fecha/semana, por lo que no se puede saber a que periodo "
          "exacto corresponde cada lectura.")

    return faltantes, valores_organico


# ---------------------------------------------------------------------
# 3. ESTADISTICA CON NUMPY
# ---------------------------------------------------------------------
def calcular_estadisticas(datos):
    print("\n" + "=" * 70)
    print(f"ANALISIS ESTADISTICO DE '{COLUMNA_PRINCIPAL}'")
    print("=" * 70)

    # Version cruda: todos los valores numericos validos (excluye solo el
    # registro con celda vacia; SI incluye el valor atipico 0.45)
    crudos = np.array([
        float(f[COLUMNA_PRINCIPAL]) for f in datos
        if f[COLUMNA_PRINCIPAL].strip() != ""
    ])

    # Version depurada: ademas excluye el valor atipico (< 10 kg, fuera de
    # escala frente al resto de registros de recoleccion)
    depurados = crudos[crudos >= 10]

    def resumen(arr, etiqueta):
        print(f"\n-- {etiqueta} (n={len(arr)}) --")
        print(f"   Media               : {np.mean(arr):.2f} kg")
        print(f"   Mediana             : {np.median(arr):.2f} kg")
        print(f"   Desviacion estandar : {np.std(arr, ddof=1):.2f} kg")
        print(f"   Minimo              : {np.min(arr):.2f} kg")
        print(f"   Maximo              : {np.max(arr):.2f} kg")

    resumen(crudos, "Datos crudos (incluye valor atipico 0.45)")
    resumen(depurados, "Datos depurados (excluye valor atipico y faltante)")

    return crudos, depurados


# ---------------------------------------------------------------------
# 4. VISUALIZACION CON MATPLOTLIB
# ---------------------------------------------------------------------
def graficar_distribucion(depurados, ruta_salida="distribucion_cantidad_kg.png"):
    plt.figure(figsize=(7, 5))
    plt.hist(depurados, bins=6, color="#4C72B0", edgecolor="white")
    plt.title("Distribucion de cantidad_kg recolectada (datos depurados)")
    plt.xlabel("Cantidad (kg)")
    plt.ylabel("Frecuencia (numero de registros)")
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()
    print(f"\nGrafico guardado: {ruta_salida}")


def graficar_relacion_tipo_cantidad(datos, ruta_salida="cantidad_por_tipo_residuo.png"):
    # Promedio de cantidad_kg por tipo_residuo, excluyendo faltantes y el
    # valor atipico ya identificado.
    acumulado = {}
    conteo = {}
    for f in datos:
        valor_txt = f[COLUMNA_PRINCIPAL].strip()
        if valor_txt == "":
            continue
        valor = float(valor_txt)
        if valor < 10:
            continue
        tipo = f["tipo_residuo"]
        acumulado[tipo] = acumulado.get(tipo, 0) + valor
        conteo[tipo] = conteo.get(tipo, 0) + 1

    tipos = list(acumulado.keys())
    promedios = [acumulado[t] / conteo[t] for t in tipos]

    plt.figure(figsize=(7, 5))
    plt.bar(tipos, promedios, color="#55A868", edgecolor="white")
    plt.title("Cantidad promedio recolectada (kg) por tipo de residuo")
    plt.xlabel("Tipo de residuo")
    plt.ylabel("Promedio (kg)")
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150)
    plt.close()
    print(f"Grafico guardado: {ruta_salida}")

    return dict(zip(tipos, promedios))


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    datos = cargar_datos(RUTA_CSV)
    mostrar_primeras_filas(datos, n=5)
    detectar_problemas_calidad(datos)
    crudos, depurados = calcular_estadisticas(datos)
    graficar_distribucion(depurados)
    promedios_por_tipo = graficar_relacion_tipo_cantidad(datos)

    print("\n" + "=" * 70)
    print("PROMEDIO POR TIPO DE RESIDUO (kg, datos depurados)")
    print("=" * 70)
    for tipo, prom in sorted(promedios_por_tipo.items(), key=lambda x: -x[1]):
        print(f"   {tipo:10s}: {prom:.2f} kg")


if __name__ == "__main__":
    main()
