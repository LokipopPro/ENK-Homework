from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils import get_db, calculate_accuracy, calculate_incorrect, check_overdue
from app.models import HomeworkType, HomeworkCycle, HomeworkRecord, Student, User
from app.schemas import (
    HomeworkTypeCreate, HomeworkTypeUpdate, HomeworkTypeResponse,
    HomeworkCycleCreate, HomeworkCycleUpdate, HomeworkCycleResponse,
    HomeworkRecordCreate, HomeworkRecordUpdate, HomeworkRecordResponse
)
from app.api.auth import get_admin_user, get_sa_user, get_current_user

router = APIRouter()

# 作业类型管理

# 获取所有作业类型
@router.get("/types", response_model=List[HomeworkTypeResponse])
def get_homework_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    types = db.query(HomeworkType).offset(skip).limit(limit).all()
    return types

# 创建作业类型（仅管理员）
@router.post("/types", response_model=HomeworkTypeResponse)
def create_homework_type(
    homework_type: HomeworkTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # 检查作业类型名称是否已存在
    db_type = db.query(HomeworkType).filter(HomeworkType.name == homework_type.name).first()
    if db_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Homework type already exists"
        )
    # 创建新作业类型
    db_type = HomeworkType(
        name=homework_type.name,
        description=homework_type.description
    )
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

# 更新作业类型（仅管理员）
@router.put("/types/{type_id}", response_model=HomeworkTypeResponse)
def update_homework_type(
    type_id: int,
    homework_type_update: HomeworkTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_type = db.query(HomeworkType).filter(HomeworkType.id == type_id).first()
    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework type not found"
        )
    # 如果更新名称，检查是否已存在
    if homework_type_update.name and homework_type_update.name != db_type.name:
        existing_type = db.query(HomeworkType).filter(HomeworkType.name == homework_type_update.name).first()
        if existing_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Homework type name already exists"
            )
    # 更新作业类型
    update_data = homework_type_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_type, field, value)
    db.commit()
    db.refresh(db_type)
    return db_type

# 删除作业类型（仅管理员）
@router.delete("/types/{type_id}")
def delete_homework_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_type = db.query(HomeworkType).filter(HomeworkType.id == type_id).first()
    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework type not found"
        )
    # 检查是否有关联的作业记录
    records = db.query(HomeworkRecord).filter(HomeworkRecord.homework_type_id == type_id).first()
    if records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete homework type with existing records"
        )
    db.delete(db_type)
    db.commit()
    return {"message": "Homework type deleted successfully"}

# 作业周期管理

# 获取所有作业周期
@router.get("/cycles", response_model=List[HomeworkCycleResponse])
def get_homework_cycles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cycles = db.query(HomeworkCycle).offset(skip).limit(limit).all()
    return cycles

# 创建作业周期（仅管理员）
@router.post("/cycles", response_model=HomeworkCycleResponse)
def create_homework_cycle(
    homework_cycle: HomeworkCycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # 检查周期名称是否已存在
    db_cycle = db.query(HomeworkCycle).filter(HomeworkCycle.name == homework_cycle.name).first()
    if db_cycle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Homework cycle already exists"
        )
    # 创建新作业周期
    db_cycle = HomeworkCycle(name=homework_cycle.name)
    db.add(db_cycle)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

# 更新作业周期（仅管理员）
@router.put("/cycles/{cycle_id}", response_model=HomeworkCycleResponse)
def update_homework_cycle(
    cycle_id: int,
    homework_cycle_update: HomeworkCycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_cycle = db.query(HomeworkCycle).filter(HomeworkCycle.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework cycle not found"
        )
    # 如果更新名称，检查是否已存在
    if homework_cycle_update.name and homework_cycle_update.name != db_cycle.name:
        existing_cycle = db.query(HomeworkCycle).filter(HomeworkCycle.name == homework_cycle_update.name).first()
        if existing_cycle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Homework cycle name already exists"
            )
    # 更新作业周期
    update_data = homework_cycle_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cycle, field, value)
    db.commit()
    db.refresh(db_cycle)
    return db_cycle

# 删除作业周期（仅管理员）
@router.delete("/cycles/{cycle_id}")
def delete_homework_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    db_cycle = db.query(HomeworkCycle).filter(HomeworkCycle.id == cycle_id).first()
    if not db_cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework cycle not found"
        )
    # 检查是否有关联的作业记录
    records = db.query(HomeworkRecord).filter(HomeworkRecord.cycle_id == cycle_id).first()
    if records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete homework cycle with existing records"
        )
    db.delete(db_cycle)
    db.commit()
    return {"message": "Homework cycle deleted successfully"}

