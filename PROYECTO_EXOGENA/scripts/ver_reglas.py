#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificar reglas existentes en la base de datos

Este script muestra todas las reglas actuales en la BD
para poder hacer un script de carga/actualización inteligente.

Uso:
    python scripts/ver_reglas_db.py
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.mapping_rule import MappingRule


def ver_reglas():
    """Mostrar reglas existentes en la BD"""
    
    db = SessionLocal()
    
    try:
        reglas = db.query(MappingRule).order_by(MappingRule.puc_code).all()
        
        print("\n" + "="*80)
        print("📊 REGLAS EXISTENTES EN BASE DE DATOS")
        print("="*80)
        print(f"Total: {len(reglas)} reglas\n")
        
        if not reglas:
            print("⚠️ No hay reglas en la base de datos")
            print("   Ejecuta el script de carga inicial")
            return
        
        # Mostrar en formato tabla
        print(f"{'PUC':<12} | {'Formato':<8} | {'Concepto':<10} | {'Nombre':<30}")
        print("-" * 80)
        
        for r in reglas:
            print(f"{r.puc_code:<12} | {r.exogena_format:<8} | {r.exogena_concept:<10} | {r.puc_name[:30] if r.puc_name else ''}")
        
        # Mostrar resumen por formato
        print("\n" + "-"*80)
        print("📋 RESUMEN POR FORMATO:")
        print("-"*80)
        
        from collections import Counter
        formatos = Counter(r.exogena_format for r in reglas)
        for formato, count in formatos.items():
            print(f"  Formato {formato}: {count} reglas")
        
        print("\n" + "-"*80)
        print("📋 RESUMEN POR CONCEPTO:")
        print("-"*80)
        
        conceptos = Counter(r.exogena_concept for r in reglas)
        for concepto, count in conceptos.most_common(10):
            # Obtener nombre del concepto del primer registro que lo tenga
            ejemplo = next((r for r in reglas if r.exogena_concept == concepto), None)
            nombre = ejemplo.exogena_concept_name if ejemplo else ""
            print(f"  Concepto {concepto}: {count} reglas - {nombre}")
        
    finally:
        db.close()


if __name__ == "__main__":
    ver_reglas()