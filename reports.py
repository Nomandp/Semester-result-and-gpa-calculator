import csv
import os
from datetime import datetime
from matplotlib.figure import Figure
from grade_system import StudentRecord

REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def build_university_transcript(student: StudentRecord) -> str:
    line = "=" * 88
    thin = "-" * 88
    out = [
        line,
        "                   UNIVERSITY SEMESTER RESULT & FULL CALCULATION SHEET",
        line,
        f"Student Name : {student.name:<30} Roll No      : {student.roll_no}",
        f"Department   : {student.department:<30} Semester     : {student.semester}",
        f"Date         : {datetime.now():%Y-%m-%d %H:%M}                  Passing Rule : >= 50% in Final Exam",
        thin,
        f"{'Code':<9}{'Subject Name':<21}{'Type':<7}{'Credits':>8}{'Final%':>8}{'Total%':>8}{'Grade':>7}{'GP':>6}{'Risk':>8}",
        thin,
    ]

    for s in student.subjects:
        out.append(
            f"{s.code:<9}{s.name[:20]:<21}{s.category:<7}{s.credit_hours:>8.1f}"
            f"{s.final_percentage:>7.1f}%{s.total_percentage:>7.1f}%{s.grade:>7}{s.grade_point:>6.2f}{s.risk:>8}"
        )

    qp_terms = [f"({s.grade_point:.2f} × {s.credit_hours:.1f})" for s in student.subjects]
    total_qp = sum(s.grade_point * s.credit_hours for s in student.subjects)

    out += [
        thin,
        "HOW YOUR SEMESTER GPA (SGPA) IS CALCULATED:",
        "  Formula: SGPA = Total Quality Points ÷ Total Attempted Credit Hours",
        f"  1. Quality Points per Course : {' + '.join(qp_terms)}",
        f"  2. Total Quality Points      : {total_qp:.2f}",
        f"  3. Total Attempted Credits   : {student.total_credits:.1f}  (Earned Credits: {student.earned_credits:.1f})",
        f"  4. Final SGPA                : {total_qp:.2f} ÷ {student.total_credits:.1f} = {student.sgpa:.2f} / 4.00",
        f"  5. Overall Weighted Average  : {student.overall_percentage:.2f}%",
        f"  6. Academic Risk Standing    : {student.overall_risk}",
        line,
        "COMPLETE SUBJECT-BY-SUBJECT BREAKDOWN (ATTENDANCE, QUIZZES, MIDTERM & FINALS)",
        line,
    ]

    for idx, s in enumerate(student.subjects, 1):
        out.append(f"\n[{idx}] " + "\n".join(s.calculation_steps))
        out.append("")
        out.append("STEP 4: Final Exam Target Estimator (Based on your pre-final marks)")
        for label, req in s.targets.items():
            out.append(f"  * To get {label:<13}: {req}")
        out.append(line)

    return "\n".join(out)


def save_transcript_and_csv(student: StudentRecord) -> tuple[str, str]:
    os.makedirs(REPORT_DIR, exist_ok=True)
    safe_roll = "".join(ch if ch.isalnum() else "_" for ch in student.roll_no)
    txt_path = os.path.join(REPORT_DIR, f"{safe_roll}_transcript.txt")
    csv_path = os.path.join(REPORT_DIR, f"{safe_roll}_courses.csv")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(build_university_transcript(student))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Code", "Subject", "Category", "Credit Hours",
            "Attendance %", "Assignments/Quizzes %", "Midterm %",
            "Final Exam %", "Total %", "Grade", "Grade Point", "Risk"
        ])
        for s in student.subjects:
            writer.writerow([
                s.code, s.name, s.category, s.credit_hours,
                s.percentages["Attendance"],
                s.percentages["Assignments & Quizzes"],
                s.percentages["Midterm"],
                s.percentages["Final Exam"],
                s.total_percentage, s.grade, s.grade_point, s.risk
            ])

    return txt_path, csv_path


def build_university_figure(student: StudentRecord) -> Figure:
    fig = Figure(figsize=(9.5, 5.2), dpi=100, facecolor="#f8fafc")

    if not student.subjects:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Add subjects to visualize semester analytics",
                ha="center", va="center", fontsize=12, color="#64748b")
        ax.axis("off")
        return fig

    labels = [f"{s.code}\n({s.category[0]})" for s in student.subjects]
    totals = [s.total_percentage for s in student.subjects]
    finals = [s.final_percentage for s in student.subjects]

    ax1 = fig.add_subplot(121)
    x = range(len(labels))
    width = 0.36
    b1 = ax1.bar([i - width/2 for i in x], totals, width, label="Overall %", color="#1e3a8a")
    b2 = ax1.bar([i + width/2 for i in x], finals, width, label="Final Exam %", color="#0ea5e9")

    ax1.axhline(50, color="#dc2626", linestyle="--", linewidth=1.2, label="50% Final Pass Rule")
    ax1.set_ylim(0, 112)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_title("Course Overall % vs. Final Exam %", fontsize=10, fontweight="bold", color="#0f172a")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.bar_label(b1, fmt="%.0f", padding=2, fontsize=8)
    ax1.bar_label(b2, fmt="%.0f", padding=2, fontsize=8)

    ax2 = fig.add_subplot(122)
    major_qp = sum(s.grade_point * s.credit_hours for s in student.subjects if s.category == "Major")
    minor_qp = sum(s.grade_point * s.credit_hours for s in student.subjects if s.category == "Minor")
    max_major_qp = sum(4.0 * s.credit_hours for s in student.subjects if s.category == "Major")
    max_minor_qp = sum(4.0 * s.credit_hours for s in student.subjects if s.category == "Minor")

    cats = ["Major Courses", "Minor Courses"]
    earned = [major_qp, minor_qp]
    possible = [max_major_qp, max_minor_qp]

    ax2.bar(cats, possible, width=0.45, color="#e2e8f0", label="Max Quality Points")
    b3 = ax2.bar(cats, earned, width=0.45, color=["#2563eb", "#10b981"], label="Earned Quality Points")
    ax2.bar_label(b3, fmt="%.1f", padding=3, fontsize=9)
    ax2.set_ylim(0, max(possible + [4]) * 1.2)
    ax2.set_title(f"Quality Points by Track (SGPA: {student.sgpa:.2f})", fontsize=10, fontweight="bold", color="#0f172a")
    ax2.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        f"{student.name} ({student.roll_no})  |  SGPA: {student.sgpa:.2f}  |  Overall Risk: {student.overall_risk}",
        fontsize=11, fontweight="bold", color="#1e293b"
    )
    fig.tight_layout()
    return fig