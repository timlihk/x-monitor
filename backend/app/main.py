from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from app.database import SessionLocal, engine, get_db, Base
from app import crud, schemas
from app.services.twitter_service import TwitterService
from app.services.llm_service import LLMService
from app.services.scheduler_service import SchedulerService

Base.metadata.create_all(bind=engine)

app = FastAPI(title="X Monitor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

twitter_service = TwitterService()
llm_service = LLMService()
scheduler_service = SchedulerService()

@app.on_event("startup")
async def startup_event():
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler_service.shutdown()

@app.get("/")
def read_root():
    return {"message": "X Monitor API is running"}

@app.get("/api/terms", response_model=List[schemas.MonitoredTerm])
def get_terms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_monitored_terms(db, skip=skip, limit=limit)

@app.post("/api/terms", response_model=schemas.MonitoredTerm)
def create_term(term: schemas.MonitoredTermCreate, db: Session = Depends(get_db)):
    return crud.create_monitored_term(db=db, term=term)

@app.put("/api/terms/{term_id}", response_model=schemas.MonitoredTerm)
def update_term(term_id: int, term_update: schemas.MonitoredTermUpdate, db: Session = Depends(get_db)):
    db_term = crud.update_monitored_term(db, term_id=term_id, term_update=term_update)
    if db_term is None:
        raise HTTPException(status_code=404, detail="Term not found")
    return db_term

@app.delete("/api/terms/{term_id}")
def delete_term(term_id: int, db: Session = Depends(get_db)):
    success = crud.delete_monitored_term(db, term_id=term_id)
    if not success:
        raise HTTPException(status_code=404, detail="Term not found")
    return {"message": "Term deleted successfully"}

@app.get("/api/results", response_model=List[schemas.Result])
def get_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_results(db, skip=skip, limit=limit)

@app.get("/api/results/{result_id}", response_model=schemas.Result)
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = crud.get_result(db, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

@app.post("/api/run", response_model=schemas.TweetSummaryResponse)
async def manual_run(request: schemas.TweetSummaryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        tweets = await twitter_service.search_tweets(
            keyword=request.keyword,
            restrict_following=request.restrict_following
        )
        
        if not tweets:
            return schemas.TweetSummaryResponse(
                summary="No tweets found for this keyword.",
                tweet_count=0,
                keyword=request.keyword
            )
        
        summary = await llm_service.summarize_tweets(tweets, request.keyword)
        
        term = crud.get_monitored_terms(db)
        matching_term = next((t for t in term if t.keyword == request.keyword), None)
        if matching_term:
            result_data = schemas.ResultCreate(
                keyword_id=matching_term.id,
                tweets_raw=tweets,
                summary=summary
            )
            crud.create_result(db=db, result=result_data)
        
        return schemas.TweetSummaryResponse(
            summary=summary,
            tweet_count=len(tweets),
            keyword=request.keyword
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)