#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de archivos XML para Retenciones en la Fuente

Genera XML separados por tipo de retención (ReteFuente, ReteIVA, ReteICA)
con nombres descriptivos.

Autor: [Tu nombre]
Fecha: 2026-08-22
Versión: 2.0.0
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class XMLGenerator:
    """
    Generador de archivos XML para retenciones
    """
    
    # Mapeo de tipos de retención a nombres descriptivos
    TIPO_A_NOMBRE = {
        "renta": "ReteFuente",
        "iva": "ReteIVA",
        "ica": "ReteICA",
    }
    
    TIPO_A_CODIGO = {
        "renta": "1003",
        "iva": "1003",
        "ica": "1003",
    }
    
    def __init__(self, output_dir: Path = Path("outputs/xml")):
        """
        Inicializar el generador
        
        Args:
            output_dir: Directorio de salida para los archivos XML
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generar_xml_retenciones(
        self,
        retenciones: List[Dict],
        periodo: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> Path:
        """
        Generar XML de retenciones con nombre descriptivo
        
        Args:
            retenciones: Lista de retenciones procesadas
            periodo: Período (YYYY-MM)
            tipo: Tipo de retención (renta, iva, ica)
        
        Returns:
            Path del archivo generado
        """
        if not retenciones:
            raise ValueError("No hay retenciones para generar")
        
        # Determinar el tipo
        if tipo is None and retenciones:
            tipo = retenciones[0].get('tipo_retencion', 'renta')
        
        nombre_tipo = self.TIPO_A_NOMBRE.get(tipo, "Retenciones")
        codigo_formato = self.TIPO_A_CODIGO.get(tipo, "1003")
        
        if periodo:
            filename = f"{codigo_formato}-{nombre_tipo}-{periodo}.xml"
        else:
            filename = f"{codigo_formato}-{nombre_tipo}-{datetime.now().strftime('%Y%m%d')}.xml"
        
        file_path = self.output_dir / filename
        
        # Crear estructura XML
        root = etree.Element("InformacionExogena")
        etree.SubElement(root, "Version").text = "1.0"
        etree.SubElement(root, "Año").text = periodo[:4] if periodo else "2025"
        etree.SubElement(root, "Periodo").text = periodo[5:] if periodo else "01"
        etree.SubElement(root, "Formato").text = codigo_formato
        etree.SubElement(root, "TipoRetencion").text = nombre_tipo
        etree.SubElement(root, "FechaGeneracion").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Detalle
        detalle = etree.SubElement(root, "Detalle")
        
        for item in retenciones:
            if item.get('valor_retenido', 0) > 0:
                registro = etree.SubElement(detalle, "Registro")
                
                nit = etree.SubElement(registro, "NitTercero")
                nit.text = str(item.get('nit_tercero', ''))
                
                nombre = etree.SubElement(registro, "NombreTercero")
                nombre.text = str(item.get('nombre_tercero', ''))
                
                concepto = etree.SubElement(registro, "Concepto")
                concepto.text = str(item.get('concepto_dian', ''))
                
                base = etree.SubElement(registro, "BaseGravable")
                base.text = f"{item.get('base_gravable', 0):.2f}"
                
                valor = etree.SubElement(registro, "ValorRetenido")
                valor.text = f"{item.get('valor_retenido', 0):.2f}"
                
                tarifa = etree.SubElement(registro, "Tarifa")
                tarifa.text = f"{item.get('tarifa', 0):.4f}"
                
                cuenta = etree.SubElement(registro, "CuentaPasivo")
                cuenta.text = str(item.get('cuenta_pasivo', ''))
                
                tipo_elem = etree.SubElement(registro, "TipoRetencion")
                tipo_elem.text = nombre_tipo
        
        # Guardar
        xml_str = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
        
        with open(file_path, 'wb') as f:
            f.write(xml_str)
        
        logger.info(f"📄 XML generado: {file_path}")
        return file_path
    
    def generar_xml_por_tipo(
        self,
        retenciones: List[Dict],
        periodo: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        Generar XML separados por tipo de retención
        
        Args:
            retenciones: Lista de retenciones procesadas
            periodo: Período (YYYY-MM)
        
        Returns:
            Dict con los paths de los archivos generados
        """
        if not retenciones:
            return {}
        
        # Agrupar por tipo
        retenciones_por_tipo = {}
        for r in retenciones:
            tipo = r.get('tipo_retencion', 'renta')
            if tipo not in retenciones_por_tipo:
                retenciones_por_tipo[tipo] = []
            retenciones_por_tipo[tipo].append(r)
        
        archivos_generados = {}
        
        for tipo, retenciones_tipo in retenciones_por_tipo.items():
            archivo = self.generar_xml_retenciones(
                retenciones=retenciones_tipo,
                periodo=periodo,
                tipo=tipo
            )
            archivos_generados[tipo] = archivo
        
        return archivos_generados