#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recargar reglas de mapeo desde JSON a la BD.

Uso:
    python scripts/recargar_reglas.py              # Carga real (UPSERT)
    python scripts/recargar_reglas.py --dry-run    # Solo valida
    python scripts/recargar_reglas.py --estadisticas
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.services.reglas_service import ReglasService


def main():
    parser = argparse.ArgumentParser(description="Recargar reglas de mapeo")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo valida, no escribe en BD")
    parser.add_argument("--estadisticas", action="store_true",
                        help="Mostrar estadísticas de reglas en BD")
    parser.add_argument("--reglas-dir", default="data/reglas",
                        help="Directorio de los JSON de reglas")
    args = parser.parse_args()

    print("=" * 60)
    print("RECARGA DE REGLAS DE MAPEO")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = ReglasService(db, Path(args.reglas_dir))

        if args.estadisticas:
            stats = service.estadisticas()
            print("\nEstadísticas en BD:")
            for k, v in stats.items():
                print(f"   {k}: {v}")
            return

        print("\nValidando reglas desde JSON...")
        try:
            reglas = service.loader.cargar_todas(validar=False)
        except FileNotFoundError as e:
            print(f"\nERROR: {e}")
            sys.exit(1)

        print(f"\n{len(reglas)} reglas encontradas")

        if args.dry_run:
            print("\nModo dry-run: no se escribió nada en BD.")
            return

        print("\nCargando a BD (UPSERT)...")
        resultado = service.recargar_desde_json(validar=False)

        print(f"\nResultado:")
        print(f"   Creadas:      {resultado['creadas']}")
        print(f"   Actualizadas: {resultado['actualizadas']}")
        print(f"   Sin cambios:  {resultado['sin_cambios']}")

        print("\nProceso completado")

    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()