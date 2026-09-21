#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constantes del negocio contable.

Este archivo contiene ÚNICAMENTE constantes inmutables:
  - UVT por año
  - Conceptos DIAN de retención
  - Formatos DIAN
  - Mapas de conceptos contables → DIAN

Las reglas de mapeo viven en data/reglas/*.json y se cargan vía ReglasService.

NO agregar reglas aquí.
NO generar este archivo automáticamente.
"""

from decimal import Decimal
from typing import Dict, Optional


# ============================================================================
# UVT (Unidad de Valor Tributario)
# ============================================================================


UVT: Dict[int, int] = {
    2025: 47065,
    2024: 45458,
    2023: 42412,
    2022: 38004,
    2021: 36308,
}


def get_uvt(year: int = 2025) -> Decimal:
    """Obtener UVT para un año específico."""
    if year not in UVT:
        # Usar el año más reciente disponible
        year = max(UVT.keys())
    return Decimal(str(UVT[year]))


# ============================================================================
# FORMATOS DIAN
# ============================================================================

FORMATO_RETENCION = "1003"
FORMATO_EXOGENA_PAGOS = "1001"
FORMATO_EXOGENA_INGRESOS = "1007"
FORMATO_EXOGENA_CXC = "1008"
FORMATO_EXOGENA_CXP = "1009"

# Mapeo de formato exógena → formato retención
FORMATO_EXOGENA_A_RETENCION: Dict[str, str] = {
    "1001": "1003",
    "1007": "1003",
    "1008": "1003",
    "1009": "1003",
}


# ============================================================================
# CONCEPTOS DE RETENCIÓN DIAN
# ============================================================================

# ⚠️ CORREGIDO:
#   - Conceptos IVA 11/12/13 con nombres correctos (11=servicios, 13=honorarios)
#   - Agregados ICA: 21, 22, 23
CONCEPTOS_RETENCION_DIAN: Dict[str, str] = {
    # Renta
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
    # IVA
    "11": "ReteIVA Servicios",
    "12": "ReteIVA Bienes",
    "13": "ReteIVA Honorarios",
    # ICA
    "21": "ReteICA Actividades Comerciales",
    "22": "ReteICA Actividades de Servicios",
    "23": "ReteICA Actividades Industriales",
    # Otros
    "99": "Concepto Contable Múltiple",
}

# ⚠️ NUEVO: conceptos válidos por tipo (para validación contable)
CONCEPTOS_POR_TIPO: Dict[str, set] = {
    "renta": {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10"},
    "iva": {"11", "12", "13"},
    "ica": {"21", "22", "23"},
}


# ============================================================================
# PARÁMETROS GENERALES
# ============================================================================

# ⚠️ CORREGIDO: usar Decimal, no int
IVA_FRACCION = Decimal("0.19")  # 19% como fracción
IVA_PORCENTAJE = 19  # 19 como porcentaje entero (para mostrar)

ICA_PORCENTAJE_DEFAULT = Decimal("0.0033")  # 0.33% como fracción


def get_iva_fraccion() -> Decimal:
    """Retorna el IVA como fracción (0.19)."""
    return IVA_FRACCION


def get_iva_factor() -> Decimal:
    """
    Retorna el factor para convertir valor-con-IVA a valor-sin-IVA.
    factor = 1 + IVA = 1.19
    """
    return Decimal("1") + IVA_FRACCION


# ============================================================================
# TIPOS DE RETENCIÓN
# ============================================================================

TIPOS_RETENCION: Dict[str, str] = {
    "renta": "Retención en la fuente por renta",
    "iva": "Retención en la fuente por IVA",
    "ica": "Retención en la fuente por ICA",
}

# ⚠️ NUEVO: valores válidos para calcula_base_sobre
CALCULA_BASE_SOBRE_VALORES: Dict[str, str] = {
    "valor": "Sobre el valor sin IVA",
    "total": "Sobre el total (incluye IVA)",
    "iva": "Sobre el IVA generado",
}


# ============================================================================
# ESTADOS DE RETENCIÓN
# ============================================================================

ESTADOS_RETENCION: Dict[str, str] = {
    "procesado": "Calculada pero no reportada",
    "reportado": "Incluida en reporte DIAN",
    "error": "Error en el procesamiento",
    "no_aplica": "No aplica retención (tope mínimo)",
}


# ============================================================================
# MAPEO DE CONCEPTOS CONTABLES
# ============================================================================

CONCEPTO_CONTABLE_A_DIAN: Dict[str, str] = {
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
    "ReteIVA": "11",
    "ReteIVA Bienes": "12",
    "ReteIVA Servicios": "13",
    "ReteIVA Honorarios": "13",
    "ReteICA": "22",
}


# ============================================================================
# HELPERS
# ============================================================================

def get_concepto_dian_from_contable(concepto_contable: str) -> Optional[str]:
    """Obtener código DIAN desde el concepto contable."""
    return CONCEPTO_CONTABLE_A_DIAN.get(concepto_contable)


def es_concepto_valido_para_tipo(concepto: str, tipo: str) -> bool:
    """Verifica si un concepto DIAN corresponde a un tipo de retención."""
    return concepto in CONCEPTOS_POR_TIPO.get(tipo, set())


def get_conceptos_de_tipo(tipo: str) -> set:
    """Retorna los conceptos válidos para un tipo."""
    return CONCEPTOS_POR_TIPO.get(tipo, set())


def normalizar_tarifa(tarifa) -> Decimal:
    """
    Normaliza una tarifa a fracción [0, 1].

    Si viene como 3.5 (porcentaje), retorna 0.035.
    Si viene como 0.035 (fracción), retorna 0.035.

    Args:
        tarifa: Puede ser int, float, Decimal o str.

    Returns:
        Decimal en fracción [0, 1].
    """
    t = Decimal(str(tarifa))
    if t > 1:
        t = t / Decimal("100")
    return t


# ============================================================================
# EJECUCIÓN DIRECTA (para verificar)
# ============================================================================

if __name__ == "__main__":
    print("📊 Constantes cargadas:")
    print(f"   UVT 2025: ${UVT[2025]:,}")
    print(f"   IVA: {IVA_PORCENTAJE}% ({IVA_FRACCION})")
    print(f"   Formatos: {list(FORMATO_EXOGENA_A_RETENCION.keys())}")
    print(f"   Conceptos renta: {len(CONCEPTOS_POR_TIPO['renta'])}")
    print(f"   Conceptos IVA: {sorted(CONCEPTOS_POR_TIPO['iva'])}")
    print(f"   Conceptos ICA: {sorted(CONCEPTOS_POR_TIPO['ica'])}")