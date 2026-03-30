from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
from typing import Optional
from app.utils import get_db
from app.models import Student, User, HomeworkRecord, HomeworkType, HomeworkCycle
from app.api.auth import get_admin_user, get_sa_user, get_current_user

router = APIRouter()

# 导出学生作业记录为CSV
@router.get("/records/csv")
def export_records_csv(
    student_id: Optional[int] = None,
    sa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建查询
    query = db.query(
        HomeworkRecord.id,
        Student.name.label('student_name'),
        Student.level,
        Student.class_.label('class_name'),
        HomeworkType.name.label('homework_type'),
        HomeworkCycle.name.label('cycle'),
        HomeworkRecord.week_number,
        HomeworkRecord.total_questions,
        HomeworkRecord.correct_questions,
        HomeworkRecord.incorrect_questions,
        HomeworkRecord.accuracy,
        HomeworkRecord.grading_date,
        User.name.label('grader_name'),
        HomeworkRecord.is_overdue,
        HomeworkRecord.remark
    ).join(Student, HomeworkRecord.student_id == Student.id).join(HomeworkType, HomeworkRecord.homework_type_id == HomeworkType.id).join(HomeworkCycle, HomeworkRecord.cycle_id == HomeworkCycle.id).join(User, HomeworkRecord.grader_id == User.id)
    
    # 应用过滤条件
    if student_id:
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
        query = query.filter(HomeworkRecord.student_id == student_id)
    
    if sa_id:
        # 检查SA老师是否存在
        sa = db.query(User).filter(User.id == sa_id, User.role == "sa").first()
        if not sa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SA teacher not found"
            )
        # 检查权限：管理员或SA老师本人
        if current_user.role != "admin" and current_user.id != sa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        query = query.filter(Student.sa_id == sa_id)
    elif current_user.role == "sa":
        # 如果是SA老师，只导出自己名下学生的记录
        query = query.filter(Student.sa_id == current_user.id)
    
    # 执行查询
    records = query.all()
    
    # 转换为DataFrame
    df = pd.DataFrame([{
        "ID": record.id,
        "学生姓名": record.student_name,
        "级别": record.level,
        "班级": record.class_name,
        "作业类型": record.homework_type,
        "周期": record.cycle,
        "周次": record.week_number,
        "总题数": record.total_questions,
        "正确题数": record.correct_questions,
        "错误题数": record.incorrect_questions,
        "正确率": record.accuracy,
        "批改日期": record.grading_date,
        "批改人": record.grader_name,
        "是否逾期": "是" if record.is_overdue else "否",
        "备注": record.remark
    } for record in records])
    
    # 转换为CSV
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=homework_records.csv"}
    )

# 导出学生作业记录为Excel
@router.get("/records/excel")
def export_records_excel(
    student_id: Optional[int] = None,
    sa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建查询
    query = db.query(
        HomeworkRecord.id,
        Student.name.label('student_name'),
        Student.level,
        Student.class_.label('class_name'),
        HomeworkType.name.label('homework_type'),
        HomeworkCycle.name.label('cycle'),
        HomeworkRecord.week_number,
        HomeworkRecord.total_questions,
        HomeworkRecord.correct_questions,
        HomeworkRecord.incorrect_questions,
        HomeworkRecord.accuracy,
        HomeworkRecord.grading_date,
        User.name.label('grader_name'),
        HomeworkRecord.is_overdue,
        HomeworkRecord.remark
    ).join(Student, HomeworkRecord.student_id == Student.id).join(HomeworkType, HomeworkRecord.homework_type_id == HomeworkType.id).join(HomeworkCycle, HomeworkRecord.cycle_id == HomeworkCycle.id).join(User, HomeworkRecord.grader_id == User.id)
    
    # 应用过滤条件
    if student_id:
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
        query = query.filter(HomeworkRecord.student_id == student_id)
    
    if sa_id:
        # 检查SA老师是否存在
        sa = db.query(User).filter(User.id == sa_id, User.role == "sa").first()
        if not sa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SA teacher not found"
            )
        # 检查权限：管理员或SA老师本人
        if current_user.role != "admin" and current_user.id != sa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        query = query.filter(Student.sa_id == sa_id)
    elif current_user.role == "sa":
        # 如果是SA老师，只导出自己名下学生的记录
        query = query.filter(Student.sa_id == current_user.id)
    
    # 执行查询
    records = query.all()
    
    # 转换为DataFrame
    df = pd.DataFrame([{
        "ID": record.id,
        "学生姓名": record.student_name,
        "级别": record.level,
        "班级": record.class_name,
        "作业类型": record.homework_type,
        "周期": record.cycle,
        "周次": record.week_number,
        "总题数": record.total_questions,
        "正确题数": record.correct_questions,
        "错误题数": record.incorrect_questions,
        "正确率": record.accuracy,
        "批改日期": record.grading_date,
        "批改人": record.grader_name,
        "是否逾期": "是" if record.is_overdue else "否",
        "备注": record.remark
    } for record in records])
    
    # 转换为Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='作业记录', index=False)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=homework_records.xlsx"}
    )

