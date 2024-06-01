import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path
parent_dir = Path(__file__).parents[1]
sys.path.append(str(parent_dir))

from run import app
from routers.auth import get_current_user,bcrypt_context
from database import get_db,Base
from routers.employee import router as employee_router
from models import User,Project,Skill,Request,EmployeeSkill,Project_assignment,Employee_assignment


# app = FastAPI()
# Set up a test database
TEST_DATABASE_URL = "postgresql://postgres:rohit792A@localhost:5432/test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency function for testing
def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()

app.dependency_overrides[get_db] = override_get_db

#to clear the db after test
def cleanup_db(db):
    db.query(EmployeeSkill).delete()

    db.query(User).filter(User.email != 'ro@gmail.com').delete()
    db.query(Project).delete()
    db.query(Skill).delete()
    db.query(Project_assignment).delete()
    db.query(Employee_assignment).delete()
    db.query(Request).delete()
    db.commit()

    
#create all the tables
Base.metadata.create_all(bind=engine)



# Create a test client
client = TestClient(app)

def override_get_current_user_admin():
    return {"id": 1, "user_type": "admin"}
def override_get_current_user_employee():
    return {"id": 2, "user_type": "employee"}

def override_get_current_user_manager():
    return {"id": 3, "user_type": "manager"}

def override_get_current_user_not_found():
    return {"id": 999, "user_type": "employee"}


def test_login():
    formData = {
        "username": "ro@gmail.com",  
        "password": "ro12"
    }
    response = client.post("/auth/newtoken", data=formData)  
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert "role" in response.json()

def test_update_password_success():
    # Create a test user in the database
    db = next(override_get_db())
    test_user = User(id=2, name="Test User", email="testuser@example.com", user_type="employee", password="oldpassword")
    db.add(test_user)
    db.commit()

    app.dependency_overrides[get_current_user] = override_get_current_user_employee

    # Data for updating password
    userdata = {
        "email": "testuser@example.com",
        "password": "newpassword123"
    }

    # Make the request
    response = client.post("/update_password/", json=userdata)
    cleanup_db(db)

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully"}


def test_update_password_user_not_found():

    db = next(override_get_db())
    test_user = User(id=2, name="Test User", email="testuser@example.com", user_type="employee", password="oldpassword")
    db.add(test_user)
    db.commit()

    app.dependency_overrides[get_current_user] = override_get_current_user_employee


    # Data for updating password
    userdata = {
        "email": "user2@example.com",
        "password": "newpassword123"
    }


    # Make the request
    response = client.post("/update_password/", json=userdata)

    cleanup_db(db)

    # Assertions
    assert response.status_code == 404
    assert response.json() == {"detail": "Email not found"}


