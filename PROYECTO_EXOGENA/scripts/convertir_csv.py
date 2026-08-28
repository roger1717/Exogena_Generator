import os
import pandas as pd
from pathlib import Path
import chardet

ruta_base = r"C:\INSPECCION\PROYECTS\PROYECTO_CONTADURIA\PROYECTO_EXOGENA\Docs\Datos"
carpeta_excel = os.path.join(ruta_base, "arc_xls")

print(f"Ruta base: {ruta_base}")
print(f"Carpeta destino: {carpeta_excel}")

if not os.path.exists(ruta_base):
    print("ERROR: La ruta base no existe.")
    exit()

os.makedirs(carpeta_excel, exist_ok=True)

csvs = [f for f in os.listdir(ruta_base) if f.lower().endswith(".csv")]
print(f"\nArchivos CSV encontrados: {len(csvs)}")
for f in csvs:
    print(f" - {f}")

if not csvs:
    print("No se encontraron archivos CSV.")
    exit()

def detectar_encoding(archivo):
    with open(archivo, 'rb') as f:
        raw = f.read(10000)
        result = chardet.detect(raw)
        return result['encoding'] or 'utf-8'

def leer_csv_manual(ruta_csv):
    encoding = detectar_encoding(ruta_csv)
    print(f"   Encoding detectado: {encoding}")
    
    try:
        with open(ruta_csv, 'r', encoding=encoding, errors='replace') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"   ✗ Error al leer archivo: {e}")
        return None
    
    if not lines:
        print("   ✗ El archivo está vacío.")
        return None
    
    # Extraer encabezado delimitado por ';'
    header = [col.strip('" ').strip() for col in lines[0].split(';')]
    num_cols = len(header)
    
    # Procesar filas ajustándolas al número exacto de columnas del encabezado
    datos = []
    for line in lines[1:]:
        campos = [campo.strip('" ').strip() for campo in line.split(';')]
        
        # Si la línea tiene más campos de los esperados (por ; sobrantes al final), recortar
        if len(campos) > num_cols:
            campos = campos[:num_cols]
        # Si le faltan campos, rellenar con cadenas vacías
        elif len(campos) < num_cols:
            campos.extend([''] * (num_cols - len(campos)))
            
        datos.append(campos)
    
    # Crear el DataFrame estructurado por columnas
    df = pd.DataFrame(datos, columns=header)
    
    # Convertir datos numéricos automáticamente
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
    print(f"   ✓ Lectura exitosa: {df.shape[0]} filas, {df.shape[1]} columnas")
    return df

for archivo in csvs:
    ruta_csv = os.path.join(ruta_base, archivo)
    nombre_sin_ext = Path(archivo).stem
    ruta_excel = os.path.join(carpeta_excel, f"{nombre_sin_ext}.xlsx")
    
    print(f"\nProcesando: {archivo}")
    
    df = leer_csv_manual(ruta_csv)
    
    if df is None:
        print(f"   ✗ No se pudo leer el archivo. Saltando.")
        continue
    
    try:
        df.to_excel(ruta_excel, index=False, engine='openpyxl')
        print(f"   ✓ Excel guardado correctamente en columnas: {ruta_excel}")
    except Exception as e:
        print(f"   ✗ Error al guardar Excel: {e}")

print("\n¡Conversión completada!")