#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de constants.py desde reglas_mapeo.json

Este script lee el archivo JSON con todas las reglas de mapeo y genera
el archivo app/core/constants.py con las constantes derivadas.

Uso:
    python scripts/generar_constants.py
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def convertir_valor_python(valor):
    """
    Convertir un valor JSON a valor Python válido para código
    
    Args:
        valor: Valor a convertir (puede ser dict, list, str, etc.)
    
    Returns:
        Valor convertido para Python
    """
    if isinstance(valor, dict):
        return {k: convertir_valor_python(v) for k, v in valor.items()}
    elif isinstance(valor, list):
        return [convertir_valor_python(v) for v in valor]
    elif isinstance(valor, bool):
        return valor
    elif valor is None:
        return None
    else:
        return valor


def leer_json() -> Dict[str, Any]:
    """Leer el archivo reglas_mapeo.json"""
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "data" / "reglas_mapeo.json"
    
    if not json_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generar_constants(data: Dict[str, Any]) -> str:
    """
    Generar el contenido de constants.py desde los datos del JSON
    """
    
    # Extraer datos
    version = data.get('version', '1.0.0')
    fecha = data.get('fecha_actualizacion', datetime.now().strftime('%Y-%m-%d'))
    uvt = data.get('uvt', {})
    formatos = data.get('formatos', {})
    reglas = data.get('reglas', [])
    
    # 🔵 NUEVO: Extraer conceptos de retención del JSON (si existe)
    conceptos_retencion_dian = data.get('conceptos_retencion_dian', {
        "01": "Arrendamientos",
        "02": "Servicios Generales",
        "03": "Honorarios",
        "04": "Servicios Profesionales",
        "05": "Comisiones",
        "06": "Transporte de carga",
        "07": "Servicios de restaurante",
        "08": "Compra de bienes",
        "09": "Intereses",
        "10": "Regalías",
        "99": "Concepto Contable Múltiple",
    })
    
    # Convertir reglas a string JSON con indentación
    reglas_json_str = json.dumps(reglas, indent=4, ensure_ascii=False)
    
    # Reemplazar true/false por True/False (para Python)
    reglas_json_str = reglas_json_str.replace('true', 'True')
    reglas_json_str = reglas_json_str.replace('false', 'False')
    reglas_json_str = reglas_json_str.replace('null', 'None')
    
    # Generar contenido
    content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONSTANTES DEL NEGOCIO
¡NO MODIFICAR MANUALMENTE!

Este archivo es GENERADO AUTOMÁTICAMENTE desde data/reglas_mapeo.json
Para actualizar, modificar el JSON y ejecutar:
    python scripts/generar_constants.py

