from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.utils import get_db
from app.models import Student, User, HomeworkRecord
from app.schemas import StudentStats, SAStats, ClassStats
from app.api.auth import get_admin_user, get_sa_user, get_current_user

router = APIRouter()

# 获取学生统计数据
@router.get("/students", response_model=List[StudentStats])
def get_student_statistics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建查询
    query = db.query(
        Student.id,
        Student.name,
        func.avg(HomeworkRecord.accuracy).label('average_accuracy'),
        func.count(HomeworkRecord.id).label('total_records'),
        func.sum(func.case((HomeworkRecord.accuracy >= 60, 1), else_=0)).label('completed_records'),
        func.sum(func.case((HomeworkRecord.is_overdue == True, 1), else_=0)).label('overdue_records')
    ).outerjoin(HomeworkRecord, Student.id == HomeworkRecord.student_id)
    
    # 如果是SA老师，只查询自己名下的学生
    if current_user.role == "sa":
        query = query.filter(Student.sa_id == current_user.id)
    
    # 分组并执行查询
    students_stats = query.group_by(Student.id, Student.name).offset(skip).limit(limit).all()
    
    # 转换为响应格式
    result = []
    for stat in students_stats:
        result.append(StudentStats(
            student_id=stat.id,
            student_name=stat.name,
            average_accuracy=round(stat.average_accuracy or 0, 2),
            total_records=stat.total_records or 0,
            completed_records=stat.completed_records or 0,
            overdue_records=stat.overdue_records or 0
        ))
    
    return result

# 获取单个学生的详细统计数据
@router.get("/students/{student_id}")
def get_student_detail_statistics(
    student_id: int,
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
    
    # 获取学生的周正确率趋势
    weekly_stats = db.query(
        HomeworkRecord.week_number,
        func.avg(HomeworkRecord.accuracy).label('average_accuracy')
    ).filter(HomeworkRecord.student_id == student_id).group_by(HomeworkRecord.week_number).order_by(HomeworkRecord.week_number).all()
    
    # 获取学生的作业类型统计
    type_stats = db.query(
        func.count(HomeworkRecord.id).label('count'),
        func.avg(HomeworkRecord.accuracy).label('average_accuracy')
    ).filter(HomeworkRecord.student_id == student_id).group_by(HomeworkRecord.homework_type_id).all()
    
    # 构建响应
    return {
        "student_id": student.id,
        "student_name": student.name,
        "level": student.level,
        "class": student.class_,
        "weekly_stats": [{
            "week_number": stat.week_number,
            "average_accuracy": round(stat.average_accuracy, 2)
        } for stat in weekly_stats],
        "type_stats": [{
            "count": stat.count,
            "average_accuracy": round(stat.average_accuracy, 2)
        } for stat in type_stats]
    }

# 获取SA老师统计数据（仅管理员）
@router.get("/sa", response_model=List[SAStats])
def get_sa_statistics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # 构建查询
    sa_users = db.query(User).filter(User.role == "sa").offset(skip).limit(limit).all()
    
    result = []
    for sa in sa_users:
        # 获取SA老师的学生数量
        total_students = db.query(func.count(Student.id)).filter(Student.sa_id == sa.id).scalar() or 0
        
        # 获取SA老师的作业记录统计
        record_stats = db.query(
            func.count(HomeworkRecord.id).label('total_records'),
            func.avg(HomeworkRecord.accuracy).label('average_accuracy')
        ).join(Student, HomeworkRecord.student_id == Student.id).filter(Student.sa_id == sa.id).first()
        
        result.append(SAStats(
            sa_id=sa.id,
            sa_name=sa.name,
            total_students=total_students,
            total_records=record_stats.total_records or 0,
            average_accuracy=round(record_stats.average_accuracy or 0, 2)
        ))
    
    return result

# 获取班级统计数据
@router.get("/classes", response_model=List[ClassStats])
def get_class_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建查询
    query = db.query(
        Student.class_.label('class_name'),
        func.count(func.distinct(Student.id)).label('total_students'),
        func.count(HomeworkRecord.id).label('total_records'),
        func.avg(HomeworkRecord.accuracy).label('average_accuracy'),
        func.sum(func.case((HomeworkRecord.accuracy >= 60, 1), else_=0)).label('completed_records')
    ).outerjoin(HomeworkRecord, Student.id == HomeworkRecord.student_id)
    
    # 如果是SA老师，只查询自己名下学生的班级
    if current_user.role == "sa":
        query = query.filter(Student.sa_id == current_user.id)
    
    # 分组并执行查询
    class_stats = query.group_by(Student.class_).all()
    
    # 转换为响应格式
    result = []
    for stat in class_stats:
        completion_rate = 0
        if stat.total_records > 0:
            completion_rate = round((stat.completed_records / stat.total_records) * 100, 2)
        
        result.append(ClassStats(
            class_name=stat.class_name,
            total_students=stat.total_students,
            total_records=stat.total_records,
            average_accuracy=round(stat.average_accuracy or 0, 2),
            completion_rate=completion_rate
        ))
    
    return result