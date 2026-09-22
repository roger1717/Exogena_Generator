from pathlib import Path
from app.core.database import SessionLocal
from app.services.retencion_csv_processor import RetencionCSVProcessor

db = SessionLocal()
p = RetencionCSVProcessor(db)
rets, _ = p.procesar_archivo(Path("data/fixtures/auxiliar_contable_sintetico.csv"))

for r in rets[:10]:
    print(f"{r['comprobante']} | {r['cuenta_pasivo']} | {r['tipo_retencion']:5s} | "
          f"base={r['base_gravable']:>12,.0f} | tarifa={r['tarifa']:.4f} | "
          f"ret={r['valor_retenido']:>10,.0f}")