import pandas as pd

class RetencionesEngine:
    def __init__(self, uvt_actual: float):
        self.uvt_actual = uvt_actual
        # Matriz paramétrica (idealmente vendría de una base de datos)
        # Concepto: [Tarifa, Tope en UVT]
        self.matriz_reglas = {
            "Compras Generales": {"tarifa": 0.025, "tope_uvt": 27},
            "Servicios Generales": {"tarifa": 0.04, "tope_uvt": 4},
            "Honorarios": {"tarifa": 0.11, "tope_uvt": 0},
            "Arrendamientos": {"tarifa": 0.035, "tope_uvt": 0}
        }

    def calcular(self, df_transacciones: pd.DataFrame) -> pd.DataFrame:
        """
        Evalúa cada transacción y calcula la retención si supera el tope legal.
        """
        # Crear columnas de salida
        df_transacciones['Valor_Retenido'] = 0.0
        df_transacciones['Aplica_Retencion'] = False

        for index, row in df_transacciones.iterrows():
            concepto = row.get('Concepto_Contable', '')
            base = row.get('Base_Gravable', 0.0)
            
            # 1. Validar si el concepto existe en la matriz
            if concepto in self.matriz_reglas:
                regla = self.matriz_reglas[concepto]
                tope_pesos = regla['tope_uvt'] * self.uvt_actual
                
                # 2. Evaluar si la base supera el tope legal
                if base >= tope_pesos:
                    # 3. Validar perfil tributario (ej. no retener a autorretenedores)
                    if row.get('Perfil_Tributario') != "Autorretenedor":
                        df_transacciones.at[index, 'Valor_Retenido'] = base * regla['tarifa']
                        df_transacciones.at[index, 'Aplica_Retencion'] = True

        return df_transacciones