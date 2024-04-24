from fastapi import FastAPI
from routes import router

app = FastAPI(
	title = "Salary Predictor",
	description = "generates a series of questions",
	version = "0.0.1",
    openapi_tags=[
		{'name':'user',
		'description':'functions that are publicly accessible'},
		{'name':'prediction',
		'description':'functions that are used for salary prediction'},
		{'name':'info',
		'description':'functions that are used to get information about the valid parameter values'}
	]
)

app.include_router(router)