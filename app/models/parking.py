from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Parking(Base):
    __tablename__ = "parking"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    nom = Column(String(150), nullable=False, unique=True)
    adresse = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Géolocalisation
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Capacité
    nombre_places_total = Column(Integer, nullable=False)
    places_disponibles = Column(Integer, nullable=False)
    
    # Tarification variable (JSON pour flexibilité)
    # Format: {"lundi": 2.5, "mardi": 2.5, ..., "dimanche": 1.5}
    tarification_par_jour = Column(JSON, nullable=False, default={
        "lundi": 2.0,
        "mardi": 2.0,
        "mercredi": 2.0,
        "jeudi": 2.0,
        "vendredi": 2.5,
        "samedi": 3.0,
        "dimanche": 1.5
    })
    
    # Horaires d'ouverture (JSON)
    # Format: {"lundi": {"ouverture": "06:00", "fermeture": "23:00"}, ...}
    horaires = Column(JSON, nullable=False, default={
        "lundi": {"ouverture": "06:00", "fermeture": "23:00"},
        "mardi": {"ouverture": "06:00", "fermeture": "23:00"},
        "mercredi": {"ouverture": "06:00", "fermeture": "23:00"},
        "jeudi": {"ouverture": "06:00", "fermeture": "23:00"},
        "vendredi": {"ouverture": "06:00", "fermeture": "23:00"},
        "samedi": {"ouverture": "08:00", "fermeture": "22:00"},
        "dimanche": {"ouverture": "08:00", "fermeture": "22:00"}
    })
    
    # Statuts
    actif = Column(Boolean, default=True)
    supprime = Column(Boolean, default=False)  # Soft delete
    
    # Timestamps
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    historiques = relationship("HistoriquePlaces", back_populates="parking", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="parking", cascade="all, delete-orphan")


class HistoriquePlaces(Base):
    __tablename__ = "historique_places"

    id = Column(Integer, primary_key=True, index=True)
    parking_id = Column(Integer, ForeignKey("parking.id"), nullable=False)
    
    places_disponibles = Column(Integer, nullable=False)
    places_occupees = Column(Integer, nullable=False)
    
    # Raison du changement
    raison = Column(String(255), nullable=True)  # "reservation", "liberation", "maintenance"
    
    date_enregistrement = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    parking = relationship("Parking", back_populates="historiques")


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, index=True)
    parking_id = Column(Integer, ForeignKey("parking.id"), nullable=False)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    
    # Informations de réservation
    plaque_immatriculation = Column(String(20), nullable=True)
    date_arrivee = Column(DateTime, nullable=False)
    date_depart = Column(DateTime, nullable=False)
    
    # Statut
    statut = Column(String(50), default="confirmee")  # "confirmee", "arrivee", "partie", "annulee"
    cout_total = Column(Float, nullable=True)

    # Code secret unique de la reservation, encode dans le QR code.
    # Le gardien le lit pour retrouver la reservation a l'entree/sortie.
    code_qr = Column(String(40), nullable=True, unique=True)

    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    parking = relationship("Parking", back_populates="reservations")
