from pydantic import BaseModel
from typing import Optional, List
    
    
class Prediction_Request(BaseModel):
    """
    Model for a salary prediction call
    """
    job_title : str
    country : str
    city : Optional[str]
    experience : Optional[str]
    skills : Optional[List[str]]