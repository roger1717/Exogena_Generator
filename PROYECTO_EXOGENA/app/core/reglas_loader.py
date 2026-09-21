# app/core/reglas_loader.py — carga los JSON

class ReglasLoader:
    def __init__(self, reglas_dir: Path = Path("data/reglas")):
        self.reglas_dir = reglas_dir
        self._cache = None

    def cargar_todas(self) -> List[Dict]:
        """Carga los 4 JSON y los valida."""
        archivos = ["renta.json", "iva.json", "ica.json", "exogena.json"]
        reglas = []
        for archivo in archivos:
            reglas.extend(self._cargar_archivo(self.reglas_dir / archivo))
        self._validar(reglas)
        return reglas

    def _cargar_archivo(self, path: Path) -> List[Dict]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("reglas", [])

    def _validar(self, reglas: List[Dict]) -> None:
        """Valida coherencia contable. Lanza excepción si hay errores."""
        validator = ReglasValidator()
        errores = validator.validar_todas(reglas)
        if errores:
            raise ValueError(f"Reglas inválidas:\n" + "\n".join(errores))