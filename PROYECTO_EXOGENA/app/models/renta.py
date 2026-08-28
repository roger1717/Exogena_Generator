#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelos para la declaración de renta

Almacena los datos de clientes, proveedores, gastos, nómina, activos, etc.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Cliente(Base):
    __tablename__ = "Terceros"
    
    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20), unique=True, index=True, nullable=False)
    razon_social = Column(String(255), nullable=False)
    ingresos_total = Column(Float, default=0)
    retenciones_practicadas = Column(Float, default=0)  # Retenciones que TE hicieron
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Proveedor(Base):
    __tablename__ = "proveedores"
    
    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20), unique=True, index=True, nullable=False)
    razon_social = Column(String(255), nullable=False)
    compras_total = Column(Float, default=0)
    retenciones_sufridas = Column(Float, default=0)  # Retenciones que TÚ les hiciste
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GastoOperativo(Base):
    __tablename__ = "gastos_operativos"
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    valor_total_en_el_ano = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Nomina(Base):
    __tablename__ = "nominas"
    
    id = Column(Integer, primary_key=True, index=True)
    empleado = Column(String(255), nullable=False)
    salario_mensual = Column(Float, default=0)
    prestaciones_sociales_anual = Column(Float, default=0)
    aportes_seg_social_anual = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ActivoFijo(Base):
    __tablename__ = "activos_fijos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False)  # Vehículo, Inmueble, Equipo, etc.
    valor_compra = Column(Float, default=0)
    impuesto_pagado = Column(Float, default=0)  # Impuesto vehicular
    vida_util = Column(Integer, default=1)  # Años
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Deuda(Base):
    __tablename__ = "deudas"
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    interes_pagado_en_el_ano = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CuentaBancaria(Base):
    __tablename__ = "cuentas_bancarias"
    
    id = Column(Integer, primary_key=True, index=True)
    entidad = Column(String(100), nullable=False)
    numero_cuenta = Column(String(50), nullable=False)
    rendimientos_financieros = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Inversion(Base):
    __tablename__ = "inversiones"
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    rendimientos = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclaracionAnterior(Base):
    __tablename__ = "declaraciones_anteriores"
    
    id = Column(Integer, primary_key=True, index=True)
    ano = Column(Integer, nullable=False)
    anticipo = Column(Float, default=0)
    saldo_a_favor = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())