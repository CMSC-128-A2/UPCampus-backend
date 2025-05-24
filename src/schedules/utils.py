from datetime import datetime
import re
from .models import ClassSection

def check_schedule_conflicts(day, time, faculty_id=None, room_id=None, exclude_section_id=None):
    """
    Helper function to check for faculty and room schedule conflicts
    Returns a list of conflicts or empty list if no conflicts exist
    
    Parameters:
    - day: String containing space-separated days (e.g., "M T")
    - time: String in format "11:00 AM - 12:00 PM"
    - faculty_id: Optional ID of the faculty to check conflicts for
    - room_id: Optional ID of the room to check conflicts for
    - exclude_section_id: Optional ID of section to exclude from conflict check
    
    Returns:
    - List of conflict dictionaries with type "faculty" or "room"
    """
    if not day or not time or (faculty_id is None and room_id is None):
        return []
    
    # Split input days into individual days
    input_days = day.split()
    if not input_days:
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
    
    # Get all class sections (will filter further based on faculty or room)
    sections_query = ClassSection.objects.all()
    
    # Exclude the section being edited if provided
    if exclude_section_id:
        sections_query = sections_query.exclude(id=exclude_section_id)
    
    # Check for faculty conflicts if faculty_id is provided
    if faculty_id:
        faculty_conflicts = check_entity_conflicts(
            sections_query.filter(faculty_id=faculty_id),
            input_days,
            start_time,
            end_time,
            time_pattern,
            "faculty"
        )
        conflicts.extend(faculty_conflicts)
    
    # Check for room conflicts if room_id is provided
    if room_id:
        room_conflicts = check_entity_conflicts(
            sections_query.filter(room_id=room_id),
            input_days,
            start_time,
            end_time,
            time_pattern,
            "room"
        )
        conflicts.extend(room_conflicts)
    
    return conflicts

def check_entity_conflicts(sections, input_days, start_time, end_time, time_pattern, conflict_type):
    """
    Helper function to check for conflicts in a filtered queryset
    
    Parameters:
    - sections: QuerySet of ClassSection filtered by entity (faculty or room)
    - input_days: List of day strings to check
    - start_time: Start time as datetime object
    - end_time: End time as datetime object
    - time_pattern: Compiled regex pattern for time format
    - conflict_type: String indicating the type of conflict ("faculty" or "room")
    
    Returns:
    - List of conflict dictionaries
    """
    conflicts = []
    
    # Check each individual day for conflicts
    for input_day in input_days:
        # Get sections that might contain this day
        day_sections = sections.filter(schedule__contains=input_day)
        
        for section in day_sections:
            # Parse the schedule string (format: "M TH | 11:00 AM - 12:00 PM")
            section_parts = section.schedule.split('|')
            if len(section_parts) != 2:
                continue
                
            section_days, section_time = section_parts[0].strip(), section_parts[1].strip()
            section_day_list = section_days.split()
            
            # Check if this specific day is included in section's schedule
            if input_day not in section_day_list:
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
                conflict = {
                    "type": conflict_type,
                    "course": section.course.course_code,
                    "section": section.section,
                    "schedule": section.schedule,
                    "room": str(section.room) if section.room else None,
                    "conflict_day": input_day  # Added for clarity in error messages
                }
                
                # Only add unique conflicts
                if not any(c["section"] == conflict["section"] and 
                          c["course"] == conflict["course"] for c in conflicts):
                    conflicts.append(conflict)
    
    return conflicts
