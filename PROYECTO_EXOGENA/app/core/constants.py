#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONSTANTES DEL NEGOCIO
¡NO MODIFICAR MANUALMENTE!

Este archivo es GENERADO AUTOMÁTICAMENTE desde data/reglas_mapeo.json
Para actualizar, modificar los archivos en data/reglas_mapeo/ y ejecutar:
    python scripts/unificar_reglas.py
    python scripts/generar_constants.py

Última actualización: 2026-08-22
Versión: 2.0.0
"""

from decimal import Decimal
from typing import Dict, Optional, List


# ============================================================================
# UVT (Unidad de Valor Tributario)
# ============================================================================

UVT = {'2025': 47065, '2024': 45458}

def get_uvt(year: int = 2025) -> Decimal:
    """
    Obtener UVT para un año específico
    
    Args:
        year: Año a consultar
    
    Returns:
        Decimal: Valor UVT para el año solicitado
    """
    return Decimal(str(UVT.get(year, UVT.get(2025, 47065))))


# ============================================================================
# FORMATOS DIAN
# ============================================================================

FORMATOS_DIAN = {'exogena_a_retencion': {'1001': '1003', '1007': '1003', '1008': '1003', '1009': '1003'}, 'tipos_retencion': {'renta': 'Retención en la fuente por renta', 'iva': 'Retención en la fuente por IVA', 'ica': 'Retención en la fuente por ICA'}}

# Mapeo de formato exógena → formato retención
FORMATO_EXOGENA_A_RETENCION = {'1001': '1003', '1007': '1003', '1008': '1003', '1009': '1003'}


# ============================================================================
# CONCEPTOS DE RETENCIÓN DIAN
# ============================================================================

CONCEPTOS_RETENCION_DIAN = {'01': 'Arrendamientos', '02': 'Servicios Generales', '03': 'Honorarios', '04': 'Servicios Profesionales', '05': 'Comisiones', '06': 'Transporte de carga', '07': 'Servicios de restaurante', '08': 'Compra de bienes', '09': 'Intereses', '10': 'Regalías', '11': 'ReteIVA', '12': 'ReteIVA Bienes', '13': 'ReteIVA Servicios', '99': 'Concepto Contable Múltiple'}


# ============================================================================
# PARÁMETROS GENERALES
# ============================================================================

IVA_PORCENTAJE = 19
ICA_PORCENTAJE = 0.33


# ============================================================================
# REGLAS DE MAPEO (TODAS)
# ============================================================================

# Lista completa de reglas
REGLAS_MAPEO = [
    {
        "puc_code": "236530",
        "puc_name": "Retencion Arrendamientos 3.5%",
        "exogena_format": "1001",
        "exogena_concept": "5025",
        "exogena_concept_name": "Retenciones Arrendamientos",
        "concepto_retencion": "01",
        "tarifa_retencion": 0.035,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236515",
        "puc_name": "Retencion Honorarios 10%",
        "exogena_format": "1001",
        "exogena_concept": "5024",
        "exogena_concept_name": "Retenciones Honorarios",
        "concepto_retencion": "03",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236525",
        "puc_name": "Retencion Servicios 4%",
        "exogena_format": "1001",
        "exogena_concept": "5026",
        "exogena_concept_name": "Retenciones Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "512010",
        "puc_name": "Arrendamientos Bienes Inmuebles",
        "exogena_format": "1001",
        "exogena_concept": "5005",
        "exogena_concept_name": "Arrendamientos",
        "concepto_retencion": "01",
        "tarifa_retencion": 0.035,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "511005",
        "puc_name": "Honorarios Asesoria Juridica",
        "exogena_format": "1001",
        "exogena_concept": "5002",
        "exogena_concept_name": "Honorarios",
        "concepto_retencion": "03",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "511010",
        "puc_name": "Honorarios Revisoria Fiscal",
        "exogena_format": "1001",
        "exogena_concept": "5002",
        "exogena_concept_name": "Honorarios",
        "concepto_retencion": "03",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513505",
        "puc_name": "Servicios de Aseo y Vigilancia",
        "exogena_format": "1001",
        "exogena_concept": "5006",
        "exogena_concept_name": "Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513550",
        "puc_name": "Servicios de Transporte",
        "exogena_format": "1001",
        "exogena_concept": "5006",
        "exogena_concept_name": "Servicios",
        "concepto_retencion": "06",
        "tarifa_retencion": 0.01,
        "tope_minimo": 100000,
        "aplica_iva": False,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513535",
        "puc_name": "Servicios Mantenimiento y Reparacion",
        "exogena_format": "1001",
        "exogena_concept": "5006",
        "exogena_concept_name": "Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513005",
        "puc_name": "Seguros y Polizas",
        "exogena_format": "1001",
        "exogena_concept": "5007",
        "exogena_concept_name": "Seguros",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "519530",
        "puc_name": "Utiles, Papeleria y Fotocopias",
        "exogena_format": "1001",
        "exogena_concept": "5012",
        "exogena_concept_name": "Gastos Varios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "519525",
        "puc_name": "Elementos de Aseo y Cafeteria",
        "exogena_format": "1001",
        "exogena_concept": "5012",
        "exogena_concept_name": "Gastos Varios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "515305",
        "puc_name": "Intereses y Gastos Financieros",
        "exogena_format": "1001",
        "exogena_concept": "5010",
        "exogena_concept_name": "Gastos Financieros",
        "concepto_retencion": "09",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236505",
        "puc_name": "Retencion Servicios 2.5%",
        "exogena_format": "1001",
        "exogena_concept": "5026",
        "exogena_concept_name": "Retenciones Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.025,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236535",
        "puc_name": "Retencion IVA 15%",
        "exogena_format": "1001",
        "exogena_concept": "5001",
        "exogena_concept_name": "Retenciones IVA",
        "concepto_retencion": "11",
        "tarifa_retencion": 0.15,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "iva",
        "calcula_base_sobre": "iva",
        "activo": True
    },
    {
        "puc_code": "236536",
        "puc_name": "Retencion IVA Bienes 15%",
        "exogena_format": "1001",
        "exogena_concept": "5001",
        "exogena_concept_name": "Retenciones IVA Bienes",
        "concepto_retencion": "12",
        "tarifa_retencion": 0.15,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "iva",
        "calcula_base_sobre": "iva",
        "activo": True
    },
    {
        "puc_code": "236537",
        "puc_name": "Retencion IVA Servicios 15%",
        "exogena_format": "1001",
        "exogena_concept": "5001",
        "exogena_concept_name": "Retenciones IVA Servicios",
        "concepto_retencion": "13",
        "tarifa_retencion": 0.15,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "iva",
        "calcula_base_sobre": "iva",
        "activo": True
    },
    {
        "puc_code": "413505",
        "puc_name": "Venta de Mercancias / Productos",
        "exogena_format": "1007",
        "exogena_concept": "8001",
        "exogena_concept_name": "Ingresos Brutos",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "417005",
        "puc_name": "Devoluciones en Ventas",
        "exogena_format": "1007",
        "exogena_concept": "8002",
        "exogena_concept_name": "Devoluciones",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "421005",
        "puc_name": "Ingresos Financieros Intereses",
        "exogena_format": "1007",
        "exogena_concept": "8003",
        "exogena_concept_name": "Ingresos Financieros",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "130505",
        "puc_name": "Clientes Nacionales",
        "exogena_format": "1008",
        "exogena_concept": "9001",
        "exogena_concept_name": "Cuentas por Cobrar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "136505",
        "puc_name": "Cuentas por Cobrar a Empleados",
        "exogena_format": "1008",
        "exogena_concept": "9001",
        "exogena_concept_name": "Cuentas por Cobrar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "220505",
        "puc_name": "Proveedores Nacionales",
        "exogena_format": "1009",
        "exogena_concept": "9002",
        "exogena_concept_name": "Cuentas por Pagar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "233595",
        "puc_name": "Costos y Gastos por Pagar Diversos",
        "exogena_format": "1009",
        "exogena_concept": "9002",
        "exogena_concept_name": "Cuentas por Pagar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    }
]

# ============================================================================
# REGLAS POR TIPO DE RETENCIÓN
# ============================================================================

# Reglas de ReteFuente (Renta)
REGLAS_RENTA = [
    {
        "puc_code": "236530",
        "puc_name": "Retencion Arrendamientos 3.5%",
        "exogena_format": "1001",
        "exogena_concept": "5025",
        "exogena_concept_name": "Retenciones Arrendamientos",
        "concepto_retencion": "01",
        "tarifa_retencion": 0.035,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236515",
        "puc_name": "Retencion Honorarios 10%",
        "exogena_format": "1001",
        "exogena_concept": "5024",
        "exogena_concept_name": "Retenciones Honorarios",
        "concepto_retencion": "03",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236525",
        "puc_name": "Retencion Servicios 4%",
        "exogena_format": "1001",
        "exogena_concept": "5026",
        "exogena_concept_name": "Retenciones Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "512010",
        "puc_name": "Arrendamientos Bienes Inmuebles",
        "exogena_format": "1001",
        "exogena_concept": "5005",
        "exogena_concept_name": "Arrendamientos",
        "concepto_retencion": "01",
        "tarifa_retencion": 0.035,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "511005",
        "puc_name": "Honorarios Asesoria Juridica",
        "exogena_format": "1001",
        "exogena_concept": "5002",
        "exogena_concept_name": "Honorarios",
        "concepto_retencion": "03",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "511010",
        "puc_name": "Honorarios Revisoria Fiscal",
        "exogena_format": "1001",
        "exogena_concept": "5002",
        "exogena_concept_name": "Honorarios",
        "concepto_retencion": "03",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513505",
        "puc_name": "Servicios de Aseo y Vigilancia",
        "exogena_format": "1001",
        "exogena_concept": "5006",
        "exogena_concept_name": "Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513550",
        "puc_name": "Servicios de Transporte",
        "exogena_format": "1001",
        "exogena_concept": "5006",
        "exogena_concept_name": "Servicios",
        "concepto_retencion": "06",
        "tarifa_retencion": 0.01,
        "tope_minimo": 100000,
        "aplica_iva": False,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513535",
        "puc_name": "Servicios Mantenimiento y Reparacion",
        "exogena_format": "1001",
        "exogena_concept": "5006",
        "exogena_concept_name": "Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "513005",
        "puc_name": "Seguros y Polizas",
        "exogena_format": "1001",
        "exogena_concept": "5007",
        "exogena_concept_name": "Seguros",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "519530",
        "puc_name": "Utiles, Papeleria y Fotocopias",
        "exogena_format": "1001",
        "exogena_concept": "5012",
        "exogena_concept_name": "Gastos Varios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "519525",
        "puc_name": "Elementos de Aseo y Cafeteria",
        "exogena_format": "1001",
        "exogena_concept": "5012",
        "exogena_concept_name": "Gastos Varios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.04,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "515305",
        "puc_name": "Intereses y Gastos Financieros",
        "exogena_format": "1001",
        "exogena_concept": "5010",
        "exogena_concept_name": "Gastos Financieros",
        "concepto_retencion": "09",
        "tarifa_retencion": 0.1,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    },
    {
        "puc_code": "236505",
        "puc_name": "Retencion Servicios 2.5%",
        "exogena_format": "1001",
        "exogena_concept": "5026",
        "exogena_concept_name": "Retenciones Servicios",
        "concepto_retencion": "02",
        "tarifa_retencion": 0.025,
        "tope_minimo": 100000,
        "aplica_iva": True,
        "tipo_retencion": "renta",
        "activo": True
    }
]

# Reglas de ReteIVA
REGLAS_IVA = [
    {
        "puc_code": "236535",
        "puc_name": "Retencion IVA 15%",
        "exogena_format": "1001",
        "exogena_concept": "5001",
        "exogena_concept_name": "Retenciones IVA",
        "concepto_retencion": "11",
        "tarifa_retencion": 0.15,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "iva",
        "calcula_base_sobre": "iva",
        "activo": True
    },
    {
        "puc_code": "236536",
        "puc_name": "Retencion IVA Bienes 15%",
        "exogena_format": "1001",
        "exogena_concept": "5001",
        "exogena_concept_name": "Retenciones IVA Bienes",
        "concepto_retencion": "12",
        "tarifa_retencion": 0.15,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "iva",
        "calcula_base_sobre": "iva",
        "activo": True
    },
    {
        "puc_code": "236537",
        "puc_name": "Retencion IVA Servicios 15%",
        "exogena_format": "1001",
        "exogena_concept": "5001",
        "exogena_concept_name": "Retenciones IVA Servicios",
        "concepto_retencion": "13",
        "tarifa_retencion": 0.15,
        "tope_minimo": 0,
        "aplica_iva": False,
        "tipo_retencion": "iva",
        "calcula_base_sobre": "iva",
        "activo": True
    }
]

# Reglas de Exógena (sin retención)
REGLAS_EXOGENA = [
    {
        "puc_code": "413505",
        "puc_name": "Venta de Mercancias / Productos",
        "exogena_format": "1007",
        "exogena_concept": "8001",
        "exogena_concept_name": "Ingresos Brutos",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "417005",
        "puc_name": "Devoluciones en Ventas",
        "exogena_format": "1007",
        "exogena_concept": "8002",
        "exogena_concept_name": "Devoluciones",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "421005",
        "puc_name": "Ingresos Financieros Intereses",
        "exogena_format": "1007",
        "exogena_concept": "8003",
        "exogena_concept_name": "Ingresos Financieros",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "130505",
        "puc_name": "Clientes Nacionales",
        "exogena_format": "1008",
        "exogena_concept": "9001",
        "exogena_concept_name": "Cuentas por Cobrar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "136505",
        "puc_name": "Cuentas por Cobrar a Empleados",
        "exogena_format": "1008",
        "exogena_concept": "9001",
        "exogena_concept_name": "Cuentas por Cobrar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "220505",
        "puc_name": "Proveedores Nacionales",
        "exogena_format": "1009",
        "exogena_concept": "9002",
        "exogena_concept_name": "Cuentas por Pagar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    },
    {
        "puc_code": "233595",
        "puc_name": "Costos y Gastos por Pagar Diversos",
        "exogena_format": "1009",
        "exogena_concept": "9002",
        "exogena_concept_name": "Cuentas por Pagar",
        "concepto_retencion": None,
        "tarifa_retencion": None,
        "tope_minimo": None,
        "aplica_iva": False,
        "tipo_retencion": None,
        "activo": True
    }
]


# ============================================================================
# REGLAS DE MAPEO POR PUC (para búsqueda rápida)
# ============================================================================

REGLAS_POR_PUC = {
    r['puc_code']: r for r in REGLAS_MAPEO if r.get('activo', True)
}

# ============================================================================
# REGLAS DE RETENCIÓN (todas las que aplican)
# ============================================================================

REGLAS_RETENCION = [
    r for r in REGLAS_MAPEO 
    if r.get('activo', True) and r.get('concepto_retencion') is not None
]

REGLAS_RETENCION_POR_PUC = {
    r['puc_code']: r for r in REGLAS_RETENCION
}

# ============================================================================
# REGLAS DE RETENCIÓN POR TIPO
# ============================================================================

REGLAS_RENTA_POR_PUC = {
    r['puc_code']: r for r in REGLAS_RENTA if r.get('activo', True)
}

REGLAS_IVA_POR_PUC = {
    r['puc_code']: r for r in REGLAS_IVA if r.get('activo', True)
}


# ============================================================================
# MAPEO DE CONCEPTOS
# ============================================================================

# Mapeo de concepto exógena → concepto retención
CONCEPTO_EXOGENA_A_RETENCION = {
    r['exogena_concept']: r['concepto_retencion']
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}

# Mapeo de concepto contable → código DIAN
CONCEPTO_CONTABLE_A_DIAN = {
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
}

# ============================================================================
# CONSTANTES DERIVADAS
# ============================================================================

# Lista de códigos de concepto que aplican para retención
CONCEPTOS_CON_RETENCION = list({
    r['concepto_retencion'] for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
})

# Topes mínimos por concepto (en COP)
TOPES_MINIMOS = {
    r['concepto_retencion']: Decimal(str(r['tope_minimo']))
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None and r.get('tope_minimo') is not None
}

# Tarifas por concepto
TARIFAS_RETENCION = {
    r['concepto_retencion']: Decimal(str(r['tarifa_retencion']))
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None and r.get('tarifa_retencion') is not None
}

# ¿Aplica IVA en la base de cálculo?
APLICA_IVA_EN_BASE = {
    r['concepto_retencion']: r.get('aplica_iva', False)
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}

# Tipos de retención por concepto
TIPOS_RETENCION_POR_CONCEPTO = {
    r['concepto_retencion']: r.get('tipo_retencion', 'renta')
    for r in REGLAS_RETENCION
    if r.get('concepto_retencion') is not None
}

# ============================================================================
# CONSTANTES FIJAS
# ============================================================================

# Formato DIAN para retenciones
FORMATO_RETENCION = "1003"

# Tipos de retención disponibles
TIPOS_RETENCION = {
    "renta": "Retención en la fuente por renta",
    "iva": "Retención en la fuente por IVA",
    "ica": "Retención en la fuente por ICA",
}

# Estados de una retención
ESTADOS_RETENCION = {
    "procesado": "Calculada pero no reportada",
    "reportado": "Incluida en reporte DIAN",
    "error": "Error en el procesamiento",
    "no_aplica": "No aplica retención (tope mínimo)",
}

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def obtener_regla(puc_code: str) -> Optional[Dict]:
    """
    Obtener regla de mapeo por código PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        Dict con la regla o None si no existe
    """
    return REGLAS_POR_PUC.get(puc_code)


def obtener_regla_retencion(puc_code: str) -> Optional[Dict]:
    """
    Obtener regla de retención por código PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        Dict con la regla de retención o None si no aplica
    """
    return REGLAS_RETENCION_POR_PUC.get(puc_code)


def obtener_regla_renta(puc_code: str) -> Optional[Dict]:
    """
    Obtener regla de ReteFuente (renta) por código PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        Dict con la regla o None si no existe
    """
    return REGLAS_RENTA_POR_PUC.get(puc_code)


def obtener_regla_iva(puc_code: str) -> Optional[Dict]:
    """
    Obtener regla de ReteIVA por código PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        Dict con la regla o None si no existe
    """
    return REGLAS_IVA_POR_PUC.get(puc_code)


def es_cuenta_retencion(puc_code: str) -> bool:
    """
    Determinar si una cuenta aplica para retención
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        True si aplica retención, False en caso contrario
    """
    regla = obtener_regla_retencion(puc_code)
    return regla is not None and regla.get('activo', True)


def get_tipo_retencion(puc_code: str) -> Optional[str]:
    """
    Obtener el tipo de retención para una cuenta PUC
    
    Args:
        puc_code: Código de cuenta contable
    
    Returns:
        str: 'renta', 'iva', 'ica' o None
    """
    regla = obtener_regla_retencion(puc_code)
    return regla.get('tipo_retencion') if regla else None


def get_tarifa_retencion(concepto_dian: str) -> Decimal:
    """
    Obtener tarifa de retención por concepto DIAN
    
    Args:
        concepto_dian: Código de concepto DIAN (ej: '01')
    
    Returns:
        Decimal: Tarifa de retención
    """
    return TARIFAS_RETENCION.get(concepto_dian, Decimal('0'))


def get_tope_minimo(concepto_dian: str) -> Decimal:
    """
    Obtener tope mínimo por concepto DIAN
    
    Args:
        concepto_dian: Código de concepto DIAN (ej: '01')
    
    Returns:
        Decimal: Tope mínimo en COP
    """
    return TOPES_MINIMOS.get(concepto_dian, Decimal('0'))


def get_concepto_dian_from_contable(concepto_contable: str) -> Optional[str]:
    """
    Obtener código DIAN desde el concepto contable
    
    Args:
        concepto_contable: Nombre del concepto contable
    
    Returns:
        str: Código DIAN o None si no existe
    """
    return CONCEPTO_CONTABLE_A_DIAN.get(concepto_contable)


def get_reglas_activas() -> List[Dict]:
    """
    Obtener lista de reglas activas
    
    Returns:
        List[Dict]: Lista de reglas activas
    """
    return [r for r in REGLAS_MAPEO if r.get('activo', True)]


def get_reglas_por_formato(formato: str) -> List[Dict]:
    """
    Obtener reglas por formato DIAN
    
    Args:
        formato: Código de formato (ej: '1001')
    
    Returns:
        List[Dict]: Lista de reglas para el formato
    """
    return [
        r for r in REGLAS_MAPEO 
        if r.get('exogena_format') == formato and r.get('activo', True)
    ]


def get_iva_porcentaje() -> int:
    """
    Obtener el porcentaje de IVA configurado
    
    Returns:
        int: Porcentaje de IVA (ej: 19)
    """
    return IVA_PORCENTAJE


# ============================================================================
# EJECUCIÓN DIRECTA (para pruebas)
# ============================================================================

if __name__ == "__main__":
    # Mostrar resumen al ejecutar el script directamente
    print("📊 Resumen de reglas cargadas:")
    print(f"   Total reglas: {len(REGLAS_MAPEO)}")
    print(f"   Reglas activas: {len(get_reglas_activas())}")
    print(f"   Reglas de retención: {len(REGLAS_RETENCION)}")
    print(f"   ReteFuente (renta): {len(REGLAS_RENTA)}")
    print(f"   ReteIVA: {len(REGLAS_IVA)}")
    print(f"   Exógena: {len(REGLAS_EXOGENA)}")
    print(f"   Conceptos con retención: {len(CONCEPTOS_CON_RETENCION)}")
    print(f"   UVT 2025: ${UVT.get(2025):,}")
    print(f"   IVA: {IVA_PORCENTAJE}%")
