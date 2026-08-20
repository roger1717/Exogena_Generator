# Lógica de Retenciones y su Relación con la Información Exógena

Al estructurar un sistema contable moderno, entender cómo fluyen los datos desde la factura hasta la DIAN es fundamental. 

## 1. El Flujo de la Retención (El Origen)
La retención en la fuente nace en el momento de la **transacción**. Cuando una empresa realiza una compra o paga por un servicio, el motor contable debe evaluar:

*   **¿El servicio/compra supera la base legal en pesos (derivada de la UVT)?**
*   **¿A quién se le paga?** (Si es autorretenedor, la regla se rompe y no se retiene).
*   **¿Cuál es el porcentaje a aplicar?** (Dependiendo del concepto).

Este proceso genera un registro en el pasivo (Cuenta 2365), que representa un dinero que le debes a la DIAN, no a tu proveedor.

## 2. La Conexión con la Información Exógena (El Destino)
La Información Exógena (como el **Formato 1001 - Pagos o abonos en cuenta y retenciones**) no es más que una **agrupación anual** de estas transacciones. 

Si tu base de datos de retenciones está bien diseñada, extraer la exógena es una simple operación de agrupación y suma.

### ¿Cómo comparten las columnas?

| Dato en la base de Retenciones | Uso en el Formato 1001 (Exógena) |
| :--- | :--- |
| `NIT_Tercero` | Se usa directamente para cruzar a quién se le retuvo. |
| `Base_Gravable` | Se suma por tercero y se reporta en las columnas de **Valor acumulado del pago o abono en cuenta**. |
| `Valor_Retenido` | Se suma por tercero y se reporta como **Retención en la fuente practicada**. |
| `Concepto_Contable` | Se mapea. Tu sistema usa nombres como *'Honorarios'*. La DIAN exige códigos numéricos. Tu software debe tener una tabla de equivalencias que transforme *'Honorarios'* al código **5002**. |

## 3. Claves para el Diseño del Backend 
Para que el motor en Python procese esto eficientemente usando herramientas como Pandas:

1.  **Tablas Paramétricas:** No "quemes" las bases ni los porcentajes en el código. Crea una tabla en base de datos donde almacenes el valor de la UVT anual y los topes de retención en UVTs. Al cargar el dataframe de transacciones, cruza (merge) con esta tabla para saber si la base en pesos supera el tope.
2.  **Mapeo de Terceros:** La tabla de terceros debe tener un campo `es_autorretenedor (Booleano)`. Si es `True`, la función de cálculo de retención en Pandas debería retornar 0 automáticamente, independientemente del monto.
3.  **El poder del `groupby`:** Para pasar de las retenciones a la exógena, la magia ocurre con algo tan simple como:
    ```python
    # Ejemplo conceptual
    exogena_1001 = df_retenciones.groupby(['NIT_Tercero', 'Codigo_DIAN']).agg({
        'Base_Gravable': 'sum',
        'Valor_Retenido': 'sum'
    }).reset_index()
    ```

Entender esta arquitectura garantiza que no tengas que escribir un módulo separado para la exógena; simplemente, la exógena se vuelve un reporte que consume la tabla de retenciones.
