from lxml import etree

def generate_xml(data: list, format_code: str):
    # Crear el elemento raíz. La estructura exacta depende del XSD de la DIAN.
    root = etree.Element("InformacionExogena")
    # ... (Añadir metadatos como versión, año, etc.)

    for item in data:
        registro = etree.SubElement(root, "Registro")
        # Crear los elementos hijos según el formato
        nit = etree.SubElement(registro, "Nit")
        nit.text = item.get("nit")
        # ... etc.s

    # Convertir el árbol a un string XML bien formateado
    xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    return xml_str