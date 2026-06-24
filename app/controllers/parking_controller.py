from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models import Parking, HistoriquePlaces
from app.schemas.parking import ParkingCreate, ParkingUpdate

# Valeurs par défaut (tarifs en ARIARY par heure)
DEFAULT_TARIFICATION = {
    "lundi": 2000,
    "mardi": 2000,
    "mercredi": 2000,
    "jeudi": 2000,
    "vendredi": 2500,
    "samedi": 3000,
    "dimanche": 1500
}

DEFAULT_HORAIRES = {
    "lundi": {"ouverture": "06:00", "fermeture": "23:00"},
    "mardi": {"ouverture": "06:00", "fermeture": "23:00"},
    "mercredi": {"ouverture": "06:00", "fermeture": "23:00"},
    "jeudi": {"ouverture": "06:00", "fermeture": "23:00"},
    "vendredi": {"ouverture": "06:00", "fermeture": "23:00"},
    "samedi": {"ouverture": "08:00", "fermeture": "22:00"},
    "dimanche": {"ouverture": "08:00", "fermeture": "22:00"}
}


class ParkingController:
    
    @staticmethod
    def creer_parking(db: Session, parking_data: ParkingCreate) -> Parking:
        """Créer un nouveau parking"""

        # Les horaires : Pydantic a transforme chaque horaire en OBJET
        # HoraireSchema. La base stocke du JSON (texte), donc on reconvertit
        # ces objets en simples dictionnaires avant de les enregistrer.
        horaires = parking_data.horaires or DEFAULT_HORAIRES
        if horaires:
            horaires = {
                jour: (valeur.model_dump() if hasattr(valeur, "model_dump") else valeur)
                for jour, valeur in horaires.items()
            }

        parking = Parking(
            nom=parking_data.nom,
            adresse=parking_data.adresse,
            description=parking_data.description,
            latitude=parking_data.latitude,
            longitude=parking_data.longitude,
            nombre_places_total=parking_data.nombre_places_total,
            places_disponibles=parking_data.places_disponibles,
            tarification_par_jour=parking_data.tarification_par_jour or DEFAULT_TARIFICATION,
            horaires=horaires
        )
        db.add(parking)
        db.commit()
        db.refresh(parking)
        
        # Enregistrer dans l'historique
        ParkingController._enregistrer_historique(
            db,
            parking.id,
            parking.places_disponibles,
            parking.nombre_places_total - parking.places_disponibles,
            "creation"
        )
        
        return parking
    
    @staticmethod
    def lister_parkings(db: Session, skip: int = 0, limit: int = 100, inclure_supprimes: bool = False) -> list[Parking]:
        """Lister tous les parkings"""
        query = db.query(Parking)
        
        if not inclure_supprimes:
            query = query.filter(Parking.supprime == False)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def obtenir_parking(db: Session, parking_id: int) -> Parking | None:
        """Obtenir un parking par son ID"""
        return db.query(Parking).filter(
            and_(
                Parking.id == parking_id,
                Parking.supprime == False
            )
        ).first()
    
    @staticmethod
    def modifier_parking(db: Session, parking_id: int, parking_data: ParkingUpdate) -> Parking | None:
        """Modifier un parking"""
        parking = ParkingController.obtenir_parking(db, parking_id)
        if not parking:
            return None
        
        # Mettre à jour les champs fournis
        update_data = parking_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(parking, field, value)
        
        parking.date_modification = datetime.utcnow()
        db.commit()
        db.refresh(parking)
        
        return parking
    
    @staticmethod
    def mettre_a_jour_places(db: Session, parking_id: int, nouvelles_places: int, raison: str = "manuel") -> Parking | None:
        """Mettre à jour le nombre de places disponibles et enregistrer dans l'historique"""
        parking = ParkingController.obtenir_parking(db, parking_id)
        if not parking:
            return None
        
        parking.places_disponibles = nouvelles_places
        parking.date_modification = datetime.utcnow()
        db.commit()
        db.refresh(parking)
        
        # Enregistrer dans l'historique
        places_occupees = parking.nombre_places_total - nouvelles_places
        ParkingController._enregistrer_historique(
            db,
            parking_id,
            nouvelles_places,
            places_occupees,
            raison
        )
        
        return parking
    
    @staticmethod
    def supprimer_parking(db: Session, parking_id: int, soft_delete: bool = True) -> bool:
        """Supprimer un parking (soft delete par défaut)"""
        parking = db.query(Parking).filter(Parking.id == parking_id).first()
        if not parking:
            return False
        
        if soft_delete:
            parking.supprime = True
            parking.actif = False
            parking.date_modification = datetime.utcnow()
            db.commit()
        else:
            db.delete(parking)
            db.commit()
        
        return True
    
    @staticmethod
    def desactiver_parking(db: Session, parking_id: int) -> Parking | None:
        """Désactiver un parking (le rendre temporairement indisponible)"""
        parking = ParkingController.obtenir_parking(db, parking_id)
        if not parking:
            return None
        
        parking.actif = False
        parking.date_modification = datetime.utcnow()
        db.commit()
        db.refresh(parking)
        
        return parking
    
    @staticmethod
    def activer_parking(db: Session, parking_id: int) -> Parking | None:
        """Activer un parking"""
        parking = db.query(Parking).filter(Parking.id == parking_id).first()
        if not parking or parking.supprime:
            return None
        
        parking.actif = True
        parking.date_modification = datetime.utcnow()
        db.commit()
        db.refresh(parking)
        
        return parking
    
    @staticmethod
    def _enregistrer_historique(
        db: Session,
        parking_id: int,
        places_disponibles: int,
        places_occupees: int,
        raison: str
    ) -> HistoriquePlaces:
        """Enregistrer un événement dans l'historique des places"""
        historique = HistoriquePlaces(
            parking_id=parking_id,
            places_disponibles=places_disponibles,
            places_occupees=places_occupees,
            raison=raison
        )
        db.add(historique)
        db.commit()
        db.refresh(historique)
        
        return historique
    
    @staticmethod
    def obtenir_historique(db: Session, parking_id: int, limit: int = 50) -> list[HistoriquePlaces]:
        """Obtenir l'historique des places pour un parking"""
        return db.query(HistoriquePlaces).filter(
            HistoriquePlaces.parking_id == parking_id
        ).order_by(HistoriquePlaces.date_enregistrement.desc()).limit(limit).all()
    
    @staticmethod
    def obtenir_taux_occupation(db: Session, parking_id: int) -> dict | None:
        """Obtenir le taux d'occupation actuel d'un parking"""
        parking = ParkingController.obtenir_parking(db, parking_id)
        if not parking:
            return None
        
        occupation = parking.nombre_places_total - parking.places_disponibles
        taux = (occupation / parking.nombre_places_total * 100) if parking.nombre_places_total > 0 else 0
        
        return {
            "parking_id": parking_id,
            "places_disponibles": parking.places_disponibles,
            "places_occupees": occupation,
            "places_totales": parking.nombre_places_total,
            "taux_occupation": round(taux, 2)
        }
