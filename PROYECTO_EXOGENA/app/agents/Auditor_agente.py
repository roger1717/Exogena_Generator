#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Auditoría de Retenciones - Versión Robusta v2.1

Alineado con los modelos reales:
  - MappingRule: usa tipo_retencion, activo, aplica_iva, es_retencion(),
                 get_tarifa_float(), get_tope_float(), exogena_format,
                 exogena_concept, exogena_concept_name.
  - Retencion:   usa tipo_retencion, formato_asignado, concepto_exogena,
                 estado, observaciones, perfil_tributario, to_dict(),
                 get_tipo_nombre().

NOTA: 'calcula_base_sobre' y 'cliente' (ICA) NO están en MappingRule;
      se manejan como constantes de negocio desde reteica.json.

Autor: [Tu nombre]
Fecha: 2026-09-11
Versión: 2.1.0
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from app.core.database import SessionLocal
from app.models.retencion import Retencion
from app.models.mapping_rule import MappingRule
from app.core.constants import CONCEPTOS_RETENCION_DIAN


# ============================================================================
# CONSTANTES DE NEGOCIO
# (alineadas con retefuente.json, reteiva.json, reteica.json)
# ============================================================================

# Conceptos DIAN por tipo de retención
CONCEPTOS_POR_TIPO = {
    "renta": {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10"},
    "iva":   {"11", "12", "13"},
    "ica":   {"21", "22", "23"},
}

# Cuentas PUC por tipo (para inferencia cuando no hay regla)
CUENTAS_IVA = {"236535", "236536", "236537"}
PREFIJO_RENTA = "2365"
PREFIJO_ICA = "2368"

# Tolerancias
TOLERANCIA_TARIFA = 0.0001
TOLERANCIA_VALOR = 0.01

# Clientes ICA con tarifas específicas (según reteica.json)
# NOTA: esto NO está en MappingRule; se maneja como constante de negocio.
CLIENTES_ICA_TARIFAS = {
    "ALION": 0.001,
    "HOLCIM": 0.006,
    "INCAUCA": 0.008,
    "LACTALIS CHIA": 0.007,
    "LACTALIS MED": 0.006,
    "ACERÍAS": 0.006,
    "CEMEX": 0.00477,
    "CEMEX IBAGUE": 0.00477,
    "CEMEX MACEO": 0.008,
    "DUITAMA": 0.061,
}

# Para ICA, la base se calcula sobre el total (incluye IVA)
# NOTA: esto NO está en MappingRule; es regla de negocio.
CALCULA_BASE_SOBRE = {
    "ica": "total",
    "renta": "valor",
    "iva": "valor",
}


# ============================================================================
# HELPERS INTERNOS
# ============================================================================

def _limpiar_puc(puc: str) -> str:
    """Limpia el código PUC eliminando puntos y decimales."""
    if not puc:
        return ""
    puc_str = str(puc).strip()
    if '.' in puc_str:
        puc_str = puc_str.split('.')[0]
    return puc_str.strip()


def _limpiar_nit(nit: str) -> Tuple[str, Optional[int]]:
    """Limpia un NIT y extrae el DV si viene con guion."""
    nit_str = str(nit).strip()
    if '-' in nit_str:
        partes = nit_str.split('-')
        nit_base = ''.join(filter(str.isdigit, partes[0]))
        dv = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else None
        return nit_base, dv
    return ''.join(filter(str.isdigit, nit_str)), None


def _calcular_dv_nit(nit_base: str) -> int:
    """Calcula el DV de un NIT colombiano (módulo 11)."""
    pesos = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    suma = 0
    for i, digito in enumerate(reversed(nit_base)):
        suma += int(digito) * pesos[i % len(pesos)]
    residuo = suma % 11
    dv = 11 - residuo
    if dv == 11:
        dv = 0
    elif dv == 10:
        dv = 9
    return dv


def _inferir_tipo_por_puc(puc: str) -> Optional[str]:
    """Infiere el tipo de retención desde el PUC (fallback)."""
    puc_limpio = _limpiar_puc(puc)
    if puc_limpio in CUENTAS_IVA:
        return "iva"
    if puc_limpio.startswith(PREFIJO_ICA):
        return "ica"
    if puc_limpio.startswith(PREFIJO_RENTA):
        return "renta"
    return None


def _obtener_regla_dict(puc_code: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene la regla desde MappingRule (BD) usando los métodos del modelo.
    Retorna dict serializable o None.
    """
    puc_limpio = _limpiar_puc(puc_code)
    db = SessionLocal()
    try:
        regla = db.query(MappingRule).filter(
            MappingRule.puc_code == puc_limpio
        ).first()

        if not regla:
            return None

        # Usar métodos del modelo (¡ya existen!)
        return {
            "puc_code": regla.puc_code,
            "puc_name": regla.puc_name,
            "exogena_format": regla.exogena_format,
            "exogena_concept": regla.exogena_concept,
            "exogena_concept_name": regla.exogena_concept_name,
            "concepto_retencion": regla.concepto_retencion,
            "tarifa_retencion": regla.get_tarifa_float(),   # método del modelo
            "tope_minimo": regla.get_tope_float(),          # método del modelo
            "aplica_iva": bool(regla.aplica_iva),
            "tipo_retencion": regla.tipo_retencion,
            "activo": bool(regla.activo),
            "es_retencion": regla.es_retencion(),           # método del modelo
        }
    finally:
        db.close()


# ============================================================================
# HERRAMIENTAS (Tools)
# ============================================================================

@tool
def obtener_regla_puc(puc_code: str) -> str:
    """
    Obtiene la regla de mapeo desde MappingRule (BD) para un PUC.
    Devuelve tipo_retencion, tarifa, tope, concepto DIAN, aplica_iva,
    exogena_format, exogena_concept, y si está activa y es retención.

    Args:
        puc_code: Código PUC (ej: '236530', '236535', '236810').

    Returns:
        JSON string con la regla o mensaje de error.
    """
    regla = _obtener_regla_dict(puc_code)
    if not regla:
        tipo_inferido = _inferir_tipo_por_puc(puc_code)
        return json.dumps({
            "error": f"No se encontró regla en MappingRule para PUC {puc_code}",
            "tipo_inferido_por_puc": tipo_inferido,
            "sugerencia": "Verificar que la cuenta exista en mapping_rules",
        }, ensure_ascii=False, indent=2)
    return json.dumps(regla, ensure_ascii=False, indent=2, default=str)


@tool
def validar_calculo_retencion(
    base: float,
    tarifa: float,
    valor_retenido: float,
    tipo_retencion: str = "renta",
) -> str:
    """
    Valida el cálculo: base × tarifa = valor_retenido.
    Considera el tipo de retención para el mensaje.

    Args:
        base: Base gravable reportada.
        tarifa: Tarifa aplicada (ej: 0.10).
        valor_retenido: Valor retenido reportado.
        tipo_retencion: 'renta', 'iva' o 'ica'.

    Returns:
        Resultado de la validación.
    """
    calculado = base * tarifa
    diferencia = abs(calculado - valor_retenido)

    if diferencia <= TOLERANCIA_VALOR:
        return (
            f"✅ Cálculo correcto [{tipo_retencion}]: "
            f"{base:,.2f} × {tarifa:.4f} = {calculado:,.2f} "
            f"(reportado: {valor_retenido:,.2f})"
        )
    return (
        f"❌ Error de cálculo [{tipo_retencion}]: "
        f"esperado {calculado:,.2f}, reportado {valor_retenido:,.2f}, "
        f"diferencia {diferencia:,.2f}"
    )


@tool
def validar_nit_colombiano(nit: str) -> str:
    """
    Valida NIT colombiano. Acepta '900123456-1' o '9001234561'.
    Calcula DV con módulo 11 y lo compara con el reportado.

    Args:
        nit: NIT a validar.

    Returns:
        Resultado de la validación.
    """
    nit_base, dv_reportado = _limpiar_nit(nit)

    if len(nit_base) < 8:
        return f"❌ NIT demasiado corto: {nit} (base: {nit_base})"

    dv_calculado = _calcular_dv_nit(nit_base)

    if dv_reportado is None:
        return (
            f"⚠️ NIT sin DV explícito: {nit_base}. "
            f"DV calculado: {dv_calculado}."
        )

    if dv_calculado == dv_reportado:
        return f"✅ NIT válido: {nit_base}-{dv_reportado}"

    return (
        f"❌ NIT inválido: {nit_base}. "
        f"DV esperado {dv_calculado}, reportado {dv_reportado}"
    )


@tool
def validar_tipo_retencion(puc_code: str, tipo_reportado: str) -> str:
    """
    Valida que el tipo reportado coincida con el tipo de la regla
    y con el tipo inferido del PUC.

    Args:
        puc_code: Código PUC.
        tipo_reportado: Tipo reportado ('renta', 'iva', 'ica').

    Returns:
        Resultado de la validación.
    """
    tipo_inferido = _inferir_tipo_por_puc(puc_code)
    regla = _obtener_regla_dict(puc_code)
    tipo_regla = regla.get("tipo_retencion") if regla else None

    problemas = []
    if tipo_inferido and tipo_inferido != tipo_reportado:
        problemas.append(
            f"PUC sugiere '{tipo_inferido}' pero se reportó '{tipo_reportado}'"
        )
    if tipo_regla and tipo_regla != tipo_reportado:
        problemas.append(
            f"MappingRule dice '{tipo_regla}' pero se reportó '{tipo_reportado}'"
        )

    if problemas:
        return "❌ Inconsistencia de tipo: " + "; ".join(problemas)

    return f"✅ Tipo correcto: {tipo_reportado} (PUC: {puc_code})"


@tool
def validar_concepto_dian(concepto_dian: str, tipo_retencion: str) -> str:
    """
    Valida que el concepto DIAN corresponda al tipo de retención.
    Renta: 01-10 | IVA: 11-13 | ICA: 21-23.

    Args:
        concepto_dian: Código DIAN (ej: '01', '11', '22').
        tipo_retencion: 'renta', 'iva' o 'ica'.

    Returns:
        Resultado de la validación.
    """
    concepto_str = str(concepto_dian).strip().zfill(2)
    validos = CONCEPTOS_POR_TIPO.get(tipo_retencion, set())

    if concepto_str in validos:
        nombre = CONCEPTOS_RETENCION_DIAN.get(concepto_str, "Desconocido")
        return f"✅ Concepto {concepto_str} válido para {tipo_retencion}: {nombre}"

    return (
        f"❌ Concepto {concepto_str} NO corresponde a {tipo_retencion}. "
        f"Válidos: {sorted(validos)}"
    )


@tool
def validar_tarifa_contra_regla(puc_code: str, tarifa_reportada: float) -> str:
    """
    Valida la tarifa reportada contra MappingRule.tarifa_retencion.
    Considera tarifas específicas de clientes ICA (reteica.json).

    Args:
        puc_code: Código PUC.
        tarifa_reportada: Tarifa aplicada (ej: 0.10).

    Returns:
        Resultado de la validación.
    """
    regla = _obtener_regla_dict(puc_code)
    if not regla:
        return f"⚠️ No hay regla para PUC {puc_code}; no se puede validar tarifa"

    tarifa_regla = regla.get("tarifa_retencion")
    if tarifa_regla is None:
        return f"⚠️ Regla sin tarifa para PUC {puc_code}"

    # Si es ICA y hay cliente específico, verificar tarifa del cliente
    tipo = regla.get("tipo_retencion")
    if tipo == "ica":
        # Buscar en CLIENTES_ICA_TARIFAS por puc_name
        puc_name = (regla.get("puc_name") or "").upper()
        for cliente, tarifa_cliente in CLIENTES_ICA_TARIFAS.items():
            if cliente in puc_name:
                diff_cliente = abs(tarifa_cliente - tarifa_reportada)
                if diff_cliente <= TOLERANCIA_TARIFA:
                    return (
                        f"✅ Tarifa ICA correcta para cliente {cliente}: "
                        f"{tarifa_reportada:.5f}"
                    )
                return (
                    f"❌ Tarifa ICA incorrecta para cliente {cliente}: "
                    f"reportada {tarifa_reportada:.5f}, "
                    f"esperada {tarifa_cliente:.5f}"
                )

    diferencia = abs(float(tarifa_regla) - float(tarifa_reportada))
    if diferencia <= TOLERANCIA_TARIFA:
        return (
            f"✅ Tarifa correcta: {tarifa_reportada:.4f} "
            f"= regla {tarifa_regla:.4f} ({regla.get('puc_name')})"
        )

    return (
        f"❌ Tarifa incorrecta: reportada {tarifa_reportada:.4f}, "
        f"regla {tarifa_regla:.4f} para {regla.get('puc_name')}"
    )


@tool
def validar_tope_minimo(base_gravable: float, puc_code: str) -> str:
    """
    Valida que la base supere el tope mínimo de MappingRule.

    Args:
        base_gravable: Base gravable reportada.
        puc_code: Código PUC.

    Returns:
        Resultado de la validación.
    """
    regla = _obtener_regla_dict(puc_code)
    if not regla:
        return f"⚠️ No hay regla para PUC {puc_code}"

    tope = float(regla.get("tope_minimo") or 0)

    if base_gravable >= tope:
        return (
            f"✅ Base {base_gravable:,.2f} supera tope "
            f"{tope:,.0f} ({regla.get('puc_name')})"
        )

    return (
        f"⚠️ Base {base_gravable:,.2f} NO supera tope "
        f"{tope:,.0f} ({regla.get('puc_name')}); no debería retenerse"
    )


@tool
def validar_base_gravable(
    base_reportada: float,
    valor_total: float,
    tipo_retencion: str,
    aplica_iva: bool = False,
    iva_porcentaje: float = 0.19,
) -> str:
    """
    Valida coherencia de la base gravable con el valor total.
    - ICA: base = total (incluye IVA)
    - IVA: base = total / (1 + IVA)
    - Renta con aplica_iva=True: base = total / (1 + IVA)
    - Renta sin IVA: base = total

    Args:
        base_reportada: Base reportada.
        valor_total: Valor total de la transacción.
        tipo_retencion: 'renta', 'iva' o 'ica'.
        aplica_iva: Si la regla aplica IVA.
        iva_porcentaje: Porcentaje de IVA (0.19).

    Returns:
        Resultado de la validación.
    """
    if tipo_retencion == "ica":
        base_esperada = valor_total
        explicacion = "ICA: base sobre total (incluye IVA)"
    elif tipo_retencion == "iva":
        base_esperada = valor_total / (1 + iva_porcentaje)
        explicacion = "IVA: base sobre valor sin IVA"
    elif aplica_iva:
        base_esperada = valor_total / (1 + iva_porcentaje)
        explicacion = "Renta con aplica_iva=True: base sin IVA"
    else:
        base_esperada = valor_total
        explicacion = "Renta sin IVA: base sobre total"

    diferencia = abs(base_esperada - base_reportada)
    if diferencia <= TOLERANCIA_VALOR:
        return (
            f"✅ Base correcta: {base_reportada:,.2f} ≈ "
            f"{base_esperada:,.2f} ({explicacion})"
        )

    return (
        f"❌ Base inconsistente: reportada {base_reportada:,.2f}, "
        f"esperada {base_esperada:,.2f} ({explicacion})"
    )


@tool
def detectar_duplicados(retenciones_json: str) -> str:
    """
    Detecta duplicados por (comprobante, nit, concepto_dian, periodo, valor).

    Args:
        retenciones_json: JSON string con la lista de retenciones.

    Returns:
        Reporte de duplicados.
    """
    try:
        retenciones = json.loads(retenciones_json)
    except json.JSONDecodeError as e:
        return f"❌ Error al parsear JSON: {e}"

    vistos = {}
    duplicados = []

    for idx, r in enumerate(retenciones):
        clave = (
            str(r.get("comprobante", "")).strip(),
            str(r.get("nit_tercero", "")).strip(),
            str(r.get("concepto_dian", "")).strip(),
            str(r.get("periodo", "")).strip(),
            round(float(r.get("valor_retenido", 0)), 2),
        )
        if clave in vistos:
            duplicados.append({
                "indice_original": vistos[clave],
                "indice_duplicado": idx,
                "clave": clave,
            })
        else:
            vistos[clave] = idx

    if not duplicados:
        return f"✅ Sin duplicados en {len(retenciones)} retenciones"

    return (
        f"❌ {len(duplicados)} duplicados detectados:\n"
        + json.dumps(duplicados, ensure_ascii=False, indent=2, default=str)
    )


@tool
def validar_periodo(periodo: str, fecha: str = None) -> str:
    """
    Valida formato YYYY-MM y coherencia con fecha.

    Args:
        periodo: Período YYYY-MM.
        fecha: Fecha opcional YYYY-MM-DD.

    Returns:
        Resultado de la validación.
    """
    patron = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
    if not patron.match(str(periodo).strip()):
        return f"❌ Período inválido: '{periodo}'. Esperado YYYY-MM"

    if fecha:
        try:
            fecha_dt = datetime.strptime(str(fecha).strip()[:10], "%Y-%m-%d")
            periodo_fecha = fecha_dt.strftime("%Y-%m")
            if periodo_fecha != str(periodo).strip():
                return (
                    f"⚠️ Período {periodo} no coincide con fecha {fecha} "
                    f"(período de la fecha: {periodo_fecha})"
                )
        except ValueError:
            return f"⚠️ Fecha inválida: {fecha}"

    return f"✅ Período válido: {periodo}"


@tool
def obtener_concepto_dian_por_puc(puc_code: str) -> str:
    """
    Obtiene el concepto DIAN desde MappingRule.concepto_retencion.

    Args:
        puc_code: Código PUC.

    Returns:
        Concepto DIAN o mensaje de error.
    """
    regla = _obtener_regla_dict(puc_code)
    if not regla:
        return f"❌ No hay regla para PUC {puc_code}"

    concepto = regla.get("concepto_retencion")
    if not concepto:
        return f"⚠️ Regla para PUC {puc_code} sin concepto_retencion"

    nombre = CONCEPTOS_RETENCION_DIAN.get(str(concepto), "Desconocido")
    return (
        f"✅ PUC {puc_code} → Concepto {concepto} ({nombre}) "
        f"[{regla.get('puc_name')}, tipo: {regla.get('tipo_retencion')}]"
    )


# ============================================================================
# AGENTE PRINCIPAL
# ============================================================================

class AgenteAuditoriaRetenciones:
    """
    Agente de auditoría alineado con MappingRule y Retencion.
    """

    def __init__(self, openai_api_key: Optional[str] = None, verbose: bool = False):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró OPENAI_API_KEY")

        self.verbose = verbose

        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
            openai_api_key=self.api_key,
        )

        self.tools = [
            obtener_regla_puc,
            validar_calculo_retencion,
            validar_nit_colombiano,
            validar_tipo_retencion,
            validar_concepto_dian,
            validar_tarifa_contra_regla,
            validar_tope_minimo,
            validar_base_gravable,
            detectar_duplicados,
            validar_periodo,
            obtener_concepto_dian_por_puc,
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un AUDITOR EXPERTO EN RETENCIONES EN LA FUENTE de Colombia.

CONTEXTO DE LA APLICACIÓN (basado en MappingRule y Retencion):
- MappingRule tiene: puc_code, puc_name, exogena_format, exogena_concept,
  exogena_concept_name, concepto_retencion, tarifa_retencion, tope_minimo,
  aplica_iva, tipo_retencion ('renta'|'iva'|'ica'), activo.
- Retencion tiene: fecha, comprobante, nit_tercero, nombre_tercero,
  perfil_tributario, concepto_contable, concepto_dian, base_gravable,
  tarifa, valor_retenido, cuenta_pasivo, tipo_retencion, formato_asignado,
  concepto_exogena, periodo, estado ('procesado'|'reportado'|'error'|'no_aplica'),
  observaciones.
- Cuentas PUC: 2365xx → renta | 236535-537 → IVA | 2368xx → ICA.
- Conceptos DIAN: renta 01-10 | IVA 11-13 | ICA 21-23.
- ICA se calcula sobre el TOTAL (incluye IVA).
- Renta con aplica_iva=True se calcula sobre el valor SIN IVA.
- NIT viene como '900123456-1' o '9001234561'.
- Clientes ICA con tarifas propias: ALION, HOLCIM, INCAUCA, LACTALIS,
  ACERÍAS, CEMEX, DUITAMA.

TU TAREA:
Auditar cada retención detectando:
1. Errores de cálculo (base × tarifa ≠ valor_retenido).
2. NITs inválidos (DV módulo 11).
3. Inconsistencias de tipo (PUC vs tipo reportado vs MappingRule).
4. Conceptos DIAN que no corresponden al tipo.
5. Tarifas que no coinciden con MappingRule (o cliente ICA).
6. Bases que no superan el tope mínimo.
7. Bases incoherentes con el valor total (ICA vs renta vs IVA).
8. Duplicados.
9. Períodos mal formados o incoherentes.

METODOLOGÍA (orden recomendado):
1. obtener_regla_puc
2. validar_nit_colombiano
3. validar_tipo_retencion
4. validar_concepto_dian
5. validar_tarifa_contra_regla
6. validar_tope_minimo
7. validar_base_gravable (si aplica)
8. validar_calculo_retencion
9. validar_periodo

FORMATO DE RESPUESTA:
- ✅ OK: [breve]
- ⚠️ ADVERTENCIA: [breve]
- ❌ ERROR: [breve]

Al final incluye RESUMEN con totales y recomendaciones.
No inventes datos: si una herramienta falla, reporta el error tal cual.
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

    def _crear_executor(self) -> AgentExecutor:
        """Executor NUEVO por auditoría (memoria limpia)."""
        memoria = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=memoria,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=15,
            return_intermediate_steps=True,
        )

    def _formatear_prompt_retencion(self, r: Dict[str, Any]) -> str:
        """Construye el prompt para auditar UNA retención."""
        return f"""
Audita esta retención:

- Comprobante: {r.get('comprobante', 'N/A')}
- Fecha: {r.get('fecha', 'N/A')}
- Período: {r.get('periodo', 'N/A')}
- NIT Tercero: {r.get('nit_tercero', 'N/A')}
- Nombre Tercero: {r.get('nombre_tercero', 'N/A')}
- Perfil Tributario: {r.get('perfil_tributario', 'N/A')}
- Concepto Contable: {r.get('concepto_contable', 'N/A')}
- Concepto DIAN: {r.get('concepto_dian', 'N/A')}
- Cuenta PUC (pasivo): {r.get('cuenta_pasivo', 'N/A')}
- Tipo Retención: {r.get('tipo_retencion', 'N/A')}
- Base Gravable: {r.get('base_gravable', 0):,.2f}
- Tarifa: {r.get('tarifa', 0):.4f}
- Valor Retenido: {r.get('valor_retenido', 0):,.2f}
- Valor Total (con IVA): {r.get('valor_total', r.get('base_gravable', 0)):,.2f}
- Estado actual: {r.get('estado', 'N/A')}

Usa las herramientas en el orden recomendado y reporta hallazgos.
"""

    def auditar_retencion(self, retencion: Dict[str, Any]) -> Dict[str, Any]:
        """Audita UNA retención con executor limpio."""
        executor = self._crear_executor()
        prompt = self._formatear_prompt_retencion(retencion)

        try:
            resultado = executor.invoke({"input": prompt})
            return {
                "retencion": retencion,
                "auditoria": resultado.get("output", ""),
                "pasos_intermedios": [
                    {"tool": s[0].tool, "input": s[0].tool_input}
                    for s in resultado.get("intermediate_steps", [])
                ],
                "timestamp": datetime.now().isoformat(),
                "exito": True,
            }
        except Exception as e:
            return {
                "retencion": retencion,
                "auditoria": f"❌ Error en auditoría: {e}",
                "timestamp": datetime.now().isoformat(),
                "exito": False,
            }

    def auditar_multiples(
        self,
        retenciones: List[Dict[str, Any]],
        detectar_dup_global: bool = True,
    ) -> Dict[str, Any]:
        """
        Audita múltiples retenciones.
        Si detectar_dup_global=True, primero corre detección global de duplicados.
        """
        # 1. Detección global de duplicados
        reporte_duplicados = None
        if detectar_dup_global and len(retenciones) > 1:
            dup_tool = detectar_duplicados
            reporte_duplicados = dup_tool.invoke(
                {"retenciones_json": json.dumps(retenciones, default=str)}
            )

        # 2. Auditoría individual
        resultados = []
        for i, ret in enumerate(retenciones, 1):
            if self.verbose:
                print(f"🔍 Auditando {i}/{len(retenciones)}: {ret.get('comprobante')}")
            resultados.append(self.auditar_retencion(ret))

        return {
            "reporte_duplicados_global": reporte_duplicados,
            "resultados": resultados,
            "total": len(resultados),
            "timestamp": datetime.now().isoformat(),
        }

    def auditar_desde_bd(
        self,
        periodo: Optional[str] = None,
        tipo_retencion: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Audita retenciones desde la BD usando Retencion.to_dict().
        """
        db = SessionLocal()
        try:
            query = db.query(Retencion)
            if periodo:
                query = query.filter(Retencion.periodo == periodo)
            if tipo_retencion:
                query = query.filter(Retencion.tipo_retencion == tipo_retencion)

            registros = query.limit(limit).all()
            retenciones = [r.to_dict() for r in registros]  # método del modelo
        finally:
            db.close()

        if not retenciones:
            return {
                "mensaje": "No hay retenciones para auditar",
                "filtros": {"periodo": periodo, "tipo_retencion": tipo_retencion},
                "resultados": [],
            }

        return self.auditar_multiples(retenciones)

    def guardar_hallazgos_en_bd(
        self,
        resultados: List[Dict[str, Any]],
    ) -> int:
        """
        Guarda los hallazgos de auditoría en Retencion.observaciones y
        actualiza Retencion.estado según el resultado.
        Retorna el número de registros actualizados.
        """
        db = SessionLocal()
        actualizados = 0
        try:
            for res in resultados:
                ret_dict = res.get("retencion", {})
                ret_id = ret_dict.get("id")
                if not ret_id:
                    continue

                ret_bd = db.query(Retencion).filter(Retencion.id == ret_id).first()
                if not ret_bd:
                    continue

                auditoria = res.get("auditoria", "")
                ret_bd.observaciones = auditoria

                if "❌" in auditoria:
                    ret_bd.estado = "error"
                elif "⚠️" in auditoria:
                    ret_bd.estado = "no_aplica"
                else:
                    ret_bd.estado = "procesado"

                actualizados += 1

            db.commit()
        finally:
            db.close()

        return actualizados

    def generar_reporte_texto(self, resultados: List[Dict[str, Any]]) -> str:
        """Genera reporte resumido en texto."""
        total = len(resultados)
        errores = sum(1 for r in resultados if "❌" in r.get("auditoria", ""))
        advertencias = sum(1 for r in resultados if "⚠️" in r.get("auditoria", ""))
        ok = total - errores - advertencias

        lineas = [
            "\n" + "=" * 60,
            "📋 REPORTE DE AUDITORÍA DE RETENCIONES",
            "=" * 60,
            f"📊 Total auditadas: {total}",
            f"   ✅ OK: {ok}",
            f"   ⚠️ Advertencias: {advertencias}",
            f"   ❌ Errores: {errores}",
            "=" * 60,
        ]

        for res in resultados:
            ret = res.get("retencion", {})
            auditoria = res.get("auditoria", "")
            comp = ret.get("comprobante", "N/A")
            if "❌" in auditoria:
                lineas.append(f"\n🔴 ERROR en {comp}:\n{auditoria}")
            elif "⚠️" in auditoria:
                lineas.append(f"\n🟡 ADVERTENCIA en {comp}:\n{auditoria}")
            else:
                lineas.append(f"\n✅ OK: {comp}")

        lineas.append("\n" + "=" * 60)
        return "\n".join(lineas)


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    agente = AgenteAuditoriaRetenciones(verbose=True)

    # Ejemplo 1: auditar una retención manual
    retencion_ejemplo = {
        "id": 1,
        "comprobante": "AS-1046",
        "fecha": "2025-03-15",
        "periodo": "2025-03",
        "nit_tercero": "900123456-1",
        "nombre_tercero": "Empresa XYZ",
        "perfil_tributario": "Responsable IVA",
        "concepto_contable": "Arrendamientos",
        "concepto_dian": "01",
        "cuenta_pasivo": "236530",
        "tipo_retencion": "renta",
        "base_gravable": 1000000.0,
        "tarifa": 0.035,
        "valor_retenido": 35000.0,
        "valor_total": 1000000.0,
        "estado": "procesado",
    }

    resultado = agente.auditar_retencion(retencion_ejemplo)
    print(resultado["auditoria"])

    # Ejemplo 2: auditar desde BD
    # resultados = agente.auditar_desde_bd(periodo="2025-03", limit=50)
    # print(agente.generar_reporte_texto(resultados["resultados"]))
    # agente.guardar_hallazgos_en_bd(resultados["resultados"])