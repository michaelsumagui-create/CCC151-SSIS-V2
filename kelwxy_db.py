"""
kelwxy_db.py  –  SQLite backend for KELWXY Student Information System
Replaces all CSV files.  Provides full CRUDL + search, sort, pagination.
"""

import sqlite3
import random
from contextlib import contextmanager

DB_PATH = "kelwxy.db"

# ──────────────────────────────────────────────────────────────────────────────
#  Connection helper
# ──────────────────────────────────────────────────────────────────────────────

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
#  Schema creation
# ──────────────────────────────────────────────────────────────────────────────

def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS colleges (
                college_code  TEXT PRIMARY KEY,
                college_name  TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS programs (
                program_code  TEXT PRIMARY KEY,
                program_name  TEXT NOT NULL UNIQUE,
                college_code  TEXT,
                FOREIGN KEY (college_code) REFERENCES colleges(college_code)
                    ON UPDATE CASCADE ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                id_number    TEXT PRIMARY KEY,
                first_name   TEXT NOT NULL,
                last_name    TEXT NOT NULL,
                gender       TEXT NOT NULL CHECK(gender IN ('Male','Female')),
                year_level   INTEGER NOT NULL CHECK(year_level BETWEEN 1 AND 4),
                program_code TEXT,
                FOREIGN KEY (program_code) REFERENCES programs(program_code)
                    ON UPDATE CASCADE ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_students_program  ON students(program_code);
            CREATE INDEX IF NOT EXISTS idx_programs_college  ON programs(college_code);
            CREATE INDEX IF NOT EXISTS idx_students_lastname ON students(last_name);
            CREATE INDEX IF NOT EXISTS idx_students_id       ON students(id_number);
        """)


# ──────────────────────────────────────────────────────────────────────────────
#  COLLEGE  CRUDL
# ──────────────────────────────────────────────────────────────────────────────

def add_college(college_code: str, college_name: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO colleges (college_code, college_name) VALUES (?, ?)",
            (college_code.strip(), college_name.strip())
        )


def get_college(college_code: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM colleges WHERE college_code = ?", (college_code,)
        ).fetchone()
        return dict(row) if row else None


def update_college(old_code: str, new_code: str, new_name: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE colleges SET college_code = ?, college_name = ? WHERE college_code = ?",
            (new_code.strip(), new_name.strip(), old_code)
        )


def delete_college(college_code: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM colleges WHERE college_code = ?", (college_code,))


def list_colleges(
    search: str = "",
    search_field: str = "college_code",
    sort_col: str = "college_code",
    sort_order: str = "ASC",
    page: int = 1,
    page_size: int = 20
):
    valid_cols   = {"college_code", "college_name"}
    valid_orders = {"ASC", "DESC"}
    sort_col     = sort_col     if sort_col     in valid_cols   else "college_code"
    sort_order   = sort_order   if sort_order   in valid_orders else "ASC"
    search_field = search_field if search_field in valid_cols   else "college_code"

    offset = (page - 1) * page_size
    where  = f"WHERE {search_field} LIKE ?" if search else ""
    params = (f"%{search}%",) if search else ()

    with get_connection() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM colleges {where}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM colleges {where} ORDER BY {sort_col} {sort_order} LIMIT ? OFFSET ?",
            params + (page_size, offset)
        ).fetchall()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [dict(r) for r in rows]}


def college_exists(college_code: str) -> bool:
    with get_connection() as conn:
        return conn.execute(
            "SELECT 1 FROM colleges WHERE LOWER(college_code)=LOWER(?)", (college_code,)
        ).fetchone() is not None


def college_name_exists(college_name: str) -> bool:
    with get_connection() as conn:
        return conn.execute(
            "SELECT 1 FROM colleges WHERE LOWER(college_name)=LOWER(?)", (college_name,)
        ).fetchone() is not None


# ──────────────────────────────────────────────────────────────────────────────
#  PROGRAM  CRUDL
# ──────────────────────────────────────────────────────────────────────────────

def add_program(program_code: str, program_name: str, college_code: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO programs (program_code, program_name, college_code) VALUES (?,?,?)",
            (program_code.strip(), program_name.strip(), college_code.strip())
        )


def get_program(program_code: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM programs WHERE program_code = ?", (program_code,)
        ).fetchone()
        return dict(row) if row else None


def update_program(old_code: str, new_code: str, new_name: str, new_college: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE programs SET program_code=?, program_name=?, college_code=? WHERE program_code=?",
            (new_code.strip(), new_name.strip(), new_college.strip(), old_code)
        )


def delete_program(program_code: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM programs WHERE program_code = ?", (program_code,))


def list_programs(
    search: str = "",
    search_field: str = "program_code",
    sort_col: str = "program_code",
    sort_order: str = "ASC",
    page: int = 1,
    page_size: int = 20
):
    valid_cols   = {"program_code", "program_name", "college_code"}
    valid_orders = {"ASC", "DESC"}
    sort_col     = sort_col     if sort_col     in valid_cols   else "program_code"
    sort_order   = sort_order   if sort_order   in valid_orders else "ASC"
    search_field = search_field if search_field in valid_cols   else "program_code"

    offset = (page - 1) * page_size
    where  = f"WHERE {search_field} LIKE ?" if search else ""
    params = (f"%{search}%",) if search else ()

    with get_connection() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM programs {where}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM programs {where} ORDER BY {sort_col} {sort_order} LIMIT ? OFFSET ?",
            params + (page_size, offset)
        ).fetchall()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [dict(r) for r in rows]}


def get_all_program_codes():
    with get_connection() as conn:
        rows = conn.execute("SELECT program_code FROM programs ORDER BY program_code").fetchall()
        return [r["program_code"] for r in rows]


def get_all_college_codes():
    with get_connection() as conn:
        rows = conn.execute("SELECT college_code FROM colleges ORDER BY college_code").fetchall()
        return [r["college_code"] for r in rows]


def program_exists(program_code: str) -> bool:
    with get_connection() as conn:
        return conn.execute(
            "SELECT 1 FROM programs WHERE LOWER(program_code)=LOWER(?)", (program_code,)
        ).fetchone() is not None


def program_name_exists(program_name: str) -> bool:
    with get_connection() as conn:
        return conn.execute(
            "SELECT 1 FROM programs WHERE LOWER(program_name)=LOWER(?)", (program_name,)
        ).fetchone() is not None


# ──────────────────────────────────────────────────────────────────────────────
#  STUDENT  CRUDL
# ──────────────────────────────────────────────────────────────────────────────

def add_student(id_number: str, first_name: str, last_name: str,
                gender: str, year_level: int, program_code: str):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO students
               (id_number, first_name, last_name, gender, year_level, program_code)
               VALUES (?,?,?,?,?,?)""",
            (id_number.strip(), first_name.strip(), last_name.strip(),
             gender.strip(), int(year_level), program_code.strip() or None)
        )


def get_student(id_number: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE id_number = ?", (id_number,)
        ).fetchone()
        return dict(row) if row else None


def update_student(old_id: str, new_id: str, first_name: str, last_name: str,
                   gender: str, year_level: int, program_code: str):
    with get_connection() as conn:
        conn.execute(
            """UPDATE students
               SET id_number=?, first_name=?, last_name=?, gender=?,
                   year_level=?, program_code=?
               WHERE id_number=?""",
            (new_id.strip(), first_name.strip(), last_name.strip(),
             gender.strip(), int(year_level),
             program_code.strip() or None, old_id)
        )


def delete_student(id_number: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM students WHERE id_number = ?", (id_number,))


def list_students(
    search: str = "",
    search_field: str = "id_number",
    sort_col: str = "id_number",
    sort_order: str = "ASC",
    page: int = 1,
    page_size: int = 20
):
    valid_cols   = {"id_number", "first_name", "last_name", "gender", "year_level", "program_code"}
    valid_orders = {"ASC", "DESC"}
    sort_col     = sort_col     if sort_col     in valid_cols   else "id_number"
    sort_order   = sort_order   if sort_order   in valid_orders else "ASC"
    search_field = search_field if search_field in valid_cols   else "id_number"

    offset = (page - 1) * page_size
    where  = f"WHERE {search_field} LIKE ?" if search else ""
    params = (f"%{search}%",) if search else ()

    with get_connection() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM students {where}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"""SELECT * FROM students {where}
                ORDER BY {sort_col} {sort_order}
                LIMIT ? OFFSET ?""",
            params + (page_size, offset)
        ).fetchall()
    return {"total": total, "page": page, "page_size": page_size,
            "data": [dict(r) for r in rows]}


def student_exists(id_number: str) -> bool:
    with get_connection() as conn:
        return conn.execute(
            "SELECT 1 FROM students WHERE id_number=?", (id_number,)
        ).fetchone() is not None


# ──────────────────────────────────────────────────────────────────────────────
#  Seed data
# ──────────────────────────────────────────────────────────────────────────────

COLLEGES = [
    ("CSS",  "College of Computer Studies"),
    ("CSM",  "College of Science and Mathematics"),
    ("COE",  "College of Engineering"),
    ("CHS",  "College of Health Sciences"),
    ("CEBA", "College of Economics Business and Accountancy"),
    ("CED",  "College of Education"),
    ("CASS", "College of Arts and Social Sciences"),
]

PROGRAMS = [
    ("BTLED-HEE",    "Bachelor of Technology and Livelihood Education - Home Economics",       "CED"),
    ("BTLED-IAA",    "Bachelor of Technology and Livelihood Education - Industrial Arts",       "CED"),
    ("BSEd-Eng",     "Bachelor of Secondary Education - English",                              "CED"),
    ("BSEd-Math",    "Bachelor of Secondary Education - Mathematics",                          "CED"),
    ("BSEd-Sci",     "Bachelor of Secondary Education - Science",                              "CED"),
    ("BSEd-Fil",     "Bachelor of Secondary Education - Filipino",                             "CED"),
    ("BSEd-SocSci",  "Bachelor of Secondary Education - Social Science",                       "CED"),
    ("BS Psych",     "Bachelor of Science in Psychology",                                      "CASS"),
    ("BA SocSci",    "Bachelor of Arts in Social Sciences",                                    "CASS"),
    ("BA Comm",      "Bachelor of Arts in Communication",                                      "CASS"),
    ("BA Hist",      "Bachelor of Arts in History",                                            "CASS"),
    ("BA Phil",      "Bachelor of Arts in Philosophy",                                         "CASS"),
    ("BS Math",      "Bachelor of Science in Mathematics",                                     "CSM"),
    ("BS Bio",       "Bachelor of Science in Biology",                                         "CSM"),
    ("BS Chem",      "Bachelor of Science in Chemistry",                                       "CSM"),
    ("BS EnvSci",    "Bachelor of Science in Environmental Science",                           "CSM"),
    ("BS Stat",      "Bachelor of Science in Statistics",                                      "CSM"),
    ("BS Marine Bio","Bachelor of Science in Marine Biology",                                  "CSM"),
    ("BSCE",         "Bachelor of Science in Civil Engineering",                               "COE"),
    ("BSEE",         "Bachelor of Science in Electrical Engineering",                          "COE"),
    ("BSME",         "Bachelor of Science in Mechanical Engineering",                          "COE"),
    ("BSChE",        "Bachelor of Science in Chemical Engineering",                            "COE"),
    ("BSIE",         "Bachelor of Science in Industrial Engineering",                          "COE"),
    ("BSECE",        "Bachelor of Science in Electronics Engineering",                         "COE"),
    ("BSCS",         "Bachelor of Science in Computer Science",                                "CSS"),
    ("BSIT",         "Bachelor of Science in Information Technology",                          "CSS"),
    ("BSIS",         "Bachelor of Science in Information Systems",                             "CSS"),
    ("BSEMC",        "Bachelor of Science in Entertainment and Multimedia Computing",          "CSS"),
    ("BSDA",         "Bachelor of Science in Data Analytics",                                  "CSS"),
    ("BS CyberSec",  "Bachelor of Science in Cybersecurity",                                   "CSS"),
    ("BSBA-FM",      "Bachelor of Science in Business Administration - Financial Management",  "CEBA"),
    ("BSBA-MM",      "Bachelor of Science in Business Administration - Marketing Management",  "CEBA"),
    ("BSA",          "Bachelor of Science in Accountancy",                                     "CEBA"),
    ("BS Econ",      "Bachelor of Science in Economics",                                       "CEBA"),
    ("BSN",          "Bachelor of Science in Nursing",                                         "CHS"),
    ("BSPT",         "Bachelor of Science in Physical Therapy",                                "CHS"),
    ("BSMLS",        "Bachelor of Science in Medical Laboratory Science",                      "CHS"),
    ("BSPH",         "Bachelor of Science in Public Health",                                   "CHS"),
    ("BPharm",       "Bachelor of Science in Pharmacy",                                        "CHS"),
]

FIRST_NAMES = [
    "James","Maria","John","Patricia","Robert","Jennifer","Michael","Linda",
    "William","Barbara","David","Elizabeth","Richard","Susan","Joseph","Jessica",
    "Thomas","Sarah","Charles","Karen","Christopher","Lisa","Daniel","Nancy",
    "Matthew","Betty","Anthony","Margaret","Mark","Sandra","Donald","Ashley",
    "Steven","Dorothy","Paul","Kimberly","Andrew","Emily","Joshua","Donna",
    "Kevin","Michelle","Brian","Carol","George","Amanda","Edward","Melissa",
    "Ronald","Deborah","Timothy","Stephanie","Jason","Rebecca","Jeffrey","Laura",
    "Ryan","Sharon","Jacob","Cynthia","Gary","Kathleen","Nicholas","Amy",
    "Eric","Angela","Jonathan","Shirley","Stephen","Anna","Larry","Brenda",
    "Justin","Pamela","Scott","Emma","Brandon","Nicole","Frank","Helen",
    "Raymond","Samantha","Gregory","Katherine","Samuel","Christine","Patrick","Debra",
    "Juan","Rachel","Jack","Carolyn","Dennis","Janet","Jerry","Maria",
    "Alexander","Heather","Tyler","Diane","Jose","Julie","Aaron","Joyce",
    "Henry","Victoria","Douglas","Kelly","Adam","Christina","Nathan","Ruth",
    "Jose","Maria","Juan","Ana","Carlo","Ella","Miguel","Sofia","Luis","Isabel",
    "Marco","Camille","Angelo","Bianca","Paolo","Crisanta","Rafael","Liza",
    "Gabriel","Marites","Christian","Rowena","Ramon","Rosario","Eduardo","Gina",
    "Fernando","Maricel","Antonio","Luz","Ricardo","Teresita","Roberto","Fe",
    "Manuel","Erlinda","Cesar","Corazon","Bernardo","Edna","Alfredo","Dolores",
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
    "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
    "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson",
    "White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker",
    "Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell",
    "Carter","Roberts",
    "Santos","Reyes","Cruz","Bautista","Ocampo","Garcia","Torres","Ramos",
    "Aquino","Mendoza","Villanueva","Dela Cruz","Fernandez","De Leon","Flores",
    "Gonzales","Diaz","Castro","Morales","Soriano","Aguilar","Bernardo","Navarro",
    "Concepcion","Evangelista","Salazar","Domingo","Pascual","Valdez","Robles",
    "Castillo","Rivera","Santiago","Espinosa","Guevarra","Legaspi","Mercado",
    "Padilla","Tolentino","Abad","Alcantara","Andrada","Apostol","Aragon",
    "Araneta","Arceo","Arcilla","Arenas","Arguelles","Arias","Arroyo",
    "Austria","Avila","Ayala","Bacani","Baclayon","Bagasao","Balboa",
    "Baluyot","Banaag","Bandala","Barrientos","Barrios","Batalla","Batungbakal",
]


def seed_db():
    with get_connection() as conn:
        if conn.execute("SELECT COUNT(*) FROM colleges").fetchone()[0] > 0:
            print("Database already seeded. Skipping.")
            return

    with get_connection() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO colleges (college_code, college_name) VALUES (?,?)",
            COLLEGES
        )

    with get_connection() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO programs (program_code, program_name, college_code) VALUES (?,?,?)",
            PROGRAMS
        )

    program_codes = [p[0] for p in PROGRAMS]
    genders = ["Male", "Female"]
    used_ids = set()
    students = []

    for _ in range(5200):
        while True:
            year   = random.randint(2018, 2025)
            number = random.randint(1, 9999)
            id_num = f"{year}-{number:04d}"
            if id_num not in used_ids:
                used_ids.add(id_num)
                break
        students.append((
            id_num,
            random.choice(FIRST_NAMES),
            random.choice(LAST_NAMES),
            random.choice(genders),
            random.randint(1, 4),
            random.choice(program_codes),
        ))

    with get_connection() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO students
               (id_number, first_name, last_name, gender, year_level, program_code)
               VALUES (?,?,?,?,?,?)""",
            students
        )

    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    print(f"Seeded: {len(COLLEGES)} colleges | {len(PROGRAMS)} programs | {count} students")


# ──────────────────────────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────────────────────────

def setup():
    init_db()
    seed_db()


if __name__ == "__main__":
    setup()