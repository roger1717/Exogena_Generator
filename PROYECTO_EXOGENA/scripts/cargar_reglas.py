#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cargar reglas desde reglas_mapeo.json a la base de datos (versión Python)
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.mapping_rule import MappingRule


def cargar_reglas():
    """Cargar reglas desde JSON a la BD"""
    
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "data" / "reglas_mapeo.json"
    
    if not json_path.exists():
        print(f"❌ No se encontró: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    reglas = data.get('reglas', [])
    print(f"📊 Leyendo {len(reglas)} reglas desde JSON")
    
    db = SessionLocal()
    
    try:
        # Contar reglas existentes
        existentes = db.query(MappingRule).count()
        print(f"📊 Reglas existentes en BD: {existentes}")
        
        if existentes > 0:
            respuesta = input("⚠️ ¿Deseas eliminar todas las reglas existentes y recargar? (s/N): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return
            
            # Eliminar todas las reglas
            db.query(MappingRule).delete()
            db.commit()
            print("🗑️ Reglas eliminadas")
        
        # Crear nuevas reglas
        creadas = 0
        for regla_data in reglas:
            if not regla_data.get('puc_code'):
                continue
            
            regla = MappingRule(
                puc_code=regla_data.get('puc_code'),
                puc_name=regla_data.get('puc_name'),
                exogena_format=regla_data.get('exogena_format', '1001'),
                exogena_concept=regla_data.get('exogena_concept'),
                exogena_concept_name=regla_data.get('exogena_concept_name'),
                concepto_retencion=regla_data.get('concepto_retencion'),
                tarifa_retencion=regla_data.get('tarifa_retencion'),
                tope_minimo=regla_data.get('tope_minimo'),
                aplica_iva=regla_data.get('aplica_iva', False),
                tipo_retencion=regla_data.get('tipo_retencion'),
                activo=regla_data.get('activo', True)
            )
            
            db.add(regla)
            creadas += 1
        
        db.commit()
        
        print(f"✅ {creadas} reglas creadas exitosamente")
        
        # Mostrar resumen
        total = db.query(MappingRule).count()
        activas = db.query(MappingRule).filter(MappingRule.activo == True).count()
        con_retencion = db.query(MappingRule).filter(
            MappingRule.concepto_retencion.isnot(None)
        ).count()
        
        # Contar por tipo
        renta = db.query(MappingRule).filter(MappingRule.tipo_retencion == 'renta').count()
        iva = db.query(MappingRule).filter(MappingRule.tipo_retencion == 'iva').count()
        ica = db.query(MappingRule).filter(MappingRule.tipo_retencion == 'ica').count()
        
        print(f"\n📊 Resumen final:")
        print(f"   Total reglas: {total}")
        print(f"   Activas: {activas}")
        print(f"   Con retención: {con_retencion}")
        print(f"   ReteFuente (renta): {renta}")
        print(f"   ReteIVA: {iva}")
        print(f"   ReteICA: {ica}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cargar_reglas()