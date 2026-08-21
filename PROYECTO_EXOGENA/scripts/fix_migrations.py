#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arreglar migraciones y agregar columnas de retención

Uso:
    python scripts/fix_migrations.py
"""

import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine, SessionLocal
from sqlalchemy import text, inspect


def fix_migrations():
    """Arreglar el estado de las migraciones"""
    
    print("\n" + "="*60)
    print("🔧 ARREGLANDO MIGRACIONES")
    print("="*60)
    
    # 1. Conectar a la BD y arreglar alembic_version
    db_path = Path("exogena.db")
    
    if db_path.exists():
        print("\n📊 Conectando a la base de datos...")
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Ver versión actual
            cursor.execute("SELECT * FROM alembic_version")
            version_actual = cursor.fetchone()
            print(f"   Versión actual en BD: {version_actual}")
            
            # Actualizar a la versión correcta
            if version_actual and version_actual[0] != '1ed6953c0420':
                print(f"   Actualizando versión a: 1ed6953c0420")
                cursor.execute("DELETE FROM alembic_version")
                cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('1ed6953c0420')")
                conn.commit()
                print("   ✅ Versión actualizada")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 2. Agregar columnas de retención
    print("\n📊 Agregando columnas de retención...")
    
    try:
        db = SessionLocal()
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('mapping_rules')]
        
        nuevas_columnas = [
            ("concepto_retencion", "VARCHAR(10)"),
            ("tarifa_retencion", "NUMERIC(10, 4)"),
            ("tope_minimo", "NUMERIC(15, 2)"),
            ("aplica_iva", "BOOLEAN DEFAULT 0"),
            ("tipo_retencion", "VARCHAR(20)"),
            ("activo", "BOOLEAN DEFAULT 1"),
        ]
        
        for col_name, col_type in nuevas_columnas:
            if col_name not in columns:
                print(f"   ✅ Agregando: {col_name}")
                db.execute(text(f"""
                    ALTER TABLE mapping_rules 
                    ADD COLUMN {col_name} {col_type}
                """))
                db.commit()
            else:
                print(f"   ⏭️ Ya existe: {col_name}")
        
        # Actualizar datos existentes
        print("\n📝 Actualizando datos existentes...")
        db.execute(text("""
            UPDATE mapping_rules 
            SET 
                concepto_retencion = CASE 
                    WHEN exogena_concept IN ('5024', '5002') THEN '03'
                    WHEN exogena_concept IN ('5025', '5005') THEN '01'
                    WHEN exogena_concept IN ('5026', '5006', '5007', '5012') THEN '02'
                    WHEN exogena_concept = '5010' THEN '09'
                    ELSE NULL
                END,
                tarifa_retencion = CASE 
                    WHEN exogena_concept IN ('5024', '5002') THEN 0.10
                    WHEN exogena_concept IN ('5025', '5005') THEN 0.035
                    WHEN exogena_concept IN ('5026', '5006') THEN 0.04
                    WHEN exogena_concept = '5007' THEN 0.04
                    WHEN exogena_concept = '5010' THEN 0.10
                    WHEN exogena_concept = '5012' THEN 0.04
                    ELSE NULL
                END,
                tope_minimo = CASE 
                    WHEN exogena_concept IN ('5024', '5002', '5026', '5006', '5007', '5012') THEN 100000
                    WHEN exogena_concept IN ('5025', '5005') THEN 0
                    WHEN exogena_concept = '5010' THEN 100000
                    ELSE NULL
                END,
                aplica_iva = CASE 
                    WHEN exogena_concept IN ('5024', '5002', '5026', '5006', '5007', '5012', '5010') THEN 1
                    WHEN exogena_concept IN ('5025', '5005') THEN 0
                    ELSE 0
                END,
                tipo_retencion = CASE 
                    WHEN exogena_concept IN ('5024', '5002', '5025', '5005', '5026', '5006', '5007', '5012', '5010') THEN 'renta'
                    ELSE NULL
                END,
                activo = CASE 
                    WHEN exogena_concept IN ('5024', '5002', '5025', '5005', '5026', '5006', '5007', '5012', '5010') THEN 1
                    ELSE 0
                END
        """))
        db.commit()
        
        # Verificar resultado
        print("\n📊 Verificando resultado...")
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(concepto_retencion) as con_retencion,
                SUM(activo) as activas
            FROM mapping_rules
        """))
        
        row = result.fetchone()
        print(f"   Total reglas: {row[0]}")
        print(f"   Con retención: {row[1]}")
        print(f"   Activas: {row[2]}")
        
        db.close()
        
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO")
        print("="*60)
        print("\nAhora puedes ejecutar:")
        print("   alembic current")
        print("   python scripts/estructura.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()


if __name__ == "__main__":
    fix_migrations()