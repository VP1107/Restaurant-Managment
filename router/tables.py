from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List

import schema
import model
from services import get_db, get_role

router = APIRouter(prefix="/tables", tags=["tables"])

# View all tables, view table by id
@router.get("", response_model=List[schema.Table])
def view_tables(db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role == "owner" or role == "admin":
        db_tables = db.query(model.Table).all()
        if db_tables:
            return db_tables
        return []
    raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/{table_id}", response_model=schema.Table)
def view_table(table_id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role == "owner" or role == "admin":
        db_table = db.query(model.Table).filter(model.Table.id == table_id).first()
        if db_table:
            return db_table
        raise HTTPException(status_code=404, detail="Table not found")
    raise HTTPException(status_code=403, detail="Not authorized")

# Create table
@router.post("", response_model=schema.Table)
def create_table(table: schema.TableCreate, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role == "owner" or role == "admin":
        db_table = model.Table(**table.model_dump())
        db.add(db_table)
        db.commit()
        db.refresh(db_table)
        return db_table
    raise HTTPException(status_code=403, detail="Not authorized")

# Delete table
@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db), role: str = Depends(get_role)):
    if role == "owner" or role == "admin":
        db_table = db.query(model.Table).filter(model.Table.id == table_id).first()
        if not db_table:
            raise HTTPException(status_code=404, detail="Table not found")
        db.delete(db_table)
        db.commit()
        return {"message": "Table deleted successfully"}
    raise HTTPException(status_code=403, detail="Not authorized")
