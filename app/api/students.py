from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils import get_db
from app.models import Student, User
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.api.auth import get_admin_user, get_sa_user, get_current_user

router = APIRouter()

# 获取所有学生（仅管理员）
@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    students = db.query(Student).offset(skip).limit(limit).all()
    # 添加SA老师姓名
    result = []
    for student in students:
        student_dict = {
            "id": student.id,
            "name": student.name,
            "level": student.level,
            "class_": student.class_,
            "sa_id": student.sa_id,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
            "sa_name": student.sa.name if student.sa else None
        }
        result.append(student_dict)
    return result

# 获取SA老师名下的学生（仅SA老师）
@router.get("/my-students", response_model=List[StudentResponse])
def get_my_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sa_user)
):
    students = db.query(Student).filter(Student.sa_id == current_user.id).offset(skip).limit(limit).all()
    # 添加SA老师姓名
    result = []
    for student in students:
        student_dict = {
            "id": student.id,
            "name": student.name,
            "level": student.level,
            "class_": student.class_,
            "sa_id": student.sa_id,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
            "sa_name": current_user.name
        }
        result.append(student_dict)
    return result

# 获取单个学生
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 检查权限：管理员或学生的SA老师
    if current_user.role != "admin" and student.sa_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 添加SA老师姓名
    student_dict = {
        "id": student.id,
        "name": student.name,
        "level": student.level,
        "class_": student.class_,
        "sa_id": student.sa_id,
        "created_at": student.created_at,
        "updated_at": student.updated_at,
        "sa_name": student.sa.name if student.sa else None
    }
    return student_dict

# 创建学生（仅管理员）
@router.post("/", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # 检查SA老师是否存在且角色为sa
    sa_user = db.query(User).filter(User.id == student.sa_id).first()
    if not sa_user or sa_user.role != "sa":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SA teacher"
        )
    # 创建新学生
    db_student = Student(
        name=student.name,
        level=student.level,
        class_=student.class_,
        sa_id=student.sa_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    # 添加SA老师姓名
    student_dict = {
        "id": db_student.id,
        "name": db_student.name,
        "level": db_student.level,
        "class_": db_student.class_,
        "sa_id": db_student.sa_id,
        "created_at": db_student.created_at,
        "updated_at": db_student.updated_at,
        "sa_name": sa_user.name
    }
    return student_dict

# 更新学生
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    # 检查权限：管理员或学生的SA老师
    if current_user.role != "admin" and db_student.sa_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 如果更新SA老师，检查新SA老师是否存在且角色为sa
    if student_update.sa_id is not None:
        sa_user = db.query(User).filter(User.id == student_update.sa_id).first()
        if not sa_user or sa_user.role != "sa":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SA teacher"
            )
    # 更新学生信息
    update_data = student_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "class_":
            setattr(db_student, "class_", value)
        else:
            setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    # 添加SA老师姓名
    student_dict = {
        "id": db_student.id,
        "name": db_student.name,
        "level": db_student.level,
        "class_": db_student.class_,
        "sa_id": db_student.sa_id,
        "created_at": db_student.created_at,
        "updated_at": db_student.updated_at,
        "sa_name": db_student.sa.name if db_student.sa else None
    }
    return student_dict

# 删除学生（仅管理员）
@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}