# app/services/reglas_service.py
class ReglasService:
    def __init__(self, db: Session, reglas_dir: Path = Path("data/reglas")):
        self.db = db
        self.loader = ReglasLoader(reglas_dir)

    def recargar_desde_json(self) -> Dict[str, int]:
        """
        
        Carga los 4 JSON a la BD con UPSERT.
        Retorna {creadas, actualizadas, sin_cambios}.
        """
        reglas = self.loader.cargar_todas()  # ya validadas
        creadas = actualizadas = sin_cambios = 0

        for r in reglas:
            puc = r["puc_code"]
            existente = self.db.query(MappingRule).filter_by(puc_code=puc).first()
            campos = self._mapear_campos(r)

            if existente:
                if self._hay_cambios(existente, campos):
                    for k, v in campos.items():
                        setattr(existente, k, v)
                    actualizadas += 1
                else:
                    sin_cambios += 1
            else:
                self.db.add(MappingRule(puc_code=puc, **campos))
                creadas += 1

        self.db.commit()
        return {"creadas": creadas, "actualizadas": actualizadas, "sin_cambios": sin_cambios}