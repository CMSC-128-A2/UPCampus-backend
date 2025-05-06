from datetime import datetime
import re
from .models import ClassSection

def check_faculty_schedule_conflicts(day, time, faculty_id, exclude_section_id=None):
    """
    Helper function to check for faculty schedule conflicts
    Returns a list of conflicts or empty list if no conflicts exist
    """
    if not all([day, time, faculty_id]):
        return []
        
    # Parse the time string to get start and end times
    # Format: "11:00 AM - 12:00 PM"
    time_pattern = r"(\d+:\d+\s*[AP]M)\s*-\s*(\d+:\d+\s*[AP]M)"
    time_match = re.match(time_pattern, time)
    
    if not time_match:
        return []
    
    start_time_str, end_time_str = time_match.groups()
    
    # Convert to datetime objects for comparison
    try:
        start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p")
        end_time = datetime.strptime(end_time_str.strip(), "%I:%M %p")
    except ValueError:
        return []
    
    conflicts = []
    
    # Get all class sections for this faculty with the same day
    day_sections = ClassSection.objects.filter(
        faculty_id=faculty_id,
        schedule__contains=day
    )
    
    # Exclude the section being edited if provided
    if exclude_section_id:
        day_sections = day_sections.exclude(id=exclude_section_id)
    
    for section in day_sections:
        # Parse the schedule string (format: "M TH | 11:00 AM - 12:00 PM")
        section_parts = section.schedule.split('|')
        if len(section_parts) != 2:
            continue
            
        section_days, section_time = section_parts[0].strip(), section_parts[1].strip()
        section_day_list = section_days.split()
        
        # Skip if the day doesn't match
        if not any(d in day.split() for d in section_day_list):
            continue
        
        # Check time overlap
        section_time_match = re.match(time_pattern, section_time)
        if not section_time_match:
            continue
            
        section_start_str, section_end_str = section_time_match.groups()
        
        try:
            section_start = datetime.strptime(section_start_str.strip(), "%I:%M %p")
            section_end = datetime.strptime(section_end_str.strip(), "%I:%M %p")
        except ValueError:
            continue
        
        # Check for time overlap
        has_time_overlap = (
            (start_time <= section_start < end_time) or
            (start_time < section_end <= end_time) or
            (section_start <= start_time < section_end) or
            (section_start < end_time <= section_end)
        )
        
        if has_time_overlap:
            conflicts.append({
                "type": "faculty",
                "course": section.course.course_code,
                "section": section.section,
                "schedule": section.schedule,
                "room": section.room
            })
    
    return conflicts 