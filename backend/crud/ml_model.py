from sqlalchemy.orm import Session
from models.ml_model import MLModel
from schemas.ml_model import MLModelCreate

def get_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MLModel).order_by(MLModel.upload_date.desc()).offset(skip).limit(limit).all()

def get_active_model(db: Session):
    return db.query(MLModel).filter(MLModel.is_active == True).first()

def create_model_record(db: Session, model_create: MLModelCreate):
    # Se o novo for ativo, desativa todos os outros
    if model_create.is_active:
        db.query(MLModel).update({MLModel.is_active: False})
        
    db_model = MLModel(
        filename=model_create.filename,
        description=model_create.description,
        framework=model_create.framework,
        is_active=model_create.is_active
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def set_model_active(db: Session, model_id: int):
    # Desativa todos
    db.query(MLModel).update({MLModel.is_active: False})
    
    # Ativa o solicitado
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if model:
        model.is_active = True
        db.commit()
        db.refresh(model)
        
    return model
