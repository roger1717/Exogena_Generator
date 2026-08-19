/Retenciones/
├── /src/
│   ├── /__init__.py
│   │
│   ├── /domain/                      # Capa de dominio - Entidades y reglas de negocio PURAS
│   │   ├── /__init__.py
│   │   ├── /entities/                # Objetos de negocio (POJOs - Plain Python Objects)
│   │   │   ├── /__init__.py
│   │   │   ├── retencion.py         # Entidad Retención (atributos, validaciones)
│   │   │   ├── concepto_retencion.py # Entidad Concepto (tarifas, códigos DIAN)
│   │   │   └── proveedor.py         # Entidad Proveedor (NIT, nombre, régimen)
│   │   ├── /value_objects/           # Objetos inmutables con validación propia
│   │   │   ├── /__init__.py
│   │   │   ├── nit.py               # Validación específica de NIT colombiano
│   │   │   ├── monto.py             # Manejo de montos (decimales, redondeo)
│   │   │   └── periodo.py           # Periodos tributarios (año-mes)
│   │   └── /enums/                   # Enumeraciones (valores fijos del negocio)
│   │       ├── /__init__.py
│   │       ├── tipo_retencion.py    # Renta, IVA, ICA, etc.
│   │       ├── regimen_proveedor.py  # Simplificado, Común, Gran contribuyente
│   │       └── estado_retencion.py   # Calculada, Reportada, Pagada
│   │
│   ├── /application/                 # Capa de aplicación - Casos de uso (ORQUESTACIÓN)
│   │   ├── /__init__.py
│   │   ├── /services/                # Servicios que implementan la lógica de negocio
│   │   │   ├── /__init__.py
│   │   │   ├── calculo_retencion_service.py    # Algoritmo de cálculo de retención
│   │   │   ├── generador_reporte_service.py    # Generación de archivos DIAN
│   │   │   ├── validador_retencion_service.py  # Validaciones (topes, aplicabilidad)
│   │   │   └── importador_facturas_service.py  # Importar facturas desde CSV/Excel
│   │   ├── /dto/                     # Data Transfer Objects (para entrada/salida de API)
│   │   │   ├── /__init__.py
│   │   │   ├── retencion_dto.py     # DTO para crear/actualizar retenciones
│   │   │   ├── factura_dto.py       # DTO para importar facturas
│   │   │   └── reporte_dto.py       # DTO para generar reportes
│   │   └── /interfaces/              # Interfaces/Contratos (para inyección de dependencias)
│   │       ├── /__init__.py
│   │       ├── i_retencion_repository.py    # Contrato para repositorio
│   │       └── i_concepto_repository.py     # Contrato para repositorio de conceptos
│   │
│   ├── /infrastructure/              # Capa de infraestructura - Implementaciones concretas
│   │   ├── /__init__.py
│   │   ├── /repositories/            # Implementación de acceso a datos
│   │   │   ├── /__init__.py
│   │   │   ├── retencion_repository.py       # SQLAlchemy/PostgreSQL implementación
│   │   │   ├── concepto_repository.py        # Implementación para conceptos
│   │   │   └── proveedor_repository.py       # Implementación para proveedores
│   │   ├── /database/                # Configuración de base de datos
│   │   │   ├── /__init__.py
│   │   │   ├── connection.py         # Conexión a PostgreSQL/SQLite
│   │   │   └── models.py            # Modelos SQLAlchemy (mapeo ORM)
│   │   ├── /external/                # Integraciones externas
│   │   │   ├── /__init__.py
│   │   │   ├── dian_formatter.py    # Formateo según especificaciones DIAN
│   │   │   └── excel_generator.py   # Generación de Excel para el contador
│   │   └── /mappers/                 # Convertir entre entidades y modelos DB
│   │       ├── /__init__.py
│   │       ├── retencion_mapper.py   # Entidad <-> Modelo SQLAlchemy
│   │       └── concepto_mapper.py    # Entidad <-> Modelo SQLAlchemy
│   │
│   ├── /api/                         # Capa de presentación - API REST
│   │   ├── /__init__.py
│   │   ├── /routers/                 # Definición de rutas (FastAPI/Flask)
│   │   │   ├── /__init__.py
│   │   │   ├── retencion_router.py   # Endpoints para retenciones
│   │   │   ├── concepto_router.py    # Endpoints para conceptos
│   │   │   └── reporte_router.py     # Endpoints para generación de reportes
│   │   ├── /middleware/              # Middlewares (autenticación, logging)
│   │   │   ├── /__init__.py
│   │   │   ├── auth.py               # Validación de JWT/token
│   │   │   └── logging.py            # Logging de peticiones
│   │   └── /schemas/                 # Schemas Pydantic (validación de entrada/salida)
│   │       ├── /__init__.py
│   │       ├── retencion_schema.py   # Validación de retenciones
│   │       └── concepto_schema.py    # Validación de conceptos
│   │
│   ├── /core/                        # Configuración y utilidades compartidas
│   │   ├── /__init__.py
│   │   ├── config.py                 # Configuración (variables de entorno)
│   │   ├── constants.py              # Constantes de negocio (tarifas DIAN)
│   │   ├── exceptions.py             # Excepciones personalizadas
│   │   └── logger.py                 # Configuración de logging
│   │
│   └── /utils/                       # Utilidades generales
│       ├── /__init__.py
│       ├── file_handler.py           # Manejo de archivos (CSV, Excel, TXT)
│       ├── date_utils.py            # Utilidades de fechas (periodos tributarios)
│       ├── validators.py            # Validadores comunes (NIT, teléfono, email)
│       └── decimal_utils.py         # Manejo de decimales (redondeo contable)
│
├── /tests/                           # Pruebas
│   ├── /__init__.py
│   ├── /unit/                        # Pruebas unitarias
│   │   ├── /__init__.py
│   │   ├── test_calculo_retencion.py # Pruebas de lógica de cálculo
│   │   └── test_validators.py       # Pruebas de validadores
│   ├── /integration/                 # Pruebas de integración
│   │   ├── /__init__.py
│   │   ├── test_api_retenciones.py   # Pruebas de endpoints
│   │   └── test_repository.py       # Pruebas de repositorios
│   └── /fixtures/                    # Datos de prueba
│       ├── /__init__.py
│       ├── conceptos_retencion.json  # Datos de conceptos DIAN
│       ├── proveedores.json          # Datos de proveedores sintéticos
│       └── facturas.csv              # Facturas de prueba
│
├── /scripts/                         # Scripts utilitarios
│   ├── /__init__.py
│   ├── seed_data.py                 # Poblar base de datos con datos iniciales
│   ├── generate_synthetic_data.py   # Generar datos sintéticos para pruebas
│   └── migrate_db.py                # Scripts de migración de BD
│
├── /docs/                            # Documentación
│   ├── manual_usuario.md
│   ├── arquitectura.md
│   ├── dian_especificaciones.md     # Especificaciones técnicas DIAN
│   └── conceptos_retencion.md       # Lista de conceptos con tarifas
│
├── /data/                            # Archivos de datos (input/output)
│   ├── /input/                       # Archivos cargados por el usuario
│   │   └── facturas_ejemplo.csv
│   └── /output/                      # Archivos generados por el sistema
│       └── reporte_retenciones.txt   # Archivo para DIAN
│
├── requirements.txt                  # Dependencias del proyecto
├── .env.example                     # Variables de entorno de ejemplo
├── .gitignore                       # Archivos ignorados por Git
├── pyproject.toml                   # Configuración del proyecto (Poetry)
├── docker-compose.yml              # Configuración de Docker
├── Dockerfile                       # Docker para el proyecto
├── main.py                          # Punto de entrada de la aplicación
└── README.md                        # Documentación principal