#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cálculo de la declaración de renta usando datos de la base de datos

Uso desde código:
    from app.services.declaracion_renta import calcular_declaracion
    resultado = calcular_declaracion()
"""

from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.renta import (
    Cliente, Proveedor, GastoOperativo, Nomina, ActivoFijo,
    Deuda, CuentaBancaria, Inversion, DeclaracionAnterior
)


def calcular_declaracion():
    """Calcular la declaración de renta a partir de los datos en BD"""
    
    db = SessionLocal()
    
    try:
        # 1. Ingresos
        ingresos_operacionales = db.query(func.sum(Cliente.ingresos_total)).scalar() or 0
        rendimientos_financieros = db.query(func.sum(CuentaBancaria.rendimientos_financieros)).scalar() or 0
        rendimientos_inversiones = db.query(func.sum(Inversion.rendimientos)).scalar() or 0
        ingresos_no_operacionales = rendimientos_financieros + rendimientos_inversiones
        total_ingresos = ingresos_operacionales + ingresos_no_operacionales
        
        # 2. Gastos deducibles
        compras = db.query(func.sum(Proveedor.compras_total)).scalar() or 0
        gastos_operativos = db.query(func.sum(GastoOperativo.valor_total_en_el_ano)).scalar() or 0
        
        # Nómina
        salarios = db.query(func.sum(Nomina.salario_mensual * 12)).scalar() or 0
        prestaciones = db.query(func.sum(Nomina.prestaciones_sociales_anual)).scalar() or 0
        aportes = db.query(func.sum(Nomina.aportes_seg_social_anual)).scalar() or 0
        gastos_nomina = salarios + prestaciones + aportes
        
        # Depreciación
        activos = db.query(ActivoFijo).all()
        depreciacion_anual = 0
        for a in activos:
            if a.tipo == "Vehículo":
                vida_util = 5
            elif a.tipo == "Inmueble":
                vida_util = 20
            else:
                vida_util = 1
            depreciacion_anual += a.valor_compra / vida_util
        
        intereses = db.query(func.sum(Deuda.interes_pagado_en_el_ano)).scalar() or 0
        impuesto_vehiculos = db.query(func.sum(ActivoFijo.impuesto_pagado)).scalar() or 0
        
        # ICA pagado (ajustar según tus datos, por ahora 0)
        ica_pagado = 0
        
        total_gastos = compras + gastos_operativos + gastos_nomina + depreciacion_anual + intereses + impuesto_vehiculos + ica_pagado
        
        # 3. Renta líquida gravable
        renta_liquida = total_ingresos - total_gastos
        
        # 4. Impuesto determinado (35%)
        tarifa = 0.35
        impuesto_determinado = renta_liquida * tarifa if renta_liquida > 0 else 0
        
        # 5. Créditos tributarios
        retenciones_clientes = db.query(func.sum(Cliente.retenciones_practicadas)).scalar() or 0
        retenciones_proveedores = db.query(func.sum(Proveedor.retenciones_sufridas)).scalar() or 0
        retenciones_sufridas = retenciones_clientes + retenciones_proveedores
        
        declaracion_ant = db.query(DeclaracionAnterior).filter(DeclaracionAnterior.ano == 2024).first()
        if declaracion_ant:
            anticipo = declaracion_ant.anticipo
            saldo_a_favor = declaracion_ant.saldo_a_favor
        else:
            anticipo = 0
            saldo_a_favor = 0
        
        creditos = retenciones_sufridas + anticipo + saldo_a_favor
        
        # 6. Saldo final
        saldo_final = impuesto_determinado - creditos
        
        # 7. Resultado
        return {
            "ingresos_operacionales": ingresos_operacionales,
            "ingresos_no_operacionales": ingresos_no_operacionales,
            "total_ingresos": total_ingresos,
            "compras": compras,
            "gastos_operativos": gastos_operativos,
            "gastos_nomina": gastos_nomina,
            "depreciacion_anual": depreciacion_anual,
            "intereses": intereses,
            "impuesto_vehiculos": impuesto_vehiculos,
            "ica_pagado": ica_pagado,
            "total_gastos": total_gastos,
            "renta_liquida": renta_liquida,
            "impuesto_determinado": impuesto_determinado,
            "retenciones_sufridas": retenciones_sufridas,
            "anticipo": anticipo,
            "saldo_a_favor": saldo_a_favor,
            "creditos_tributarios": creditos,
            "saldo_final": saldo_final,
            "es_saldo_a_favor": saldo_final < 0
        }
    
    finally:
        db.close()


def generar_reporte(resultado):
    """Generar un reporte formateado de la declaración de renta"""
    
    print("\n" + "="*60)
    print("DECLARACIÓN DE RENTA 2025 - RESUMEN")
    print("="*60)
    
    print(f"\n📊 INGRESOS:")
    print(f"   Operacionales: ${resultado['ingresos_operacionales']:,.0f}")
    print(f"   No operacionales: ${resultado['ingresos_no_operacionales']:,.0f}")
    print(f"   Total ingresos: ${resultado['total_ingresos']:,.0f}")
    
    print(f"\n📉 COSTOS Y GASTOS DEDUCIBLES:")
    print(f"   Compras: ${resultado['compras']:,.0f}")
    print(f"   Gastos operativos: ${resultado['gastos_operativos']:,.0f}")
    print(f"   Nómina: ${resultado['gastos_nomina']:,.0f}")
    print(f"   Depreciación: ${resultado['depreciacion_anual']:,.0f}")
    print(f"   Intereses: ${resultado['intereses']:,.0f}")
    print(f"   Impuesto vehicular: ${resultado['impuesto_vehiculos']:,.0f}")
    print(f"   ICA pagado: ${resultado['ica_pagado']:,.0f}")
    print(f"   Total gastos: ${resultado['total_gastos']:,.0f}")
    
    print(f"\n💰 RENTA LÍQUIDA GRAVABLE: ${resultado['renta_liquida']:,.0f}")
    print(f"\n💸 IMPUESTO DETERMINADO (35%): ${resultado['impuesto_determinado']:,.0f}")
    
    print(f"\n✅ CRÉDITOS TRIBUTARIOS:")
    print(f"   Retenciones sufridas: ${resultado['retenciones_sufridas']:,.0f}")
    print(f"   Anticipo 2024: ${resultado['anticipo']:,.0f}")
    print(f"   Saldo a favor 2024: ${resultado['saldo_a_favor']:,.0f}")
    print(f"   Total créditos: ${resultado['creditos_tributarios']:,.0f}")
    
    print("\n" + "="*60)
    if resultado['es_saldo_a_favor']:
        print(f"✅ SALDO A FAVOR (a favor de la empresa): ${abs(resultado['saldo_final']):,.0f}")
    else:
        print(f"⚠️ SALDO A PAGAR: ${resultado['saldo_final']:,.0f}")
    print("="*60)