# app/api/routes/admin.py
@router.post("/reglas/recargar")
async def recargar_reglas(
    db: Session = Depends(get_db),
    _: str = Depends(verificar_admin),  # ← auth obligatoria
):
    service = ReglasService(db)
    resultado = service.recargar_desde_json()
    return {"status": "ok", **resultado}