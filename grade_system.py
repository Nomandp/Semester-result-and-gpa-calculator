from dataclasses import dataclass, field

UNIVERSITY_GRADE_BANDS = [
    (85.0, "A",  4.00),
    (80.0, "A-", 3.70),
    (75.0, "B+", 3.30),
    (70.0, "B",  3.00),
    (65.0, "B-", 2.70),
    (60.0, "C+", 2.30),
    (55.0, "C",  2.00),
    (50.0, "D",  1.00),
    (0.0,  "F",  0.00),
]

COURSE_WEIGHTS = {
    "Attendance": 0.10,
    "Assignments & Quizzes": 0.20,
    "Midterm": 0.30,
    "Final Exam": 0.40,
}

FINAL_PASS_THRESHOLD = 50.0
MAX_CREDIT_HOURS = 3.0


def get_grade_and_gp(percentage: float, final_pct: float) -> tuple[str, float, bool]:
    if final_pct < FINAL_PASS_THRESHOLD:
        return "F", 0.00, False

    for cutoff, letter, gp in UNIVERSITY_GRADE_BANDS:
        if percentage >= cutoff:
            return letter, gp, (letter != "F")
    return "F", 0.00, False


@dataclass
class Subject:
    name: str
    code: str
    category: str
    credit_hours: float
    components: dict
    percentages: dict = field(default_factory=dict)
    contributions: dict = field(default_factory=dict)
    total_percentage: float = 0.0
    final_percentage: float = 0.0
    grade: str = "F"
    grade_point: float = 0.0
    passed_final_rule: bool = False
    risk: str = "HIGH"
    calculation_steps: list[str] = field(default_factory=list)
    targets: dict = field(default_factory=dict)


@dataclass
class StudentRecord:
    name: str
    roll_no: str
    department: str
    semester: str
    subjects: list[Subject] = field(default_factory=list)
    sgpa: float = 0.0
    overall_percentage: float = 0.0
    total_credits: float = 0.0
    earned_credits: float = 0.0
    overall_risk: str = "LOW"