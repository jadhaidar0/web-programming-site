import re
from datetime import date

STUDENT_ID = re.compile(r"^\d{9}$")
FULLNAME = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,79}$")
EMAIL = re.compile(r"^[a-z0-9._%+\-]+@net\.usek\.edu\.lb$")
PHONE = re.compile(r"^[0-9][0-9 \-]{5,13}$")
GITHUB = re.compile(r"^https://github\.com/[A-Za-z0-9][A-Za-z0-9\-]{0,38}/?$")
HTTPS_URL = re.compile(r"^https://[A-Za-z0-9.\-]+\.[A-Za-z]{2,}(/\S*)?$")
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
HEXCOLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")

MAJORS = {"computer", "electrical", "biomedical", "telecommunications"}
GRADUATION = {"spring", "summer", "fall"}
YESNO = {"yes", "no"}
PHONE_CODES = {
    "+961", "+971", "+966", "+974", "+965", "+973", "+968", "+962", "+963", "+964",
    "+20", "+90", "+357", "+33", "+32", "+49", "+44", "+39", "+34", "+41", "+31",
    "+46", "+1", "+61", "+55", "+234", "+225", "+27",
}
SKILLS = {
    "programming", "embedded-systems", "electronics", "computer-networks",
    "telecommunications", "biomedical-instrumentation", "artificial-intelligence",
    "signal-processing",
}
SOFTWARE = {
    "MATLAB", "Simulink", "LabVIEW", "LTspice", "Vivado", "SolidWorks", "Proteus",
    "AutoCAD", "ANSYS", "Altium Designer", "Quartus", "KiCad", "Arduino IDE",
}
PROJECT_AREAS = {
    "artificial-intelligence", "web-applications", "cybersecurity", "internet-of-things",
    "power-systems", "renewable-energy", "control-systems",
    "medical-imaging", "biosensors", "medical-devices",
    "wireless-communications", "5g-6g-networks", "digital-signal-processing",
}

REQUIRED = {"student_id", "fullname", "email", "major", "graduation"}

FORM_VERSION = "2026-2027"


def parse_date(text):
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def to_number(text):
    try:
        return float(text)
    except ValueError:
        return None


def to_int(text):
    try:
        return int(text)
    except ValueError:
        return None


