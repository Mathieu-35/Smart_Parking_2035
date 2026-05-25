from sqlalchemy import Column, Integer, String, CheckConstraint
from app.database import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint(
            "nom IN ('administrateur', 'gardien', 'conducteur')",
            name="check_role_nom"
        ),
    )
