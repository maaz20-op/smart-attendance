# backend/app/api/routes/schedule.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.db.mongo import db
from app.api.deps import get_current_teacher
from app.utils.utils import serialize_bson
from bson import ObjectId


router = APIRouter(prefix="/schedule", tags=["schedule"])


# Response Models
class ClassPeriod(BaseModel):
    subject: Optional[str] = None
    grade: Optional[str] = None
    room: Optional[str] = None
    start_time: str  # "HH:MM"
    end_time: str    # "HH:MM"
    slot: int
    attendance_status: Optional[str] = None  # "completed", "pending", None


class TodayScheduleResponse(BaseModel):
    classes: List[ClassPeriod]
    current_day: str


@router.get("/today", response_model=TodayScheduleResponse)
async def get_today_schedule(current: dict = Depends(get_current_teacher)):
    """
    Get today's schedule for the authenticated teacher.
    Returns all classes scheduled for the current day of the week.
    """
    user_id = ObjectId(current["id"])
    
    # Fetch teacher document
    teacher = await db.teachers.find_one({"userId": user_id})
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    # Get current day of week
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day = days_of_week[datetime.now().weekday()]
    
    # Extract schedule
    schedule = teacher.get("schedule", {})
    timetable = schedule.get("timetable", [])
    
    # Find today's schedule
    today_classes = []
    for day_schedule in timetable:
        if day_schedule.get("day") == current_day:
            periods = day_schedule.get("periods", [])
            
            for period in periods:
                metadata = period.get("metadata")
                
                # Only include periods with metadata (actual classes)
                if metadata and metadata.get("tracked", True):
                    class_period = ClassPeriod(
                        subject=metadata.get("subject_name"),
                        grade=None,  # Can be extracted from subject_name if needed
                        room=metadata.get("room"),
                        start_time=period.get("start", ""),
                        end_time=period.get("end", ""),
                        slot=period.get("slot", 0),
                        attendance_status=None  # TODO: Check if attendance exists for today
                    )
                    today_classes.append(class_period)
            
            break  # Found today's schedule, no need to continue
    
    # Sort by start time
    today_classes.sort(key=lambda x: x.start_time)
    
    return TodayScheduleResponse(
        classes=today_classes,
        current_day=current_day
    )
