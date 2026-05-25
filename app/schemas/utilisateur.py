from pydantic import BaseModel, EmailStr
from typing import Optional


class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    mot_passe: str
    telephone: Optional[str] = None
    role_id: int
    actif: bool = True


class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    mot_passe: Optional[str] = None
    telephone: Optional[str] = None
    role_id: Optional[int] = None
    actif: Optional[bool] = None
