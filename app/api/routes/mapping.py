# ============================================================================
# API/ROUTES/MAPPING.PY
# OBJETIVO: Definir los endpoints de la API para gestionar las reglas de mapeo.
#           Implementa el CRUD completo (Crear, Leer, Actualizar, Eliminar) 
#           para las reglas PUC → Concepto Exógena usando FastAPI y SQLAlchemy.
# ============================================================================

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.mapping_rule import MappingRule
from app.schemas.mapping import (
    MappingRuleCreate, 
    MappingRuleUpdate, 
    MappingRuleResponse
)

# Crear el router para agrupar endpoints relacionados con mapeo
router = APIRouter(prefix="/mapping", tags=["Reglas de Mapeo"])

@router.get("/", response_model=List[MappingRuleResponse])
def get_all_rules(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Obtener todas las reglas de mapeo con paginación.
    
    Args:
        skip: Número de registros a saltar (para paginación)
        limit: Número máximo de registros a retornar
        db: Sesión de base de datos (inyectada automáticamente)
    
    Returns:
        Lista de reglas de mapeo
    """
    rules = db.query(MappingRule).offset(skip).limit(limit).all()
    return rules

@router.get("/{rule_id}", response_model=MappingRuleResponse)
def get_rule_by_id(
    rule_id: int, 
    db: Session = Depends(get_db)
):
    """
    Obtener una regla de mapeo específica por su ID.
    
    Args:
        rule_id: ID de la regla a buscar
        db: Sesión de base de datos
    
    Returns:
        La regla encontrada
    
    Raises:
        HTTPException 404: Si no se encuentra la regla
    """
    rule = db.query(MappingRule).filter(MappingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regla de mapeo no encontrada"
        )
    return rule

@router.post("/", response_model=MappingRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_data: MappingRuleCreate, 
    db: Session = Depends(get_db)
):
    """
    Crear una nueva regla de mapeo.
    
    Args:
        rule_data: Datos de la nueva regla (validados por Pydantic)
        db: Sesión de base de datos
    
    Returns:
        La regla creada
    
    Raises:
        HTTPException 400: Si ya existe una regla con el mismo PUC
    """
    # Verificar si ya existe una regla con ese PUC
    existing_rule = db.query(MappingRule).filter(
        MappingRule.puc_code == rule_data.puc_code
    ).first()
    
    if existing_rule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una regla para el PUC {rule_data.puc_code}"
        )
    
    # Crear la nueva regla
    new_rule = MappingRule(
        puc_code=rule_data.puc_code,
        puc_name=rule_data.puc_name,
        exogena_format=rule_data.exogena_format,
        exogena_concept=rule_data.exogena_concept,
        exogena_concept_name=rule_data.exogena_concept_name
    )
    
    # Guardar en la base de datos
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)  # Recargar para obtener el ID generado
    
    return new_rule

@router.put("/{rule_id}", response_model=MappingRuleResponse)
def update_rule(
    rule_id: int, 
    rule_data: MappingRuleUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualizar una regla de mapeo existente.
    
    Args:
        rule_id: ID de la regla a actualizar
        rule_data: Nuevos datos para la regla
        db: Sesión de base de datos
    
    Returns:
        La regla actualizada
    
    Raises:
        HTTPException 404: Si no se encuentra la regla
    """
    # Buscar la regla existente
    rule = db.query(MappingRule).filter(MappingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regla de mapeo no encontrada"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = rule_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    # Guardar cambios
    db.commit()
    db.refresh(rule)
    
    return rule

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int, 
    db: Session = Depends(get_db)
):
    """
    Eliminar una regla de mapeo.
    
    Args:
        rule_id: ID de la regla a eliminar
        db: Sesión de base de datos
    
    Raises:
        HTTPException 404: Si no se encuentra la regla
    """
    rule = db.query(MappingRule).filter(MappingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regla de mapeo no encontrada"
        )
    
    db.delete(rule)
    db.commit()