def validate_profile(form):
    errors = {}
    cleaned = {}

    for field in REQUIRED:
        if form.get(field, "").strip() == "":
            errors[field] = "This field is required."

    student_id = form.get("student_id", "").strip()
    if student_id != "" and not STUDENT_ID.match(student_id):
        errors["student_id"] = "Student ID must be exactly 9 digits."
    cleaned["student_id"] = student_id

    fullname = form.get("fullname", "").strip()
    if fullname != "" and not FULLNAME.match(fullname):
        errors["fullname"] = "Use letters, spaces, hyphens or apostrophes (2-80 chars)."
    cleaned["fullname"] = fullname

    email = form.get("email", "").strip().lower()
    if email != "" and not EMAIL.match(email):
        errors["email"] = "Use your USEK email (...@net.usek.edu.lb)."
    cleaned["email"] = email

    phone_country = form.get("phone_country", "").strip()
    phone = form.get("phone", "").strip()
    if phone != "":
        if phone_country not in PHONE_CODES:
            errors["phone"] = "Choose a country code from the list."
        elif not PHONE.match(phone):
            errors["phone"] = "Enter the number without the country code, e.g. 70 123456."
        cleaned["phone"] = phone_country + " " + phone
    else:
        cleaned["phone"] = ""

    birthdate = form.get("birthdate", "").strip()
    if birthdate != "":
        day = parse_date(birthdate)
        if day is None:
            errors["birthdate"] = "Not a valid date."
        elif day > date.today():
            errors["birthdate"] = "Date of birth cannot be in the future."
        else:
            age = (date.today() - day).days // 365
            if age < 15 or age > 100:
                errors["birthdate"] = "Age looks out of range."
    cleaned["birthdate"] = birthdate

    portfolio = form.get("portfolio", "").strip()
    if portfolio != "" and not GITHUB.match(portfolio):
        errors["portfolio"] = "Use a GitHub URL: https://github.com/username"
    cleaned["portfolio"] = portfolio

    gin446 = form.get("gin446", "").strip()
    if gin446 != "" and not HTTPS_URL.match(gin446):
        errors["gin446"] = "Enter a valid https:// link."
    cleaned["gin446"] = gin446

    major = form.get("major", "").strip().lower()
    if major != "" and major not in MAJORS:
        errors["major"] = "Choose a valid major."
    cleaned["major"] = major

    gpa = form.get("gpa", "").strip()
    if gpa != "":
        number = to_number(gpa)
        if number is None or number < 40 or number > 100:
            errors["gpa"] = "GPA must be a number between 40 and 100."
    cleaned["gpa"] = gpa

    credits = form.get("credits", "").strip()
    if credits != "":
        number = to_int(credits)
        if number is None or number < 0 or number > 148:
            errors["credits"] = "Credits must be a whole number between 0 and 148."
    cleaned["credits"] = credits

    graduation = form.get("graduation", "").strip()
    if graduation != "" and graduation not in GRADUATION:
        errors["graduation"] = "Choose spring, summer or fall."
    cleaned["graduation"] = graduation

    graduation_month = form.get("graduation_month", "").strip()
    if graduation_month != "" and not MONTH.match(graduation_month):
        errors["graduation_month"] = "Use the month picker (YYYY-MM)."
    cleaned["graduation_month"] = graduation_month

    internship = form.get("internship_completed", "").strip()
    if internship != "" and internship not in YESNO:
        errors["internship_completed"] = "Choose yes or no."
    cleaned["internship_completed"] = internship

    language = form.get("language", "").strip()
    if len(language) > 40:
        errors["language"] = "Keep it under 40 characters."
    cleaned["language"] = language

    skills = form.getlist("skills")
    good_skills = []
    bad_skills = []
    for skill in skills:
        if skill in SKILLS:
            good_skills.append(skill)
        else:
            bad_skills.append(skill)
    if bad_skills:
        errors["skills"] = "Unknown skill(s): " + ", ".join(bad_skills)
    cleaned["skills"] = good_skills

    software = form.getlist("software")
    good_software = []
    bad_software = []
    for item in software:
        if item in SOFTWARE:
            good_software.append(item)
        else:
            bad_software.append(item)
    if bad_software:
        errors["software"] = "Unknown software: " + ", ".join(bad_software)
    cleaned["software"] = good_software

    project_title = form.get("project_title", "").strip()
    if len(project_title) > 120:
        errors["project_title"] = "Title must be 120 characters or fewer."
    cleaned["project_title"] = project_title

    project_area = form.get("project_area", "").strip()
    if project_area != "" and project_area not in PROJECT_AREAS:
        errors["project_area"] = "Choose a valid project area."
    cleaned["project_area"] = project_area

    description = form.get("description", "").strip()
    if len(description) > 1000:
        errors["description"] = "Description must be 1000 characters or fewer."
    cleaned["description"] = description

    team_size = form.get("team_size", "").strip()
    if team_size != "":
        number = to_int(team_size)
        if number is None or number < 1 or number > 4:
            errors["team_size"] = "Team size must be a whole number from 1 to 4."
    cleaned["team_size"] = team_size

    project_color = form.get("project_color", "").strip()
    if project_color != "" and not HEXCOLOR.match(project_color):
        errors["project_color"] = "Use a colour like #336699."
    if project_color == "":
        project_color = "#336699"
    cleaned["project_color"] = project_color

    meeting_date = form.get("meeting_date", "").strip()
    if meeting_date != "" and parse_date(meeting_date) is None:
        errors["meeting_date"] = "Not a valid date."
    cleaned["meeting_date"] = meeting_date

    meeting_time = form.get("meeting_time", "").strip()
    if meeting_time != "":
        if not TIME.match(meeting_time):
            errors["meeting_time"] = "Use HH:MM."
        elif meeting_time < "08:00" or meeting_time > "18:00":
            errors["meeting_time"] = "Pick a time between 08:00 and 18:00."
    cleaned["meeting_time"] = meeting_time

    if form.get("confirmation") != "yes":
        errors["confirmation"] = "You must confirm the information is accurate."

    cleaned["form_version"] = FORM_VERSION

    return errors, cleaned
