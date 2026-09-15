# Parcial 1 – Inteligencia Artificial – Grupo 07
Análisis de recolección de residuos sólidos en Cartago, Valle del Cauca

## 1. Configuración del entorno

Requisitos: Docker Desktop (con WSL2 si estás en Windows) o Docker Engine en Linux/Mac.

Pasos para reproducir el entorno:

```bash
# 1. Clonar el repositorio
git clone https://github.com/manuela-aguirre/parcial1-ia-grupo07.git
cd parcial1-ia-grupo07

# 2. Construir la imagen y levantar el contenedor
docker compose up --build
```

Esto instala Python 3.12, NumPy y Matplotlib dentro del contenedor (ver `Dockerfile`
y `requirements.txt`) y ejecuta automáticamente `analisis.py`.

Alternativa sin Docker (entorno local):
```bash
pip install -r requirements.txt
python analisis.py
```

## 2. Carga de datos

`analisis.py` carga `grupo_07.csv` con la función `cargar_datos()` y muestra las
primeras 5 filas junto con el número total de registros (**13 registros**).

## 3. Calidad de datos

Se detectaron 3 problemas de calidad, todos documentados y reportados en consola
por `detectar_problemas_calidad()`:

**[1] Dato faltante** — La fila `Papel, , Miércoles, Sur` tiene la celda de
`cantidad_kg` vacía.
- *Detección*: recorrido de la columna buscando celdas vacías.
- *Decisión*: excluir ese registro del cálculo estadístico en vez de inventar un
  valor. Se documenta y se conserva visible en el CSV original para trazabilidad.
- *Por qué*: imputar sin contexto (por ejemplo con el promedio de Papel) introduce
  un sesgo silencioso; es más honesto reportar la ausencia.

**[2] Valor atípico / posible error de unidad** — El registro
`Orgánico, 0.45, Lunes, Centro` rompe el orden de magnitud frente a los otros dos
registros de la misma combinación tipo/día/zona (450 y 480 kg).
- *Detección*: comparación directa entre los 3 registros de "Orgánico/Lunes/Centro".
- *Decisión*: no se adivina el valor "correcto" (podría ser 450 con error de
  captura, o kg registrados como toneladas). Se excluye del análisis principal y
  se muestra el efecto de incluirlo vs. excluirlo sobre la media.
- **Pregunta clave del enunciado**: sí, este valor es claramente sospechoso. Si no
  se corrige, arrastra la media general de 280.00 kg a 256.70 kg (una caída del
  8.3%) y reduce artificialmente el mínimo del dataset a 0.45 kg, lo que podría
  hacer pensar que existen eventos de recolección casi nulos cuando en realidad
  es un error de captura.

**[3] Registros "cuasi-duplicados" sin diferenciador temporal** — Las combinaciones
(Orgánico, Lunes, Centro), (Plástico, Martes, Norte) y (Papel, Miércoles, Sur) se
repiten 3 veces cada una; (Vidrio, Jueves, Oriente) y (Metal, Viernes, Occidente)
se repiten 2 veces.
- *Detección*: se agruparon las filas por (tipo_residuo, día, zona) y se contaron
  las repeticiones.
- *Decisión*: no se eliminan (probablemente corresponden a semanas distintas),
  pero se documenta como limitación de diseño: falta una columna de fecha/semana
  real que permita diferenciarlas con certeza.

## 4. Análisis estadístico (NumPy)

| Métrica | Datos crudos (n=12) | Datos depurados (n=11) |
|---|---|---|
| Media | 256.70 kg | 280.00 kg |
| Mediana | 290.00 kg | 300.00 kg |
| Desviación estándar | 144.74 kg | 126.02 kg |
| Mínimo | 0.45 kg | 120.00 kg |
| Máximo | 480.00 kg | 480.00 kg |

**¿El promedio es representativo?** En los datos crudos: la media
(256.70) está un 11.4% por debajo de la mediana (290.00), esto es una señal de que un valor
atípico está desplazando el promedio. Al limpiar el dataset media (280.00) y
mediana (300.00) se acercan (diferencia de solo 6.7%) lo que la vuelve una
medida bastante más confiable. Además la desviación estándar depurada
(126.02 kg) sigue siendo alta en relación con la media (45%), lo que indica que
hay bastante dispersión entre tipos de residuo (el orgánico pesa mucho más que
el metal) no solo por el valor atípico.

## 5. Visualización

- `distribucion_cantidad_kg.png`: histograma de `cantidad_kg` (datos depurados).
  Muestra que la mayoría de los registros se concentran entre 120–350 kg con un
  grupo más pequeño cerca de 450–480 kg (los dos registros de Orgánico), lo que
  confirma la dispersión reflejada en la desviación estándar.
- `cantidad_por_tipo_residuo.png`: promedio de `cantidad_kg` por `tipo_residuo`.
  Muestra un orden claro: Orgánico (465.00 kg) > Plástico (336.67 kg) >
  Papel (290.00 kg) > Vidrio (155.00 kg) > Metal (125.00 kg).

## 6. Interpretación profunda

En este dataset, `tipo_residuo`, `día_recoleccion` y `zona` están perfectamente
correlacionados (cada tipo siempre aparece con el mismo día y la misma zona). Esto
es una correlación **por diseño del dataset**, no evidencia de causalidad: no se
puede concluir que la Zona Centro *solo* produce residuo orgánico, solo que así
fue registrado en esta muestra. El orgánico es, por buen margen, el residuo más
pesado por evento de recolección — consistente con patrones típicos de residuos
urbanos en la región, donde el componente orgánico domina el peso total.

## 7. Recomendación

1. La zona Centro (Orgánico) acumula 930 kg en los dos registros válidos, y
   Orgánico tiene el promedio más alto de todo el dataset (465.00 kg) — se
   recomienda priorizar un programa de compostaje comunitario ahí.
2. La zona Norte (Plástico) acumula el mayor total del dataset (1,010 kg en 3
   registros) — se recomienda reforzar rutas de reciclaje de plástico.
3. Vidrio (310 kg totales) y Metal (250 kg totales) son las categorías de menor
   volumen — sus rutas de recolección podrían consolidarse a frecuencia menor,
   liberando recursos para las zonas de mayor generación (Centro y Norte).

## 8. Limitaciones

- Muestra muy pequeña (13 registros, uno perdido y uno erróneo) para generalizar
  conclusiones a nivel de ciudad.
- No existe una columna de fecha/semana real, solo el día de la semana genérico,
  por lo que no se puede analizar tendencia temporal real.
- Cada zona aparece asociada a un único tipo de residuo en el dataset, así que no
  se puede comparar "qué zona genera más basura en total" (solo por tipo).
- No hay datos de población por zona para normalizar a kg per cápita.
