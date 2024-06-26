from pydantic import BaseModel
from enum import Enum


class UserType(str, Enum):
    admin = 'admin'
    employee = 'employee'
    manager = 'manager'
 
class User(BaseModel):
    name: str
    email: str
    user_type: UserType
    password: str

class User_with_id(BaseModel):
    id : int
    name: str
    email: str
    user_type: UserType
    password: str

class ProjectCreate(BaseModel):
    name: str
    manager_id: int

class Project(BaseModel):
    id : int
    name: str
    manager_id: int

class EmployeeUpdate(BaseModel):
    name: str
    email: str
    password: str
    user_type: UserType

class AssignEmployeeToProject(BaseModel):
    project_id: int
    employee_id: int

class EmployeeSkillUpdate(BaseModel):
    skill_ids: list[int]

class RequestCreate(BaseModel):
    manager_id: int
    project_id: int
    requested_emp_id: int

class Request(BaseModel):
    manager_id: int
    requested_emp_id: int

class Status(str,Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'

class RequestStatus(BaseModel):
    id : int
    manager_id: int
    project_id: int
    requested_emp_id: int
    status: Status

class Skills(BaseModel):
    id : int
    name : str

class Skillname(BaseModel):
    name : str
