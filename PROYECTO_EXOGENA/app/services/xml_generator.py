#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de archivos XML para Retenciones y Exógena

Autor: [Tu nombre]
Fecha: 2026-08-21
Versión: 1.0.0
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from lxml import etree


class XMLGenerator:
    """
    Generador de archivos XML para retenciones y exógena
    """
    
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
        periodo: Optional[str] = None
    ) -> Path:
        """
        Generar XML de retenciones (Formato 1003)
        
        Args:
            retenciones: Lista de retenciones procesadas
            periodo: Período (opcional)
        
        Returns:
            Path del archivo generado
        """
        if not retenciones:
            raise ValueError("No hay retenciones para generar")
        
        # Crear nombre del archivo
        fecha = datetime.now().strftime("%Y%m%d")
        periodo_str = f"_{periodo}" if periodo else ""
        filename = f"{fecha}_ReteFuente{periodo_str}.xml"
        file_path = self.output_dir / filename
        
        # Crear estructura XML
        root = etree.Element("InformacionExogena")
        etree.SubElement(root, "Version").text = "1.0"
        etree.SubElement(root, "Año").text = periodo[:4] if periodo else "2025"
        etree.SubElement(root, "Periodo").text = periodo[5:] if periodo else "01"
        etree.SubElement(root, "Tipo").text = "1003"
        etree.SubElement(root, "FechaGeneracion").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Detalle de retenciones
        detalle = etree.SubElement(root, "Detalle")
        
        for item in retenciones:
            if item.get('valor_retenido', 0) > 0:
                registro = etree.SubElement(detalle, "Registro")
                
                # Campos del registro
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
                
                comprobante = etree.SubElement(registro, "Comprobante")
                comprobante.text = str(item.get('comprobante', ''))
        
        # Guardar XML
        xml_str = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
        
        with open(file_path, 'wb') as f:
            f.write(xml_str)
        
        return file_path
    
    def generar_xml_exogena(
        self,
        datos: List[Dict],
        formato: str = "1001",
        periodo: Optional[str] = None
    ) -> Path:
        """
        Generar XML de exógena
        
        Args:
            datos: Lista de datos procesados
            formato: Formato DIAN (1001, 1007, 1008, 1009)
            periodo: Período (opcional)
        
        Returns:
            Path del archivo generado
        """
        if not datos:
            raise ValueError("No hay datos para generar")
        
        fecha = datetime.now().strftime("%Y%m%d")
        periodo_str = f"_{periodo}" if periodo else ""
        filename = f"{fecha}_Exogena_{formato}{periodo_str}.xml"
        file_path = self.output_dir / filename
        
        # Crear estructura XML
        root = etree.Element("InformacionExogena")
        etree.SubElement(root, "Version").text = "1.0"
        etree.SubElement(root, "Año").text = periodo[:4] if periodo else "2025"
        etree.SubElement(root, "Periodo").text = periodo[5:] if periodo else "01"
        etree.SubElement(root, "Formato").text = formato
        etree.SubElement(root, "FechaGeneracion").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Detalle
        detalle = etree.SubElement(root, "Detalle")
        
        for item in datos:
            registro = etree.SubElement(detalle, "Registro")
            
            nit = etree.SubElement(registro, "NitTercero")
            nit.text = str(item.get('nit_tercero', ''))
            
            nombre = etree.SubElement(registro, "NombreTercero")
            nombre.text = str(item.get('nombre_tercero', ''))
            
            valor = etree.SubElement(registro, "Valor")
            valor.text = f"{item.get('valor', 0):.2f}"
            
            puc = etree.SubElement(registro, "CodigoPUC")
            puc.text = str(item.get('codigo_puc', ''))
            
            concepto = etree.SubElement(registro, "Concepto")
            concepto.text = str(item.get('concepto_asignado', ''))
            
            if item.get('formato_asignado'):
                fmt = etree.SubElement(registro, "Formato")
                fmt.text = str(item.get('formato_asignado', ''))
        
        # Guardar
        xml_str = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
        
        with open(file_path, 'wb') as f:
            f.write(xml_str)
        
        return file_path