Última actualización: {fecha}
Versión: {version}
"""

from decimal import Decimal
from typing import Dict, Optional, List


# ============================================================================
# UVT (Unidad de Valor Tributario)
# ============================================================================

UVT = {uvt}

def get_uvt(year: int = 2025) -> Decimal:
    \"\"\"
    Obtener UVT para un año específico
    
    Args:
        year: Año a consultar
    
    Returns:
        Decimal: Valor UVT para el año solicitado
    \"\"\"
    return Decimal(str(UVT.get(year, UVT.get(2025, 47065))))


# ============================================================================
# FORMATOS DIAN
# ============================================================================

FORMATOS_DIAN = {formatos}

# Mapeo de formato exógena → formato retención
FORMATO_EXOGENA_A_RETENCION = {formatos.get('exogena_a_retencion', {})}


# ============================================================================
# CONCEPTOS DE RETENCIÓN DIAN
# ============================================================================

CONCEPTOS_RETENCION_DIAN = {conceptos_retencion_dian}


# ============================================================================
# REGLAS DE MAPEO (TODAS)
# ============================================================================

# Lista completa de reglas
REGLAS_MAPEO = {reglas_json_str}

# ============================================================================
# REGLAS DE MAPEO POR PUC (para búsqueda rápida)
# ============================================================================

REGLAS_POR_PUC = {{
    r['puc_code']: r for r in REGLAS_MAPEO if r.get('activo', True)
}}

# ============================================================================
# REGLAS DE RETENCIÓN (solo las que aplican)
# ============================================================================

REGLAS_RETENCION = [
    r for r in REGLAS_MAPEO 
    if r.get('activo', True) and r.get('concepto_retencion') is not None
]

REGLAS_RETENCION_POR_PUC = {{
    r['puc_code']: r for r in REGLAS_RETENCION
}}

# ============================================================================
# MAPEO DE CONCEPTOS
# ============================================================================

# Mapeo de concepto exógena → concepto retención
CONCEPTO_EXOGENA_A_RETENCION = {{
    r['exogena_concept']: r['concepto_retencion']
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}}

# Mapeo de concepto contable → código DIAN
CONCEPTO_CONTABLE_A_DIAN = {{
    "Arrendamientos": "01",
    "Servicios Generales": "02",
    "Honorarios": "03",
    "Servicios Profesionales": "04",
    "Comisiones": "05",
    "Transporte de carga": "06",
    "Servicios de restaurante": "07",
    "Compra de bienes": "08",
    "Intereses": "09",
    "Regalías": "10",
}}

# ============================================================================
# CONSTANTES DERIVADAS
# ============================================================================

# Lista de códigos de concepto que aplican para retención
CONCEPTOS_CON_RETENCION = list({{
    r['concepto_retencion'] for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}})

# Topes mínimos por concepto (en COP)
TOPES_MINIMOS = {{
    r['concepto_retencion']: Decimal(str(r['tope_minimo']))
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None and r.get('tope_minimo') is not None
}}

# Tarifas por concepto
TARIFAS_RETENCION = {{
    r['concepto_retencion']: Decimal(str(r['tarifa_retencion']))
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None and r.get('tarifa_retencion') is not None
}}

# ¿Aplica IVA en la base de cálculo?
APLICA_IVA_EN_BASE = {{
    r['concepto_retencion']: r.get('aplica_iva', False)
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}}

# Tipos de retención por concepto
TIPOS_RETENCION_POR_CONCEPTO = {{
    r['concepto_retencion']: r.get('tipo_retencion', 'renta')
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}}

# ============================================================================
# CONSTANTES FIJAS
# ============================================================================

# Formato DIAN para retenciones
FORMATO_RETENCION = "1003"

# Tipos de retención disponibles
TIPOS_RETENCION = {{
    "renta": "Retención en la fuente por renta",
    "iva": "Retención en la fuente por IVA",
    "ica": "Retención en la fuente por ICA",
}}

# Estados de una retención
ESTADOS_RETENCION = {{
    "procesado": "Calculada pero no reportada",
    "reportado": "Incluida en reporte DIAN",
    "error": "Error en el procesamiento",
    "no_aplica": "No aplica retención (tope mínimo)",
}}

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def obtener_regla(puc_code: str) -> Optional[Dict]:
    \"\"\"
    Obtener regla de mapeo por código PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        Dict con la regla o None si no existe
    \"\"\"
    return REGLAS_POR_PUC.get(puc_code)


def obtener_regla_retencion(puc_code: str) -> Optional[Dict]:
    \"\"\"
    Obtener regla de retención por código PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        Dict con la regla de retención o None si no aplica
    \"\"\"
    return REGLAS_RETENCION_POR_PUC.get(puc_code)


def es_cuenta_retencion(puc_code: str) -> bool:
    \"\"\"
    Determinar si una cuenta aplica para retención
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        True si aplica retención, False en caso contrario
    \"\"\"
    regla = obtener_regla_retencion(puc_code)
    return regla is not None and regla.get('activo', True)


def get_tarifa_retencion(concepto_dian: str) -> Decimal:
    \"\"\"
    Obtener tarifa de retención por concepto DIAN
    
    Args:
        concepto_dian: Código de concepto DIAN (ej: '01')
    
    Returns:
        Decimal: Tarifa de retención
    \"\"\"
    return TARIFAS_RETENCION.get(concepto_dian, Decimal('0'))


def get_tope_minimo(concepto_dian: str) -> Decimal:
    \"\"\"
    Obtener tope mínimo por concepto DIAN
    
    Args:
        concepto_dian: Código de concepto DIAN (ej: '01')
    
    Returns:
        Decimal: Tope mínimo en COP
    \"\"\"
    return TOPES_MINIMOS.get(concepto_dian, Decimal('0'))


def get_concepto_dian_from_contable(concepto_contable: str) -> Optional[str]:
    \"\"\"
    Obtener código DIAN desde el concepto contable
    
    Args:
        concepto_contable: Nombre del concepto contable
    
    Returns:
        str: Código DIAN o None si no existe
    \"\"\"
    return CONCEPTO_CONTABLE_A_DIAN.get(concepto_contable)


def get_reglas_activas() -> List[Dict]:
    \"\"\"
    Obtener lista de reglas activas
    
    Returns:
        List[Dict]: Lista de reglas activas
    \"\"\"
    return [r for r in REGLAS_MAPEO if r.get('activo', True)]


def get_reglas_por_formato(formato: str) -> List[Dict]:
    \"\"\"
    Obtener reglas por formato DIAN
    
    Args:
        formato: Código de formato (ej: '1001')
    
    Returns:
        List[Dict]: Lista de reglas para el formato
    \"\"\"
    return [
        r for r in REGLAS_MAPEO 
        if r.get('exogena_format') == formato and r.get('activo', True)
    ]


# ============================================================================
# EJECUCIÓN DIRECTA (para pruebas)
# ============================================================================

if __name__ == "__main__":
    # Mostrar resumen al ejecutar el script directamente
    print("📊 Resumen de reglas cargadas:")
    print(f"   Total reglas: {{len(REGLAS_MAPEO)}}")
    print(f"   Reglas activas: {{len(get_reglas_activas())}}")
    print(f"   Reglas de retención: {{len(REGLAS_RETENCION)}}")
    print(f"   Conceptos con retención: {{len(CONCEPTOS_CON_RETENCION)}}")
    print(f"   UVT 2025: ${{UVT.get(2025):,}}")
'''
    
    return content


def guardar_constants(content: str) -> None:
    """Guardar el contenido en app/core/constants.py"""
    base_dir = Path(__file__).parent.parent
    output_path = base_dir / "app" / "core" / "constants.py"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ constants.py generado en: {output_path}")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔄 GENERANDO CONSTANTS.PY")
    print("="*60)
    
    try:
        # 1. Leer JSON
        print("\n📄 Leyendo data/reglas_mapeo.json...")
        data = leer_json()
        print(f"   ✅ {len(data.get('reglas', []))} reglas cargadas")
        
        # 2. Generar contenido
        print("\n📝 Generando constants.py...")
        content = generar_constants(data)
        
        # 3. Guardar archivo
        guardar_constants(content)
        
        # 4. Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        reglas = data.get('reglas', [])
        reglas_activas = [r for r in reglas if r.get('activo', True)]
        reglas_retencion = [
            r for r in reglas_activas 
            if r.get('concepto_retencion') is not None
        ]
        print(f"   Total reglas: {len(reglas)}")
        print(f"   Reglas activas: {len(reglas_activas)}")
        print(f"   Reglas de retención: {len(reglas_retencion)}")
        print("\n✅ Proceso completado exitosamente")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n   Crea el archivo data/reglas_mapeo.json con las reglas")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()