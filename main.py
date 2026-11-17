import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from grade_system import COURSE_WEIGHTS, MAX_CREDIT_HOURS, Subject, StudentRecord
from calculations import validate_component_pair, evaluate_subject, evaluate_semester
from reports import build_university_transcript, save_transcript_and_csv, build_university_figure

RISK_COLORS = {"LOW": "#15803d", "MEDIUM": "#b45309", "HIGH": "#b91c1c"}


class UniversityPortalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("University Academic Standing, SGPA & Final Pass Estimator")
        self.geometry("1240x740")
        self.minsize(1100, 680)
        self.configure(bg="#f1f5f9")

        self.subjects: list[Subject] = []
        self.student_record: StudentRecord | None = None

        self._setup_styles()
        self._init_vars()
        self._build_header()
        self._build_body()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f1f5f9")
        style.configure("Card.TLabelframe", background="#ffffff", borderwidth=1, relief="solid")
        style.configure("Card.TLabelframe.Label", background="#ffffff", foreground="#1e3a8a",
                        font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background="#ffffff", foreground="#1e293b", font=("Segoe UI", 9))
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), padding=6)
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#e2e8f0")

    def _init_vars(self):
        self.name_var = tk.StringVar(value="Ali Raza")
        self.roll_var = tk.StringVar(value="CS-2026-042")
        self.dept_var = tk.StringVar(value="BS Artificial Intelligence")
        self.sem_var = tk.StringVar(value="Fall 2026")

        self.code_var = tk.StringVar()
        self.subj_var = tk.StringVar()
        self.cat_var = tk.StringVar(value="Major")
        self.ch_var = tk.StringVar(value="3.0")

        self.mark_inputs = {}
        default_totals = {
            "Attendance": "100",
            "Assignments & Quizzes": "20",
            "Midterm": "30",
            "Final Exam": "50",
        }
        for comp in COURSE_WEIGHTS:
            self.mark_inputs[comp] = (
                tk.StringVar(),
                tk.StringVar(value=default_totals[comp]),
            )

    def _build_header(self):
        banner = tk.Frame(self, bg="#1e3a8a", height=58)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text="UNIVERSITY GRADE ESTIMATOR & ACADEMIC RISK PORTAL",
            bg="#1e3a8a", fg="#ffffff", font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=18)

        tk.Label(
            banner,
            text="Max 3.0 Credit Hours / Course  |  50% Final Exam Pass Rule  |  4.00 SGPA Scale",
            bg="#1e3a8a", fg="#bfdbfe", font=("Segoe UI", 9, "bold")
        ).pack(side="right", padx=18)

    def _build_body(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=12, pady=10)

        left = ttk.Frame(container, width=395)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        self._build_student_card(left)
        self._build_subject_card(left)

        right = ttk.Frame(container)
        right.pack(side="right", fill="both", expand=True)

        self._build_kpi_bar(right)
        self._build_course_table(right)
        self._build_notebook(right)

    def _build_student_card(self, parent):
        card = ttk.LabelFrame(parent, text=" 1. Student Profile ", style="Card.TLabelframe", padding=10)
        card.pack(fill="x", pady=(0, 10))

        fields = [
            ("Student Name:", self.name_var, "Roll No:", self.roll_var),
            ("Department:", self.dept_var, "Semester:", self.sem_var),
        ]
        for r, (l1, v1, l2, v2) in enumerate(fields):
            ttk.Label(card, text=l1).grid(row=r, column=0, sticky="w", pady=3)
            ttk.Entry(card, textvariable=v1, width=18).grid(row=r, column=1, padx=(4, 10), pady=3)
            ttk.Label(card, text=l2).grid(row=r, column=2, sticky="w", pady=3)
            ttk.Entry(card, textvariable=v2, width=13).grid(row=r, column=3, padx=(4, 0), pady=3)

    def _build_subject_card(self, parent):
        card = ttk.LabelFrame(parent, text=" 2. Add Subject (Major / Minor) & Marks ", style="Card.TLabelframe", padding=10)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Course Code:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(card, textvariable=self.code_var, width=14).grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(card, text="Category:").grid(row=0, column=2, sticky="w", pady=3)
        cat_box = ttk.Combobox(card, textvariable=self.cat_var, values=["Major", "Minor"], state="readonly", width=10)
        cat_box.grid(row=0, column=3, sticky="w", pady=3)

        ttk.Label(card, text="Subject Name:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(card, textvariable=self.subj_var, width=21).grid(row=1, column=1, columnspan=2, sticky="we", pady=3)

        ttk.Label(card, text="Credits (Max 3):").grid(row=1, column=2, sticky="e", padx=(4, 4), pady=3)
        ch_box = ttk.Combobox(card, textvariable=self.ch_var, values=["3.0", "2.0", "1.0"], width=7)
        ch_box.grid(row=1, column=3, sticky="w", pady=3)

        ttk.Separator(card).grid(row=2, column=0, columnspan=4, sticky="ew", pady=8)

        ttk.Label(card, text="Assessment Component", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Label(card, text="Obtained", font=("Segoe UI", 9, "bold")).grid(row=3, column=2, sticky="w")
        ttk.Label(card, text="Full Marks", font=("Segoe UI", 9, "bold")).grid(row=3, column=3, sticky="w")

        row = 4
        for comp, weight in COURSE_WEIGHTS.items():
            obt_var, tot_var = self.mark_inputs[comp]
            ttk.Label(card, text=f"{comp} ({weight*100:.0f}%)").grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
            ttk.Entry(card, textvariable=obt_var, width=9).grid(row=row, column=2, sticky="w", pady=4)
            ttk.Entry(card, textvariable=tot_var, width=9).grid(row=row, column=3, sticky="w", pady=4)
            row += 1

        btn_frame = tk.Frame(card, bg="#ffffff")
        btn_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(12, 4))

        ttk.Button(btn_frame, text="+ Add Subject & Show Calculation", style="Primary.TButton",
                   command=self.add_subject).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Load Demo Semester", command=self.load_demo_data).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Export Transcript & CSV", command=self.export_files).pack(fill="x", pady=2)

    def _build_kpi_bar(self, parent):
        kpi_frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid", padx=12, pady=8)
        kpi_frame.pack(fill="x", pady=(0, 8))

        self.kpi_sgpa = tk.Label(kpi_frame, text="SGPA: 0.00 / 4.00", bg="#ffffff", fg="#1e3a8a", font=("Segoe UI", 12, "bold"))
        self.kpi_sgpa.pack(side="left", padx=(0, 22))

        self.kpi_avg = tk.Label(kpi_frame, text="Weighted Avg: 0.0%", bg="#ffffff", fg="#0f172a", font=("Segoe UI", 11, "bold"))
        self.kpi_avg.pack(side="left", padx=(0, 22))

        self.kpi_credits = tk.Label(kpi_frame, text="Credits: 0.0 / 0.0", bg="#ffffff", fg="#334155", font=("Segoe UI", 10, "bold"))
        self.kpi_credits.pack(side="left", padx=(0, 22))

        self.kpi_risk = tk.Label(kpi_frame, text="Standing: LOW RISK", bg="#ffffff", fg="#15803d", font=("Segoe UI", 11, "bold"))
        self.kpi_risk.pack(side="right")

    def _build_course_table(self, parent):
        table_card = ttk.LabelFrame(parent, text=" Added Semester Courses ", style="Card.TLabelframe", padding=6)
        table_card.pack(fill="x", pady=(0, 8))

        cols = ("code", "name", "cat", "ch", "final", "total", "grade", "gp", "rule", "risk")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=5)

        headers = {
            "code": ("Code", 75), "name": ("Subject Name", 185), "cat": ("Track", 65),
            "ch": ("Credits", 60), "final": ("Final %", 70), "total": ("Total %", 70),
            "grade": ("Grade", 55), "gp": ("GP", 55), "rule": ("50% Final Rule", 105),
            "risk": ("Risk", 70),
        }
        for col, (title, width) in headers.items():
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w")

        self.tree.pack(side="left", fill="x", expand=True)

        side_btns = tk.Frame(table_card, bg="#ffffff")
        side_btns.pack(side="right", fill="y", padx=(6, 0))
        ttk.Button(side_btns, text="Remove Selected", command=self.remove_selected).pack(fill="x", pady=2)
        ttk.Button(side_btns, text="Clear All", command=self.clear_all).pack(fill="x", pady=2)

    def _build_notebook(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        text_container = ttk.Frame(self.notebook)
        y_scroll = ttk.Scrollbar(text_container, orient="vertical")
        x_scroll = ttk.Scrollbar(text_container, orient="horizontal")

        self.calc_text = tk.Text(
            text_container,
            font=("Consolas", 10),
            wrap="none",
            bg="#ffffff",
            fg="#0f172a",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        y_scroll.config(command=self.calc_text.yview)
        x_scroll.config(command=self.calc_text.xview)

        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.calc_text.pack(side="left", fill="both", expand=True)

        self.chart_frame = ttk.Frame(self.notebook)

        self.notebook.add(text_container, text="Step-by-Step Calculations & Transcript")
        self.notebook.add(self.chart_frame, text="Visual Analytics")

    def add_subject(self):
        code = self.code_var.get().strip().upper()
        name = self.subj_var.get().strip()
        category = self.cat_var.get()

        if not code or not name:
            messagebox.showwarning("Missing Course Details", "Enter both Course Code and Subject Name.")
            return

        try:
            ch = float(self.ch_var.get().strip())
            if not (0.5 <= ch <= MAX_CREDIT_HOURS):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Credits", f"Credit hours must be between 0.5 and {MAX_CREDIT_HOURS:.1f}.")
            return

        components = {}
        try:
            for comp, (obt_v, tot_v) in self.mark_inputs.items():
                components[comp] = validate_component_pair(comp, obt_v.get(), tot_v.get())
        except ValueError as err:
            messagebox.showerror("Invalid Marks", str(err))
            return

        subj = Subject(name=name, code=code, category=category, credit_hours=ch, components=components)
        evaluate_subject(subj)
        self.subjects.append(subj)

        self.code_var.set("")
        self.subj_var.set("")
        for obt_v, _ in self.mark_inputs.values():
            obt_v.set("")

        self._refresh_all()

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        self.subjects.pop(idx)
        self._refresh_all()

    def clear_all(self):
        self.subjects.clear()
        self._refresh_all()

    def load_demo_data(self):
        self.subjects.clear()
        demo_courses = [
            ("AI-301", "Machine Learning", "Major", 3.0, {
                "Attendance": (92, 100), "Assignments & Quizzes": (17, 20),
                "Midterm": (24, 30), "Final Exam": (39, 50)
            }),
            ("CS-305", "Data Structures", "Major", 3.0, {
                "Attendance": (85, 100), "Assignments & Quizzes": (16, 20),
                "Midterm": (25, 30), "Final Exam": (22, 50)
            }),
            ("MT-202", "Linear Algebra", "Minor", 3.0, {
                "Attendance": (95, 100), "Assignments & Quizzes": (18, 20),
                "Midterm": (26, 30), "Final Exam": (43, 50)
            }),
            ("HU-104", "Technical Writing", "Minor", 2.0, {
                "Attendance": (72, 100), "Assignments & Quizzes": (14, 20),
                "Midterm": (18, 30), "Final Exam": (28, 50)
            }),
        ]
        for code, name, cat, ch, comps in demo_courses:
            s = Subject(name=name, code=code, category=cat, credit_hours=ch, components=comps)
            evaluate_subject(s)
            self.subjects.append(s)

        self._refresh_all()

    def _refresh_all(self):
        record = StudentRecord(
            name=self.name_var.get().strip() or "Unnamed Student",
            roll_no=self.roll_var.get().strip() or "N/A",
            department=self.dept_var.get().strip() or "General",
            semester=self.sem_var.get().strip() or "Current",
            subjects=self.subjects,
        )
        evaluate_semester(record)
        self.student_record = record

        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in self.subjects:
            rule_txt = "PASSED" if s.passed_final_rule else "FAILED (<50%)"
            self.tree.insert("", "end", values=(
                s.code, s.name, s.category, f"{s.credit_hours:.1f}",
                f"{s.final_percentage:.1f}%", f"{s.total_percentage:.1f}%",
                s.grade, f"{s.grade_point:.2f}", rule_txt, s.risk
            ))

        self.kpi_sgpa.config(text=f"SGPA: {record.sgpa:.2f} / 4.00")
        self.kpi_avg.config(text=f"Weighted Avg: {record.overall_percentage:.1f}%")
        self.kpi_credits.config(text=f"Credits: {record.earned_credits:.1f} / {record.total_credits:.1f}")
        self.kpi_risk.config(text=f"Standing: {record.overall_risk} RISK", fg=RISK_COLORS[record.overall_risk])

        self.calc_text.config(state="normal")
        self.calc_text.delete("1.0", "end")
        if self.subjects:
            self.calc_text.insert("1.0", build_university_transcript(record))
        else:
            self.calc_text.insert("1.0", "No courses added yet. Add Major/Minor courses on the left or click 'Load Demo Semester'.")
        self.calc_text.config(state="disabled")

        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(build_university_figure(record), master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_files(self):
        if not self.subjects or self.student_record is None:
            messagebox.showinfo("Nothing to Export", "Add at least one subject first.")
            return
        txt_path, csv_path = save_transcript_and_csv(self.student_record)
        messagebox.showinfo("Export Complete", f"Saved Transcript & CSV:\n\n1. {txt_path}\n2. {csv_path}")


if __name__ == "__main__":
    app = UniversityPortalApp()
    app.load_demo_data()
    app.mainloop()