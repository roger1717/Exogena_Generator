Fecha: 2025-01-01
Cuenta: 236530 (PUC)
Nombre_Cuenta: Retención Arrendamientos 3.5%
NIT_Tercero: 800987654
Razon_Social: Insumos Industriales Ltda
Debito: 0
Credito: 1447771.55
Concepto: Registro contable de retencion arrendamientos...
¿Qué significa esto?

La empresa pagó $1,447,771.55 a Insumos Industriales Ltda (tercero)

Ese pago fue por "Retención Arrendamientos 3.5%" (el concepto)

El código contable de esa transacción es 236530 (el PUC)



______________________________________

Código PUC	Nombre de la Cuenta	¿Qué significa?
512010	Arrendamientos Bienes Inmuebles	Gastos de arriendo
511005	Honorarios Asesoría Jurídica	Pagos a abogados/consultores
413505	Venta de Mercancías / Productos	Ingresos por ventas
236530	Retención Arrendamientos 3.5%	Retención en la fuente
220505	Proveedores Nacionales	Compras a proveedores
421005	Ingresos Financieros Intereses	Intereses ganados
¿Para qué sirve el PUC?

Clasificar cada transacción (saber si es un gasto, ingreso, activo, pasivo)

Agrupar transacciones similares (todos los arriendos van a la misma cuenta)

Reportar a la DIAN usando códigos estandarizados


___________________________________________

3. El Problema del Contador: Informar a la DIAN
El contador NO puede enviar el archivo CSV tal cual a la DIAN. La DIAN exige que la información se reporte en formatos específicos (1001, 1007, 1008, 1009).

Cada formato tiene un propósito:

Formato	¿Qué reporta?	Ejemplo
1001	Pagos o abonos a terceros (gastos)	Arriendos, honorarios,servicios, compras
1007	Ingresos recibidos	Ventas, ingresos financieros
1008	Cuentas por cobrar	Lo que le deben a la empresa
1009	Cuentas por pagar	Lo que la empresa debe

_____________________________________________

4. El Mapeo PUC → Concepto Exógena
El contador debe mapear (traducir) cada PUC a un concepto de exógena de la DIAN.

Ejemplo de mapeo:

PUC	Concepto DIAN	Código DIAN
512010 (Arrendamientos)	Arrendamientos	5005
511005 (Honorarios)	Honorarios	5002
413505 (Ventas)	Ingresos Brutos	8001
236530 (Retención Arrendamientos)	Retenciones Arrendamientos	5025
220505 (Proveedores)	Cuentas por Pagar	9002

¿Por qué se hace esto? Porque la DIAN no entiende el PUC de la empresa, necesita su propio sistema de codificación.  


____________________________________________________

5. ¿Qué le interesa al contador?
El contador necesita:

Agrupar todas las transacciones por concepto de exógena (ej. todos los arriendos juntos, todos los honorarios juntos, etc.)

Sumar los valores de cada grupo

Generar un reporte que muestre:

Total de arriendos: $X

Total de honorarios: $Y

Total de ventas: $Z

Total de retenciones: $W

Presentar este reporte a la DIAN en el formato que ellos exigen (generalmente XML)