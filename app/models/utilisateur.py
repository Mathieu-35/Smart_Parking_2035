from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    mot_passe = Column(String(255), nullable=False)
    telephone = Column(String(20), nullable=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    actif = Column(Boolean, default=True)

    # Le parking dont ce gardien est responsable (vide pour les autres roles).
    # Plusieurs gardiens peuvent pointer vers le meme parking (equipes/rotations).
    parking_id = Column(Integer, ForeignKey("parking.id"), nullable=True)

    role = relationship("Role", backref="utilisateurs")
    parking = relationship("Parking", backref="gardiens")
