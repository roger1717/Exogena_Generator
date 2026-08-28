#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cargar datos de los archivos Excel a la base de datos
Soporta:
- Archivo unificado: Terceros.xlsx
- Archivos separados: Clientes.xlsx, Proveedores.xlsx, etc.
- Detección automática de columnas
- Manejo robusto de columnas faltantes
"""

import pandas as pd
import sys
from pathlib import Path
import re

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.renta import (
    Cliente, Proveedor, GastoOperativo, Nomina, ActivoFijo,
    Deuda, CuentaBancaria, Inversion, DeclaracionAnterior
)


def normalize_column_name(col_name: str) -> str:
    """Normalizar nombre de columna: quitar espacios, mayúsculas, etc."""
    if col_name is None:
        return ""
    col_name = str(col_name).strip()
    col_name = re.sub(r'[^a-zA-Z0-9_]', '', col_name)
    return col_name


def detect_columns(df: pd.DataFrame, required: list) -> dict:
    """
    Detectar columnas necesarias en el DataFrame.
    Busca coincidencias insensibles a mayúsculas/minúsculas.
    """
    mapping = {}
    columns_lower = {normalize_column_name(col): col for col in df.columns}
    
    for req in required:
        req_lower = req.lower()
        found = None
        for key, original in columns_lower.items():
            if req_lower == key.lower():
                found = original
                break
        if found:
            mapping[req] = found
    return mapping


def safe_get(row, col, default=""):
    """Obtener valor de una columna de forma segura"""
    if col is None:
        return default
    try:
        val = row.get(col, default)
        if pd.isna(val):
            return default
        return val
    except:
        return default


def cargar_datos():
    """Cargar todos los datos desde Excel a la BD"""
    
    base_path = Path(__file__).parent.parent / "Docs" / "Datos" / "arc_xls"
    
    if not base_path.exists():
        print(f"❌ Directorio no encontrado: {base_path}")
        return
    
    db = SessionLocal()
    
    try:
        # ================================================================
        # 1. TERCEROS (Clientes + Proveedores)
        # ================================================================
        
        terceros_path = base_path / "Terceros.xlsx"
        if terceros_path.exists():
            print("📄 Cargando Terceros (archivo unificado)...")
            df = pd.read_excel(terceros_path)
            
            # Detectar columnas
            mapping = detect_columns(df, [
                "Nit", "Razon_Social", 
                "Ingresos_total", "Retenciones_practicadas",
                "Compras_total", "Retenciones_sufridas"
            ])
            
            print(f"   Mapeo detectado: {mapping}")
            
            if "Nit" not in mapping or "Razon_Social" not in mapping:
                print("❌ No se encontraron columnas 'Nit' y 'Razon_Social'")
                print(f"   Columnas disponibles: {df.columns.tolist()}")
                return
            
            # Variables para conteo
            count_clientes = 0
            count_proveedores = 0
            
            for _, row in df.iterrows():
                nit = str(safe_get(row, mapping.get("Nit"))).strip()
                razon = str(safe_get(row, mapping.get("Razon_Social"))).strip()
                
                if not nit or not razon:
                    continue
                
                # Clientes (si tienen ingresos)
                ingresos = safe_get(row, mapping.get("Ingresos_total"), 0)
                if ingresos and float(ingresos) > 0:
                    cliente = Cliente(
                        nit=nit,
                        razon_social=razon,
                        ingresos_total=float(ingresos),
                        retenciones_practicadas=float(safe_get(row, mapping.get("Retenciones_practicadas"), 0))
                    )
                    db.add(cliente)
                    count_clientes += 1
                
                # Proveedores (si tienen compras)
                compras = safe_get(row, mapping.get("Compras_total"), 0)
                if compras and float(compras) > 0:
                    proveedor = Proveedor(
                        nit=nit,
                        razon_social=razon,
                        compras_total=float(compras),
                        retenciones_sufridas=float(safe_get(row, mapping.get("Retenciones_sufridas"), 0))
                    )
                    db.add(proveedor)
                    count_proveedores += 1
            
            db.commit()
            print(f"   ✅ Clientes insertados: {count_clientes}")
            print(f"   ✅ Proveedores insertados: {count_proveedores}")
        
        # ================================================================
        # 2. GASTOS OPERATIVOS
        # ================================================================
        gastos_path = base_path / "Gastos_Operativos.xlsx"
        if gastos_path.exists():
            print("📄 Cargando Gastos Operativos...")
            df = pd.read_excel(gastos_path)
            mapping = detect_columns(df, ["Descripcion", "Valor_total_en_el_año"])
            
            count = 0
            for _, row in df.iterrows():
                desc = str(safe_get(row, mapping.get("Descripcion"), "Gasto sin descripción"))
                valor = safe_get(row, mapping.get("Valor_total_en_el_año"), 0)
                
                if float(valor) > 0:
                    gasto = GastoOperativo(
                        descripcion=desc,
                        valor_total_en_el_ano=float(valor)
                    )
                    db.add(gasto)
                    count += 1
            
            db.commit()
            print(f"   ✅ Gastos insertados: {count}")
        
        # ================================================================
        # 3. NÓMINA
        # ================================================================
        nomina_path = base_path / "Nominas.xlsx"
        if nomina_path.exists():
            print("📄 Cargando Nómina...")
            df = pd.read_excel(nomina_path)
            mapping = detect_columns(df, ["Empleado", "Salario_Mensual", "Prestaciones_Sociales_anual", "Aportes_Seg_Social_anual"])
            
            count = 0
            for _, row in df.iterrows():
                empleado = str(safe_get(row, mapping.get("Empleado"), "Empleado sin nombre"))
                salario = safe_get(row, mapping.get("Salario_Mensual"), 0)
                prestaciones = safe_get(row, mapping.get("Prestaciones_Sociales_anual"), 0)
                aportes = safe_get(row, mapping.get("Aportes_Seg_Social_anual"), 0)
                
                if float(salario) > 0:
                    nomina = Nomina(
                        empleado=empleado,
                        salario_mensual=float(salario),
                        prestaciones_sociales_anual=float(prestaciones),
                        aportes_seg_social_anual=float(aportes)
                    )
                    db.add(nomina)
                    count += 1
            
            db.commit()
            print(f"   ✅ Nómina insertada: {count}")
        
        # ================================================================
        # 4. ACTIVOS FIJOS
        # ================================================================
        activos_path = base_path / "Activos_Fijos.xlsx"
        if activos_path.exists():
            print("📄 Cargando Activos Fijos...")
            df = pd.read_excel(activos_path)
            mapping = detect_columns(df, ["Nombre", "Tipo", "Valor_Compra", "Impuesto_Pagado", "Vida_Util"])
            
            count = 0
            for _, row in df.iterrows():
                nombre = str(safe_get(row, mapping.get("Nombre"), "Activo sin nombre"))
                tipo = str(safe_get(row, mapping.get("Tipo"), "Equipo"))
                valor = safe_get(row, mapping.get("Valor_Compra"), 0)
                impuesto = safe_get(row, mapping.get("Impuesto_Pagado"), 0)
                vida = safe_get(row, mapping.get("Vida_Util"), 1)
                
                if float(valor) > 0:
                    activo = ActivoFijo(
                        nombre=nombre,
                        tipo=tipo,
                        valor_compra=float(valor),
                        impuesto_pagado=float(impuesto),
                        vida_util=int(vida)
                    )
                    db.add(activo)
                    count += 1
            
            db.commit()
            print(f"   ✅ Activos insertados: {count}")
        
        # ================================================================
        # 5. DEUDAS
        # ================================================================
        deudas_path = base_path / "Deudas.xlsx"
        if deudas_path.exists():
            print("📄 Cargando Deudas...")
            df = pd.read_excel(deudas_path)
            mapping = detect_columns(df, ["Descripcion", "Intereses_pagados_en_el_año"])
            
            count = 0
            for _, row in df.iterrows():
                desc = str(safe_get(row, mapping.get("Descripcion"), "Deuda sin descripción"))
                intereses = safe_get(row, mapping.get("Intereses_pagados_en_el_año"), 0)
                
                if float(intereses) > 0:
                    deuda = Deuda(
                        descripcion=desc,
                        interes_pagado_en_el_ano=float(intereses)
                    )
                    db.add(deuda)
                    count += 1
            
            db.commit()
            print(f"   ✅ Deudas insertadas: {count}")
        
        # ================================================================
        # 6. CUENTAS BANCARIAS
        # ================================================================
        bancos_path = base_path / "Cuentas_Bancarias.xlsx"
        if bancos_path.exists():
            print("📄 Cargando Cuentas Bancarias...")
            df = pd.read_excel(bancos_path)
            mapping = detect_columns(df, ["Entidad", "Numero_Cuenta", "Rendimientos_Financieros"])
            
            count = 0
            for _, row in df.iterrows():
                entidad = str(safe_get(row, mapping.get("Entidad"), "Banco"))
                numero = str(safe_get(row, mapping.get("Numero_Cuenta"), "0000"))
                rendimientos = safe_get(row, mapping.get("Rendimientos_Financieros"), 0)
                
                cuenta = CuentaBancaria(
                    entidad=entidad,
                    numero_cuenta=numero,
                    rendimientos_financieros=float(rendimientos)
                )
                db.add(cuenta)
                count += 1
            
            db.commit()
            print(f"   ✅ Cuentas insertadas: {count}")
        
        # ================================================================
        # 7. INVERSIONES
        # ================================================================
        inversiones_path = base_path / "Inversiones.xlsx"
        if inversiones_path.exists():
            print("📄 Cargando Inversiones...")
            df = pd.read_excel(inversiones_path)
            mapping = detect_columns(df, ["Descripcion", "Rendimientos"])
            
            count = 0
            for _, row in df.iterrows():
                desc = str(safe_get(row, mapping.get("Descripcion"), "Inversión"))
                rendimientos = safe_get(row, mapping.get("Rendimientos"), 0)
                
                inversion = Inversion(
                    descripcion=desc,
                    rendimientos=float(rendimientos)
                )
                db.add(inversion)
                count += 1
            
            db.commit()
            print(f"   ✅ Inversiones insertadas: {count}")
        
        # ================================================================
        # 8. DECLARACIÓN ANTERIOR
        # ================================================================
        decla_path = base_path / "Declaracion_Anterior_2024.xlsx"
        if decla_path.exists():
            print("📄 Cargando Declaración Anterior...")
            df = pd.read_excel(decla_path)
            mapping = detect_columns(df, ["Anticipo", "Saldo_a_favor"])
            
            anticipo = safe_get(df.iloc[0], mapping.get("Anticipo"), 0)
            saldo = safe_get(df.iloc[0], mapping.get("Saldo_a_favor"), 0)
            
            decla = DeclaracionAnterior(
                ano=2024,
                anticipo=float(anticipo),
                saldo_a_favor=float(saldo)
            )
            db.add(decla)
            db.commit()
            print(f"   ✅ Declaración anterior insertada")
        
        # ================================================================
        # FINAL
        # ================================================================
        
        print("\n✅ Todos los datos cargados exitosamente")
        
        # Mostrar resumen final
        print("\n📊 RESUMEN DE DATOS CARGADOS:")
        print(f"   Clientes: {db.query(Cliente).count()}")
        print(f"   Proveedores: {db.query(Proveedor).count()}")
        print(f"   Gastos operativos: {db.query(GastoOperativo).count()}")
        print(f"   Nómina: {db.query(Nomina).count()}")
        print(f"   Activos fijos: {db.query(ActivoFijo).count()}")
        print(f"   Deudas: {db.query(Deuda).count()}")
        print(f"   Cuentas bancarias: {db.query(CuentaBancaria).count()}")
        print(f"   Inversiones: {db.query(Inversion).count()}")
        print(f"   Declaración anterior: {db.query(DeclaracionAnterior).count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cargar_datos()