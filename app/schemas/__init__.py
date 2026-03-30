from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern="^(admin|sa)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|disabled)$")

class UserResponse(UserBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Student schemas
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: str = Field(..., min_length=1, max_length=50)
    class_: str = Field(..., alias="class", min_length=1, max_length=100)
    sa_id: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    level: Optional[str] = Field(None, min_length=1, max_length=50)
    class_: Optional[str] = Field(None, alias="class", min_length=1, max_length=100)
    sa_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    sa_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# HomeworkType schemas
class HomeworkTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class HomeworkTypeCreate(HomeworkTypeBase):
    pass

class HomeworkTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class HomeworkTypeResponse(HomeworkTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# HomeworkCycle schemas
class HomeworkCycleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class HomeworkCycleCreate(HomeworkCycleBase):
    pass

class HomeworkCycleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)

class HomeworkCycleResponse(HomeworkCycleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# HomeworkRecord schemas
class HomeworkRecordBase(BaseModel):
    student_id: int
    homework_type_id: int
    cycle_id: int
    week_number: int = Field(..., ge=1, le=53)
    total_questions: int = Field(..., ge=1)
    correct_questions: int = Field(..., ge=0)
    grading_date: date
    remark: Optional[str] = None

class HomeworkRecordCreate(HomeworkRecordBase):
    pass

class HomeworkRecordUpdate(BaseModel):
    total_questions: Optional[int] = Field(None, ge=1)
    correct_questions: Optional[int] = Field(None, ge=0)
    grading_date: Optional[date] = None
    remark: Optional[str] = None

class HomeworkRecordResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_level: str
    student_class: str
    homework_type_id: int
    homework_type_name: str
    cycle_id: int
    cycle_name: str
    week_number: int
    total_questions: int
    correct_questions: int
    incorrect_questions: int
    accuracy: float
    grading_date: date
    grader_id: int
    grader_name: str
    is_overdue: bool
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Statistics schemas
class StudentStats(BaseModel):
    student_id: int
    student_name: str
    average_accuracy: float
    total_records: int
    completed_records: int
    overdue_records: int

class SAStats(BaseModel):
    sa_id: int
    sa_name: str
    total_students: int
    total_records: int
    average_accuracy: float

class ClassStats(BaseModel):
    class_name: str
    total_students: int
    total_records: int
    average_accuracy: float
    completion_rate: float