# 作业记录管理

# 获取所有作业记录（仅管理员）
@router.get("/records", response_model=List[HomeworkRecordResponse])
def get_homework_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    records = db.query(HomeworkRecord).offset(skip).limit(limit).all()
    # 构建响应数据
    result = []
    for record in records:
        record_dict = {
            "id": record.id,
            "student_id": record.student_id,
            "student_name": record.student.name,
            "student_level": record.student.level,
            "student_class": record.student.class_,
            "homework_type_id": record.homework_type_id,
            "homework_type_name": record.homework_type.name,
            "cycle_id": record.cycle_id,
            "cycle_name": record.cycle.name,
            "week_number": record.week_number,
            "total_questions": record.total_questions,
            "correct_questions": record.correct_questions,
            "incorrect_questions": record.incorrect_questions,
            "accuracy": record.accuracy,
            "grading_date": record.grading_date,
            "grader_id": record.grader_id,
            "grader_name": record.grader.name,
            "is_overdue": record.is_overdue,
            "remark": record.remark,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
        result.append(record_dict)
    return result

# 获取SA老师的作业记录（仅SA老师）
@router.get("/records/my-records", response_model=List[HomeworkRecordResponse])
def get_my_homework_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_sa_user)
):
    # 获取SA老师名下学生的作业记录
    records = db.query(HomeworkRecord).join(Student).filter(Student.sa_id == current_user.id).offset(skip).limit(limit).all()
    # 构建响应数据
    result = []
    for record in records:
        record_dict = {
            "id": record.id,
            "student_id": record.student_id,
            "student_name": record.student.name,
            "student_level": record.student.level,
            "student_class": record.student.class_,
            "homework_type_id": record.homework_type_id,
            "homework_type_name": record.homework_type.name,
            "cycle_id": record.cycle_id,
            "cycle_name": record.cycle.name,
            "week_number": record.week_number,
            "total_questions": record.total_questions,
            "correct_questions": record.correct_questions,
            "incorrect_questions": record.incorrect_questions,
            "accuracy": record.accuracy,
            "grading_date": record.grading_date,
            "grader_id": record.grader_id,
            "grader_name": record.grader.name,
            "is_overdue": record.is_overdue,
            "remark": record.remark,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
        result.append(record_dict)
    return result

# 获取学生的作业记录
@router.get("/records/student/{student_id}", response_model=List[HomeworkRecordResponse])
def get_student_homework_records(
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查学生是否存在
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
    # 获取学生的作业记录
    records = db.query(HomeworkRecord).filter(HomeworkRecord.student_id == student_id).offset(skip).limit(limit).all()
    # 构建响应数据
    result = []
    for record in records:
        record_dict = {
            "id": record.id,
            "student_id": record.student_id,
            "student_name": record.student.name,
            "student_level": record.student.level,
            "student_class": record.student.class_,
            "homework_type_id": record.homework_type_id,
            "homework_type_name": record.homework_type.name,
            "cycle_id": record.cycle_id,
            "cycle_name": record.cycle.name,
            "week_number": record.week_number,
            "total_questions": record.total_questions,
            "correct_questions": record.correct_questions,
            "incorrect_questions": record.incorrect_questions,
            "accuracy": record.accuracy,
            "grading_date": record.grading_date,
            "grader_id": record.grader_id,
            "grader_name": record.grader.name,
            "is_overdue": record.is_overdue,
            "remark": record.remark,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
        result.append(record_dict)
    return result

# 创建作业记录
@router.post("/records", response_model=HomeworkRecordResponse)
def create_homework_record(
    homework_record: HomeworkRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查学生是否存在
    student = db.query(Student).filter(Student.id == homework_record.student_id).first()
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
    # 检查作业类型是否存在
    homework_type = db.query(HomeworkType).filter(HomeworkType.id == homework_record.homework_type_id).first()
    if not homework_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework type not found"
        )
    # 检查作业周期是否存在
    cycle = db.query(HomeworkCycle).filter(HomeworkCycle.id == homework_record.cycle_id).first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework cycle not found"
        )
    # 验证数据
    if homework_record.correct_questions > homework_record.total_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correct questions cannot exceed total questions"
        )
    # 计算错误题数和正确率
    incorrect_questions = calculate_incorrect(homework_record.correct_questions, homework_record.total_questions)
    accuracy = calculate_accuracy(homework_record.correct_questions, homework_record.total_questions)
    # 检查是否逾期
    is_overdue = check_overdue(homework_record.grading_date)
    # 创建作业记录
    db_record = HomeworkRecord(
        student_id=homework_record.student_id,
        homework_type_id=homework_record.homework_type_id,
        cycle_id=homework_record.cycle_id,
        week_number=homework_record.week_number,
        total_questions=homework_record.total_questions,
        correct_questions=homework_record.correct_questions,
        incorrect_questions=incorrect_questions,
        accuracy=accuracy,
        grading_date=homework_record.grading_date,
        grader_id=current_user.id,
        is_overdue=is_overdue,
        remark=homework_record.remark
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    # 构建响应数据
    record_dict = {
        "id": db_record.id,
        "student_id": db_record.student_id,
        "student_name": student.name,
        "student_level": student.level,
        "student_class": student.class_,
        "homework_type_id": db_record.homework_type_id,
        "homework_type_name": homework_type.name,
        "cycle_id": db_record.cycle_id,
        "cycle_name": cycle.name,
        "week_number": db_record.week_number,
        "total_questions": db_record.total_questions,
        "correct_questions": db_record.correct_questions,
        "incorrect_questions": db_record.incorrect_questions,
        "accuracy": db_record.accuracy,
        "grading_date": db_record.grading_date,
        "grader_id": db_record.grader_id,
        "grader_name": current_user.name,
        "is_overdue": db_record.is_overdue,
        "remark": db_record.remark,
        "created_at": db_record.created_at,
        "updated_at": db_record.updated_at
    }
    return record_dict

# 更新作业记录
@router.put("/records/{record_id}", response_model=HomeworkRecordResponse)
def update_homework_record(
    record_id: int,
    homework_record_update: HomeworkRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查作业记录是否存在
    db_record = db.query(HomeworkRecord).filter(HomeworkRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework record not found"
        )
    # 检查权限：管理员或学生的SA老师
    student = db_record.student
    if current_user.role != "admin" and student.sa_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # 更新作业记录
    update_data = homework_record_update.model_dump(exclude_unset=True)
    
    # 如果更新了总题数或正确题数，重新计算错误题数和正确率
    if "total_questions" in update_data or "correct_questions" in update_data:
        total_questions = update_data.get("total_questions", db_record.total_questions)
        correct_questions = update_data.get("correct_questions", db_record.correct_questions)
        
        # 验证数据
        if correct_questions > total_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Correct questions cannot exceed total questions"
            )
        
        # 重新计算
        incorrect_questions = calculate_incorrect(correct_questions, total_questions)
        accuracy = calculate_accuracy(correct_questions, total_questions)
        update_data["incorrect_questions"] = incorrect_questions
        update_data["accuracy"] = accuracy
    
    # 如果更新了批改日期，重新检查是否逾期
    if "grading_date" in update_data:
        is_overdue = check_overdue(update_data["grading_date"])
        update_data["is_overdue"] = is_overdue
    
    # 应用更新
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db.commit()
    db.refresh(db_record)
    
    # 构建响应数据
    record_dict = {
        "id": db_record.id,
        "student_id": db_record.student_id,
        "student_name": db_record.student.name,
        "student_level": db_record.student.level,
        "student_class": db_record.student.class_,
        "homework_type_id": db_record.homework_type_id,
        "homework_type_name": db_record.homework_type.name,
        "cycle_id": db_record.cycle_id,
        "cycle_name": db_record.cycle.name,
        "week_number": db_record.week_number,
        "total_questions": db_record.total_questions,
        "correct_questions": db_record.correct_questions,
        "incorrect_questions": db_record.incorrect_questions,
        "accuracy": db_record.accuracy,
        "grading_date": db_record.grading_date,
        "grader_id": db_record.grader_id,
        "grader_name": db_record.grader.name,
        "is_overdue": db_record.is_overdue,
        "remark": db_record.remark,
        "created_at": db_record.created_at,
        "updated_at": db_record.updated_at
    }
    return record_dict

# 删除作业记录
@router.delete("/records/{record_id}")
def delete_homework_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查作业记录是否存在
    db_record = db.query(HomeworkRecord).filter(HomeworkRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework record not found"
        )
    # 检查权限：管理员或学生的SA老师
    student = db_record.student
    if current_user.role != "admin" and student.sa_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db.delete(db_record)
    db.commit()
    return {"message": "Homework record deleted successfully"}