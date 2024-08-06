from fastapi.testclient import TestClient
from fastapi_simple_security import api_key_router, api_key_security
from os import path
from typing import Optional
from sqlalchemy.orm import Session
from database import engine, Sessionlocal
import models
from uuid import UUID
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
load_dotenv()  # before simple_security to prevent empty DB
# Also loads some default values for environment variables at startup

# Tags add descriptive text per section
tags_metadata = [
    {
        "name": "_auth",
        "description": "Security related functions for secret-key and api-key.",
    },
    {
        "name": "default",
        "description": "These are the default CRUD endpoints.",
    },
]

# Create the application (Controller Layer)
app = FastAPI(
    title=path.splitext(path.basename(__file__))[0],
    summary="This is an example of an api in python using FastAPI and SQLAlchemy",
    version="0.0.2",
    openapi_tags=tags_metadata
)

# Add models (Model Layer)
models.Base.metadata.create_all(bind=engine)

# Add DB layer/function


def get_db():
    try:
        db = Sessionlocal()
        yield db
    finally:
        db.close()


class PersonCreate(BaseModel):
    name: str
    age: int
    comment: Optional[str] = None


PEOPLE = []

# Add the api_key router which provides the auth functinos
app.include_router(api_key_router, prefix="/auth", tags=["_auth"])

# add root endpoint (unsecured)


@app.get("/", tags=["default"])
def welcome_page():
    return "Welcome to the People API!"


# add a secure endpoint (secured)
@app.get("/secure", dependencies=[Depends(api_key_security)], tags=["default"])
async def secure_endpoint():
    return {"message": "This is a secure endpoint"}

# add an endpoint to list people on table (unsecured)


@app.get("/people", tags=["default"])
def get_all_people(db: Session = Depends(get_db)):
    return db.query(models.Person).all()

# add an endpoint to list a person (unsecured)


@app.get("/person/{person_id}", tags=["default"])
def get_person_by_id(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter_by(id=person_id).first()
    if person:
        return dict(person.__dict__)
    raise HTTPException(status_code=404, detail="Person " +
                        person.name+" not found")

# add a person endpoint (secured)


@app.post("/new", dependencies=[Depends(api_key_security)], tags=["default"])
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    person_model = models.Person()
    person_model.name = person.name
    person_model.age = person.age
    person_model.comment = person.comment
    db.add(person_model)
    db.commit()
    return {"message": "Person "+person.name+" created"}

# update a person endpoint (secured)


@app.put("/update/{person_id}", dependencies=[Depends(api_key_security)], tags=["default"])
def update_person(person_id: int, person: PersonCreate, db: Session = Depends(get_db)):
    existing_person = db.query(models.Person).filter(
        models.Person.id == person_id).first()
    if not existing_person:
        raise HTTPException(status_code=404, detail="Person not found")
    existing_person.name = person.name
    existing_person.age = person.age
    existing_person.comment = person.comment
    db.add(existing_person)
    db.commit()
    return {"message": "Person "+person.name+" updated"}

# delete a person endpoint (secured)


@app.delete("/remove/{person_id}", dependencies=[Depends(api_key_security)], tags=["default"])
def delete_person(person_id: int, db: Session = Depends(get_db)):
    existing_person = db.query(models.Person).filter(
        models.Person.id == person_id).first()
    if not existing_person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.query(models.Person).filter(models.Person.id == person_id).delete()
    db.commit()
    return {"message": "Person "+existing_person.name+" deleted"}


# ---------Main---------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)


# uvicorn main:app --reload --port=8080
