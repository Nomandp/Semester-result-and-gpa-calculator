from grade_system import (
    COURSE_WEIGHTS,
    FINAL_PASS_THRESHOLD,
    Subject,
    StudentRecord,
    get_grade_and_gp,
)


def validate_component_pair(label: str, obt_str: str, tot_str: str) -> tuple[float, float]:
    try:
        obt = float(obt_str.strip())
        tot = float(tot_str.strip())
    except ValueError:
        raise ValueError(f"{label}: Obtained and Full marks must be valid numbers.")

    if tot <= 0:
        raise ValueError(f"{label}: Full marks must be greater than 0.")
    if not (0 <= obt <= tot):
        raise ValueError(f"{label}: Obtained marks ({obt}) must be between 0 and {tot}.")
    return obt, tot


def evaluate_subject(subject: Subject) -> Subject:
    steps = [
        f"COURSE: {subject.code} - {subject.name} ({subject.category} Subject | {subject.credit_hours:.1f} Credit Hours)",
        "-" * 86,
        "STEP 1: Convert Each Component's Marks into Percentage & Weighted Score",
        "        Formula: Percentage = (Obtained ÷ Full Marks) × 100",
        "                 Weighted Marks = Percentage × Component Weight",
        "",
    ]

    total_weighted = 0.0
    contrib_list = []

    for comp, weight in COURSE_WEIGHTS.items():
        obt, tot = subject.components[comp]
        pct = round((obt / tot) * 100.0, 2)
        contrib = round(pct * weight, 2)

        subject.percentages[comp] = pct
        subject.contributions[comp] = contrib
        total_weighted += contrib
        contrib_list.append(f"{contrib:.2f}")

        steps.append(f"  * {comp} (Weight: {weight * 100:.0f}%):")
        steps.append(f"      Marks Entered  : {obt:.1f} obtained out of {tot:.1f} full marks")
        steps.append(f"      Percentage     : ({obt:.1f} ÷ {tot:.1f}) × 100 = {pct:.2f}%")
        steps.append(f"      Weighted Score : {pct:.2f}% × {weight:.2f} = {contrib:.2f} marks")
        steps.append("")

    subject.total_percentage = round(total_weighted, 2)
    subject.final_percentage = subject.percentages["Final Exam"]

    steps.append("STEP 2: Add All Weighted Scores Together for Total Course Percentage")
    steps.append(f"  * Total = {' + '.join(contrib_list)} = {subject.total_percentage:.2f}%")
    steps.append("")

    grade, gp, passed_final = get_grade_and_gp(
        subject.total_percentage, subject.final_percentage
    )
    subject.grade = grade
    subject.grade_point = gp
    subject.passed_final_rule = passed_final

    final_obt, final_tot = subject.components["Final Exam"]
    min_final_needed = round(final_tot * (FINAL_PASS_THRESHOLD / 100.0), 1)

    steps.append("STEP 3: Check Mandatory 50% Final Exam Pass Rule & Assign Grade")
    if not passed_final:
        steps.append(f"  * Final Exam Score : {final_obt:.1f} / {final_tot:.1f} = {subject.final_percentage:.2f}%")
        steps.append(f"  * Required to Pass : At least {min_final_needed:.1f} / {final_tot:.1f} (50.0%) in Final Exam")
        steps.append(f"  * Result           : FAILED Final Exam Rule ({subject.final_percentage:.2f}% < 50.0%)")
        steps.append("  * Final Grade      : F (0.00 Grade Points) — even if total percentage is above 50%")
    else:
        steps.append(f"  * Final Exam Score : {final_obt:.1f} / {final_tot:.1f} = {subject.final_percentage:.2f}% (>= 50.0% PASSED)")
        steps.append(f"  * Overall Score    : {subject.total_percentage:.2f}%")
        steps.append(f"  * Final Grade      : {grade} ({gp:.2f} Grade Points)")
        steps.append(f"  * Quality Points   : {gp:.2f} GP × {subject.credit_hours:.1f} Credits = {gp * subject.credit_hours:.2f}")

    att_pct = subject.percentages["Attendance"]
    if not passed_final or subject.total_percentage < 50.0 or att_pct < 60.0:
        subject.risk = "HIGH"
    elif subject.total_percentage < 65.0 or att_pct < 75.0 or subject.final_percentage < 60.0:
        subject.risk = "MEDIUM"
    else:
        subject.risk = "LOW"

    pre_final_score = sum(
        subject.contributions[c] for c in COURSE_WEIGHTS if c != "Final Exam"
    )
    final_weight = COURSE_WEIGHTS["Final Exam"]
    targets = {}

    for cutoff, label, _ in [(85.0, "A (85%)", 4.0), (75.0, "B+ (75%)", 3.3), (65.0, "B- (65%)", 2.7), (50.0, "Pass D (50%)", 1.0)]:
        req_final_pct = max(FINAL_PASS_THRESHOLD, (cutoff - pre_final_score) / final_weight)
        req_final_marks = round((req_final_pct / 100.0) * final_tot, 1)
        if req_final_pct > 100.0:
            targets[label] = f"Not possible (needs > {final_tot:.0f}/{final_tot:.0f})"
        else:
            targets[label] = f"Need {req_final_marks:.1f} / {final_tot:.0f} ({req_final_pct:.1f}%)"

    subject.targets = targets
    subject.calculation_steps = steps
    return subject


def evaluate_semester(student: StudentRecord) -> StudentRecord:
    if not student.subjects:
        student.sgpa = 0.0
        student.overall_percentage = 0.0
        student.total_credits = 0.0
        student.earned_credits = 0.0
        student.overall_risk = "LOW"
        return student

    total_credits = sum(s.credit_hours for s in student.subjects)
    earned_credits = sum(s.credit_hours for s in student.subjects if s.grade != "F")
    quality_points = sum(s.grade_point * s.credit_hours for s in student.subjects)
    weighted_pct_sum = sum(s.total_percentage * s.credit_hours for s in student.subjects)

    student.total_credits = round(total_credits, 1)
    student.earned_credits = round(earned_credits, 1)
    student.sgpa = round(quality_points / total_credits, 2) if total_credits > 0 else 0.0
    student.overall_percentage = round(weighted_pct_sum / total_credits, 2) if total_credits > 0 else 0.0

    risks = [s.risk for s in student.subjects]
    if "HIGH" in risks or student.sgpa < 2.00:
        student.overall_risk = "HIGH"
    elif "MEDIUM" in risks or student.sgpa < 2.75:
        student.overall_risk = "MEDIUM"
    else:
        student.overall_risk = "LOW"

    return student