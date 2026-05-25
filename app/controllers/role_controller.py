from sqlalchemy.orm import Session
from app.models.role import Role


def get_all(db: Session):
    return db.query(Role).all()


def get_by_id(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()
