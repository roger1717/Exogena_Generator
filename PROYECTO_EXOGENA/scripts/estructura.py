#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificar estructura de la tabla mapping_rules

Este script muestra la estructura actual de la tabla para
saber si tiene los campos de retención.

Uso:
    python scripts/ver_estructura_db.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from app.core.database import engine
from app.models.mapping_rule import MappingRule


def ver_estructura():
    """Mostrar estructura de la tabla"""
    
    inspector = inspect(engine)
    columns = inspector.get_columns('mapping_rules')
    
    print("\n" + "="*60)
    print("📊 ESTRUCTURA DE TABLA: mapping_rules")
    print("="*60)
    
    print(f"\n{'Columna':<25} | {'Tipo':<20} | {'Nulo':<6} | {'Default'}")
    print("-"*80)
    
    for col in columns:
        nombre = col['name']
        tipo = str(col['type'])
        nulo = 'SÍ' if col['nullable'] else 'NO'
        default = col.get('default', '')
        print(f"{nombre:<25} | {tipo:<20} | {nulo:<6} | {default}")
    
    # Verificar campos de retención
    campos_retencion = ['concepto_retencion', 'tarifa_retencion', 'tope_minimo', 'aplica_iva', 'tipo_retencion']
    columnas_existentes = [col['name'] for col in columns]
    
    print("\n" + "="*60)
    print("🔍 VERIFICANDO CAMPOS DE RETENCIÓN")
    print("="*60)
    
    for campo in campos_retencion:
        existe = campo in columnas_existentes
        estado = "✅" if existe else "❌"
        print(f"{estado} {campo}: {'EXISTE' if existe else 'FALTA'}")
    
    if not all(c in columnas_existentes for c in campos_retencion):
        print("\n⚠️ Faltan campos de retención en la tabla")
        print("   Ejecuta la migración para agregarlos:")
        print("   alembic upgrade head")


if __name__ == "__main__":
    ver_estructura()