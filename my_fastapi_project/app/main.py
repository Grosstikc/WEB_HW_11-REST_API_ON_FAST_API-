from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
import models, schemas, database

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/contacts/", response_model=schemas.ContactInDB)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[schemas.ContactInDB])
def read_contacts(first_name: Optional[str] = Query(None), last_name: Optional[str] = Query(None), email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Contact)
    if first_name:
        query = query.filter(models.Contact.first_name == first_name)
    if last_name:
        query = query.filter(models.Contact.last_name == last_name)
    if email:
        query = query.filter(models.Contact.email == email)
    contacts = query.all()
    return contacts

@app.get("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db_contact.update(contact.dict(exclude_unset=True))
    db.commit()
    return db_contact

@app.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db.query(models.Contact).filter(models.Contact.id == contact_id).delete()
    db.commit()

@app.get("/contacts/birthdays/", response_model=List[schemas.ContactInDB])
def read_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=7)
    contacts = db.query(models.Contact).filter(models.Contact.birthday.between(today, end_date)).all()
    return contacts
