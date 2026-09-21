#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# C:\INSPECCION\PROYECTS\PROYECTO_CONTADURIA\PROYECTO_EXOGENA\scripts\unificar_reglas.py
"""
Unificar todas las reglas de mapeo en un solo archivo

Este script lee todos los archivos de reglas (retefuente, reteiva, reteica, exogena)
y los fusiona en un solo archivo reglas_mapeo.json

Uso:
    python scripts/unificar_reglas.py
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def cargar_reglas_desde_archivo(archivo: Path) -> List[Dict]:
    """Cargar reglas desde un archivo JSON"""
    if not archivo.exists():
        print(f"⚠️ Archivo no encontrado: {archivo}")
        return []
    
    with open(archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('reglas', [])


def unificar_reglas():
    """Unificar todas las reglas en un solo archivo"""
    
    base_dir = Path(__file__).parent.parent
    output_path = base_dir / "data" / "reglas_mapeo.json"
    reglas_dir = base_dir / "data" / "reglas_mapeo"
    
    print("\n" + "="*60)
    print("🔄 UNIFICANDO REGLAS DE MAPEO")
    print("="*60)
    
    # Crear estructura base
    maestro = {
        "version": "3.0.0",
        "fecha_actualizacion": datetime.now().strftime('%Y-%m-%d'),
        "uvt": {
            "2025": 47065,
            "2024": 45458
        },
        "formatos": {
            "exogena_a_retencion": {
                "1001": "1003",
                "1007": "1003",
                "1008": "1003",
                "1009": "1003"
            },
            "tipos_retencion": {
                "renta": "Retención en la fuente por renta",
                "iva": "Retención en la fuente por IVA",
                "ica": "Retención en la fuente por ICA"
            }
        },
        "parametros": {
            "iva_porcentaje": 19,
            "ica_porcentaje": 0.33
        },
        "reglas": []
    }
    
    # Cargar reglas de cada fuente
    todas_las_reglas = []
    fuentes_info = []
    
    fuentes = [
        ("retefuente", "retefuente.json", "ReteFuente"),
        ("reteiva", "reteiva.json", "ReteIVA"),
        ("reteica", "reteica.json", "ReteICA"),
        ("exogena", "exogena.json", "Exógena"),
    ]
    
    for nombre, archivo, descripcion in fuentes:
        print(f"\n📄 Cargando {descripcion}: {archivo}")
        ruta = reglas_dir / archivo
        reglas = cargar_reglas_desde_archivo(ruta)
        print(f"   ✅ {len(reglas)} reglas cargadas")
        todas_las_reglas.extend(reglas)
        fuentes_info.append({
            "nombre": nombre,
            "archivo": archivo,
            "descripcion": descripcion,
            "cantidad": len(reglas)
        })
    
    # Actualizar el maestro
    maestro['reglas'] = todas_las_reglas
    maestro['fecha_actualizacion'] = datetime.now().strftime('%Y-%m-%d')
    maestro['fuentes'] = fuentes_info
    
    # Guardar
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(maestro, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    for info in fuentes_info:
        print(f"   {info['descripcion']}: {info['cantidad']} reglas")
    print(f"\n   Total reglas: {len(todas_las_reglas)}")
    print(f"   Archivo generado: {output_path}")
    print("\n✅ Proceso completado exitosamente")


if __name__ == "__main__":
    unificar_reglas()