# 导出学生统计数据为Excel
@router.get("/statistics/excel")
def export_statistics_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 构建学生统计查询
    student_query = db.query(
        Student.id,
        Student.name,
        Student.level,
        Student.class_.label('class_name'),
        User.name.label('sa_name'),
        func.avg(HomeworkRecord.accuracy).label('average_accuracy'),
        func.count(HomeworkRecord.id).label('total_records'),
        func.sum(func.case((HomeworkRecord.accuracy >= 60, 1), else_=0)).label('completed_records'),
        func.sum(func.case((HomeworkRecord.is_overdue == True, 1), else_=0)).label('overdue_records')
    ).outerjoin(HomeworkRecord, Student.id == HomeworkRecord.student_id).join(User, Student.sa_id == User.id)
    
    # 如果是SA老师，只查询自己名下的学生
    if current_user.role == "sa":
        student_query = student_query.filter(Student.sa_id == current_user.id)
    
    # 执行学生统计查询
    student_stats = student_query.group_by(Student.id, Student.name, Student.level, Student.class_, User.name).all()
    
    # 构建班级统计查询
    class_query = db.query(
        Student.class_.label('class_name'),
        func.count(func.distinct(Student.id)).label('total_students'),
        func.count(HomeworkRecord.id).label('total_records'),
        func.avg(HomeworkRecord.accuracy).label('average_accuracy'),
        func.sum(func.case((HomeworkRecord.accuracy >= 60, 1), else_=0)).label('completed_records')
    ).outerjoin(HomeworkRecord, Student.id == HomeworkRecord.student_id)
    
    # 如果是SA老师，只查询自己名下学生的班级
    if current_user.role == "sa":
        class_query = class_query.filter(Student.sa_id == current_user.id)
    
    # 执行班级统计查询
    class_stats = class_query.group_by(Student.class_).all()
    
    # 转换为DataFrame
    student_df = pd.DataFrame([{
        "学生ID": stat.id,
        "学生姓名": stat.name,
        "级别": stat.level,
        "班级": stat.class_name,
        "SA老师": stat.sa_name,
        "平均正确率": round(stat.average_accuracy or 0, 2),
        "总记录数": stat.total_records or 0,
        "完成记录数": stat.completed_records or 0,
        "逾期记录数": stat.overdue_records or 0
    } for stat in student_stats])
    
    class_df = pd.DataFrame([{
        "班级": stat.class_name,
        "学生数量": stat.total_students,
        "总记录数": stat.total_records,
        "平均正确率": round(stat.average_accuracy or 0, 2),
        "完成率": round((stat.completed_records / stat.total_records * 100) if stat.total_records > 0 else 0, 2)
    } for stat in class_stats])
    
    # 转换为Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        student_df.to_excel(writer, sheet_name='学生统计', index=False)
        class_df.to_excel(writer, sheet_name='班级统计', index=False)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=statistics.xlsx"}
    )