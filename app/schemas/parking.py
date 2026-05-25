from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class HoraireSchema(BaseModel):
    ouverture: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    fermeture: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class ParkingBase(BaseModel):
    nom: str = Field(..., min_length=3, max_length=150)
    adresse: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    nombre_places_total: int = Field(..., gt=0)
    places_disponibles: int = Field(..., ge=0)
    tarification_par_jour: Optional[Dict[str, float]] = None
    horaires: Optional[Dict[str, HoraireSchema]] = None


class ParkingCreate(ParkingBase):
    pass


class ParkingUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=3, max_length=150)
    adresse: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    nombre_places_total: Optional[int] = Field(None, gt=0)
    places_disponibles: Optional[int] = Field(None, ge=0)
    tarification_par_jour: Optional[Dict[str, float]] = None
    horaires: Optional[Dict[str, HoraireSchema]] = None
    actif: Optional[bool] = None


class HistoriquePlacesRead(BaseModel):
    id: int
    parking_id: int
    places_disponibles: int
    places_occupees: int
    raison: Optional[str]
    date_enregistrement: datetime

    class Config:
        from_attributes = True


class ParkingRead(ParkingBase):
    id: int
    actif: bool
    supprime: bool
    date_creation: datetime
    date_modification: datetime
    historiques: list[HistoriquePlacesRead] = []

    class Config:
        from_attributes = True


class ParkingDetail(ParkingRead):
    pass


class ParkingListItem(BaseModel):
    id: int
    nom: str
    nombre_places_total: int
    places_disponibles: int
    actif: bool
    date_modification: datetime

    class Config:
        from_attributes = True
