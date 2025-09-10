from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from app.models import MonitoredTerm, Result
from app.schemas import MonitoredTermCreate, MonitoredTermUpdate, ResultCreate

def get_monitored_terms(db: Session, skip: int = 0, limit: int = 100) -> List[MonitoredTerm]:
    return db.query(MonitoredTerm).offset(skip).limit(limit).all()

def get_monitored_term(db: Session, term_id: int) -> Optional[MonitoredTerm]:
    return db.query(MonitoredTerm).filter(MonitoredTerm.id == term_id).first()

def get_active_monitored_terms(db: Session) -> List[MonitoredTerm]:
    return db.query(MonitoredTerm).filter(MonitoredTerm.active == True).all()

def create_monitored_term(db: Session, term: MonitoredTermCreate) -> MonitoredTerm:
    db_term = MonitoredTerm(**term.dict())
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term

def update_monitored_term(db: Session, term_id: int, term_update: MonitoredTermUpdate) -> Optional[MonitoredTerm]:
    db_term = db.query(MonitoredTerm).filter(MonitoredTerm.id == term_id).first()
    if db_term:
        update_data = term_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_term, field, value)
        db.commit()
        db.refresh(db_term)
    return db_term

def delete_monitored_term(db: Session, term_id: int) -> bool:
    db_term = db.query(MonitoredTerm).filter(MonitoredTerm.id == term_id).first()
    if db_term:
        db.delete(db_term)
        db.commit()
        return True
    return False

def get_results(db: Session, skip: int = 0, limit: int = 100) -> List[Result]:
    return db.query(Result).order_by(desc(Result.created_at)).offset(skip).limit(limit).all()

def get_result(db: Session, result_id: int) -> Optional[Result]:
    return db.query(Result).filter(Result.id == result_id).first()

def get_latest_results_per_term(db: Session) -> List[Result]:
    subquery = db.query(
        Result.keyword_id,
        func.max(Result.created_at).label('max_created_at')
    ).group_by(Result.keyword_id).subquery()
    
    return db.query(Result).join(
        subquery,
        (Result.keyword_id == subquery.c.keyword_id) &
        (Result.created_at == subquery.c.max_created_at)
    ).all()

def create_result(db: Session, result: ResultCreate) -> Result:
    db_result = Result(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result