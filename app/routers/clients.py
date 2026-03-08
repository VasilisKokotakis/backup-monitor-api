from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientOut


router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
def list_clients(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Client]:
    return db.query(Client).order_by(Client.created_at.desc()).all()


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Client:
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Client:
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client
