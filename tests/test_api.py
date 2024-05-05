import requests
import pytest
import subprocess
import time


test_url = "http://localhost:8000"

# test if container is running
def is_container_running(container_name):
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
    return container_name in result.stdout.splitlines()


# start database and api service
def setup_module(module):
    if not is_container_running("jobmarket_db_container"):
        subprocess.run(["docker-compose", "up", "-d", "jobmarket_db"])
        time.sleep(5)
        if not is_container_running("jobmarket_db_container"):
            subprocess.run(["docker-compose", "up", "-d", "jobmarket_db"])
            time.sleep(5)
            pytest.fail("Database container failed to start")
    if not is_container_running("jobmarket_api_container"):
        subprocess.run(["docker-compose", "up", "-d", "jobmarket_api"])
        time.sleep(5)
        if not is_container_running("jobmarket_api_container"):
            subprocess.run(["docker-compose", "up", "-d", "jobmarket_api"])
            time.sleep(5)
            pytest.fail("API container failed to start")


# stop services, not neededd at the moment because these services should be running non stop
"""
def teardown_module(module):
    if is_container_running("jobmarket_api"):
        subprocess.run(["docker-compose", "down", "jobmarket_api"], cwd="../")
    if is_container_running("jobmarket_api"):
        subprocess.run(["docker-compose", "down", "jobmarket_api"], cwd="../")
"""


# test if api is running
# no endpoint / configured, should return 404 and it´s message
def test_api_running():
    response = requests.get(f"{test_url}/")
    assert response.status_code == 404
    assert response.json() == {"detail":"Not Found"}


# test if endpoint /countries contains "United kingdom ""
def test_countries():
    response = requests.get(f"{test_url}/countries")
    assert response.status_code == 200
    country_list = response.json()["countries"]
    assert "United Kingdom" in country_list

    
# test if endpoint /database contains job titles, at least "Other" should be included
def test_job_titles():
    response = requests.get(f"{test_url}/job_titles")
    assert response.status_code == 200
    job_list = response.json()["job titles"]
    assert "Other" in job_list


# test endpoint /skills, at least one skill has to be in the database after tranformation
def test_skills():
    response = requests.get(f"{test_url}/skills")
    assert response.status_code == 200
    skill_list = response.json()["skills"]
    assert len(skill_list) >= 1


# test endpoint /experience, must contain "Junior", "Medium", "Senior" and nothing else
def test_skills():
    response = requests.get(f"{test_url}/experience")
    assert response.status_code == 200
    exp_list = response.json()["experience levels"]
    assert len(exp_list) == 3 and  all(exp_level in exp_list for exp_level in ("Junior", "Medium", "Senior"))


# test prediction with job title and country, "Other" and "United kingdom" should always be in the database
# optional fields are not set
def test_correct_minimal_prediction():
    data = {
        "job_title": "Other",
        "country": "United Kingdom",
        "city": None,
        "experience": None,
        "skills": None
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 200
    min_salary = response.json()["predictions"][0]["minimum yearly salary"].split()[0]
    max_salary = response.json()["predictions"][1]["maximum yearly salary"].split()[0]
    assert  0 <= float(min_salary) <= float(max_salary)


# test prediction with optional fields
def test_correct_optional_prediction():
    data = {
        "job_title": "Data architect",
        "country": "United Kingdom",
        "city": None,
        "experience": "Medium",
        "skills": None
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 200
    min_salary = response.json()["predictions"][0]["minimum yearly salary"].split()[0]
    max_salary = response.json()["predictions"][1]["maximum yearly salary"].split()[0]
    assert  0 <= float(min_salary) <= float(max_salary)


# test prediction with wrong job title
def test_wrong_jobtitle_prediction():
    data = {
        "job_title": "wrong value",
        "country": "wrong value",
        "city": "wrong value",
        "experience": "wrong value",
        "skills": ["wrong value"]
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "Job title not found"

    
# test prediction with wrong country
def test_wrong_country_prediction():
    data = {
        "job_title": "Other",
        "country": "wrong value",
        "city": "wrong value",
        "experience": "wrong value",
        "skills": ["wrong value"]
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "Country not found"

    
# test prediction with wrong city
def test_wrong_city_prediction():
    data = {
        "job_title": "Other",
        "country": "United Kingdom",
        "city": "wrong value",
        "experience": "wrong value",
        "skills": ["wrong value"]
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "City not found"


# test prediction with wrong experience
def test_wrong_experience_prediction():
    data = {
        "job_title": "Other",
        "country": "United Kingdom",
        "city": None,
        "experience": "wrong value",
        "skills": ["wrong value"]
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "Experience class not found"
 
    
# test prediction with wrong type
def test_wrong_skill_type_prediction():
    data = {
        "job_title": "Other",
        "country": "United Kingdom",
        "city": None,
        "experience": None,
        "skills": "wrong type"
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be a valid list"
 
    
# test prediction with wrong value
def test_wrong_skill_value_prediction():
    data = {
        "job_title": "Other",
        "country": "United Kingdom",
        "city": None,
        "experience": None,
        "skills": ["wrong value"]
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "Some skill(s) not found"

# test that a 422 type error occurs before a 404 value not found error
# test prediction with wrong type
def test_wrong_skill_type_prediction():
    data = {
        "job_title": "Other",
        "country": "United Kingdom",
        "city": "wrong value",
        "experience": None,
        "skills": "wrong type"
    }
    response = requests.post(f"{test_url}/make_prediciton", json=data)
    
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be a valid list"