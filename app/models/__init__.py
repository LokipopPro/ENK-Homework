from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, index=True)  # admin or sa
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    students = relationship("Student", back_populates="sa")
    homework_records = relationship("HomeworkRecord", back_populates="grader")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    level = Column(String(50), nullable=False, index=True)
    class_ = Column("class", String(100), nullable=False, index=True)
    sa_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    sa = relationship("User", back_populates="students")
    homework_records = relationship("HomeworkRecord", back_populates="student")

class HomeworkType(Base):
    __tablename__ = "homework_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    homework_records = relationship("HomeworkRecord", back_populates="homework_type")

class HomeworkCycle(Base):
    __tablename__ = "homework_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    homework_records = relationship("HomeworkRecord", back_populates="cycle")

class HomeworkRecord(Base):
    __tablename__ = "homework_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    homework_type_id = Column(Integer, ForeignKey("homework_types.id"), index=True)
    cycle_id = Column(Integer, ForeignKey("homework_cycles.id"), index=True)
    week_number = Column(Integer, nullable=False, index=True)
    total_questions = Column(Integer, nullable=False)
    correct_questions = Column(Integer, nullable=False)
    incorrect_questions = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)
    grading_date = Column(Date, nullable=False, index=True)
    grader_id = Column(Integer, ForeignKey("users.id"), index=True)
    is_overdue = Column(Boolean, nullable=False, default=False)
    remark = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="homework_records")
    homework_type = relationship("HomeworkType", back_populates="homework_records")
    cycle = relationship("HomeworkCycle", back_populates="homework_records")
    grader = relationship("User", back_populates="homework_records")