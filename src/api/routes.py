import postgres_queries as pq
from init import model_min, model_max, database_connection
from fastapi import APIRouter, HTTPException
import pandas as pd
from api_types import Prediction_Request
from logger import logging

def create_dataframe(request: Prediction_Request) -> pd.DataFrame:
    data = {
        "job_title": [request.job_title],
        "country": [request.country],
        "city": [request.city] if request.city is not None else None,
        #"area_code": [request.area_code] if request.area_code is not None else None,
        #"state": [request.state] if request.state is not None else None,
        "level": [request.experience] if request.experience is not None else None,
        "jobSkillsSumFrequency": [len(request.skills)] if request.skills is not None else None
    }
    return pd.DataFrame(data)

router = APIRouter()

@router.post("/make_prediciton", tags=["user", "prediction"])
async def make_prediction(req : Prediction_Request):
    logging.info(f"make_prediction: request: {req}")
    
    # check request
    try:
        # check if value is present in our database
        job_list = pq.get_job_title_list(database_connection)
        if req.job_title not in job_list:
            raise HTTPException(status_code=404, detail={"error": "Job title not found", "known job titles": job_list})
        
        country_list = pq.get_country_list(database_connection)
        if req.country not in country_list:
            raise HTTPException(status_code=404, detail={"error": "Country not found", "countries in database": country_list})
        
        # check optional fields if value is given
        if req.city:
            city_list = pq.get_city_list(database_connection, req.country) 
            if req.city not in city_list:
                raise HTTPException(status_code=404, detail={"error": "City not found", f"cities for {req.country} in databse": city_list})
        
        if req.skills:
            skill_list = pq.get_skill_list(database_connection)
            if not all(skill in skill_list for skill in req.skills):
                raise HTTPException(status_code=404, detail={"error": "Some skill(s) not found", "skills in database": skill_list})
        else:
            req.skills = []
            
        if req.experience:
            exp_list = pq.get_experience_list(database_connection)
            if not req.experience in exp_list:
                raise HTTPException(status_code=404, detail={"error": "Experience class not found", "experience classes in database": exp_list})
        else: 
            req.experience = "Medium"
            
        # create DataFrame for prediction
        df = create_dataframe(req)
        logging.debug(f"make_prediction: create DataFrame: {df.head()}")
    except HTTPException:
        logging.warning(f"make_prediction: values not in database, see response")
        raise 
    except Exception as a:
        logging.error(f"make_prediction: unkown error while handling request values: {e}")
        raise   
    
    #make prediction
    try:
        min_salary = int(model_min.predict(df).tolist()[0])
        max_salary = int(model_max.predict(df).tolist()[0])
    except Exception as e:
        logging.error(f"make_prediction: prediction error: {e}")
        raise
    
    logging.debug(f"make_prediction: predict min/max: {min_salary, max_salary}")
    return {"predictions": [{"minimum yearly salary": str(min_salary) + " €"}, {"maximum yearly salary": str(max_salary) + " €"}]}

@router.get("/job_titles", tags=["user", "info"])
async def get_job_titles():
    logging.info(f"get_job_titles")
    return {"job titles": pq.get_job_title_list(database_connection)}

@router.get("/countries", tags=["user", "info"])
async def get_countries():
    logging.info(f"get_countries")
    return {"countries": pq.get_country_list(database_connection)}

@router.get("/skills", tags=["user", "info"])
async def get_skills():
    logging.info(f"get_skills")
    return {"skills": pq.get_skill_list(database_connection)}

@router.get("/experience", tags=["user", "info"])
async def get_experience():
    logging.info(f"get_experiences")
    return {"experience levels": pq.get_experience_list(database_connection)}


if __name__ == "__main__":
    print(pq.get_job_title_list(database_connection))
    print(pq.get_country_list(database_connection))
    print(pq.get_experience_list(database_connection))
    print(pq.get_skill_list(database_connection))
    
