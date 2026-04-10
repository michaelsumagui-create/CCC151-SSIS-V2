# config_file.py  — trimmed for database version
# CSV filenames and fieldnames removed (handled by database.py)

header_names = {
    "STUDENTS": [
        ("id_number",    "ID Number"),
        ("first_name",   "First Name"),
        ("last_name",    "Last Name"),
        ("gender",       "Gender"),
        ("year_level",   "Year Level"),
        ("program_code", "Program"),
    ],
    "PROGRAMS": [
        ("program_code", "Program Code"),
        ("program_name", "Program Name"),
        ("college_code", "College Code"),
    ],
    "COLLEGES": [
        ("college_code", "College Code"),
        ("college_name", "College Name"),
    ],
}

search_filter = {
    "student_search_filter": ["ID Number", "First Name", "Last Name", "Gender", "Year Level", "Program Code"],
    "program_search_filter": ["Program Code", "Program Name", "College Code"],
    "college_search_filter": ["College Code", "College Name"],
}