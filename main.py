from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer

app = FastAPI()

#SqlAlchemy Setup
"""
# 1 Creates a SQLAlchemy database engine definition for SQLite.
# 2 Creates a blueprint for a SQLAlchemy session.
# 3 Defines a base model, which allows you to define Python objects as SQLAlchemy ORM objects.
# 4 Creates a method get_db which will be executed whenever you need access to the database.
#   This method instantiates a Session from the blueprint you defined earlier, 
#   and closes it when you are done with it so that you don’t have unused sessions laying around.
"""

SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# will be used to create models as Model in django.
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# models.py ===================
class DBPlace(Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    coffee = Column(Boolean)
    wifi = Column(Boolean)
    food = Column(Boolean)
    lat = Column(Float)
    lng = Column(Float)

Base.metadata.create_all(bind=engine)

class Place(BaseModel):
    name: str
    description: Optional[str] = None
    coffee: bool
    wifi: bool
    food: bool
    lat: float
    lng: float

    class Config:
        orm_mode = True

# methods like from manager
def get_place(db: Session, place_id: int):
    return db.query(DBPlace).where(DBPlace.id == place_id).first()

def get_places(db: Session):
    return db.query(DBPlace).all()

def create_place(db: Session, place: Place):
    db_place = DBPlace(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)

    return db_place

# views.py =========================


@app.post('/places/', response_model=Place)
def create_places_view(place: Place, db: Session = Depends(get_db)):
    db_place = create_place(db, place)
    return db_place

@app.get('/places/', response_model=List[Place])
def get_places_view(db: Session = Depends(get_db)):
    return get_places(db)

@app.get('/place/{place_id}')
def get_place_view(place_id: int, db: Session = Depends(get_db)):
    return get_place(db, place_id)

@app.get('/')
async def root():
    return {'message': 'Hello World!'}