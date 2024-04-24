import postgres_queries as pq
from init import database_connection, model_min, model_max
from fastapi import APIRouter, HTTPException
from api_types import Prediction_Request

router = APIRouter()

@router.post("/make_prediciton", tags=["user", "prediction"])
async def get_questions(req : Prediction_Request):
    pass

@router.get("/job_titles", tags=["user", "info"])
async def get_job_titles():
    pass

@router.get("/countries", tags=["user", "info"])
async def get_countries():
    pass

@router.get("/skills", tags=["user", "info"])
async def get_skills():
    pass

pq.get_job_title_list()
pq.get_country_list()
pq.get_experience_list()
pq.get_skill_list()
pq.get_experience_list()
