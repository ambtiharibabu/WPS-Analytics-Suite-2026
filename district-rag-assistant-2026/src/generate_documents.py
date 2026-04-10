"""
generate_documents.py
Generates 60 synthetic K-12 district documents — no student PII anywhere.
Run: python src/generate_documents.py
Output: 60 .txt files in data/documents/
"""

import os
import random
from faker import Faker

fake = Faker()
random.seed(42)  # makes output reproducible — same files every run

OUTPUT_DIR = "data/documents"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── shared vocabulary pools ──────────────────────────────────────────────────
SUBJECTS      = ["Mathematics", "English Language Arts", "Science", "Social Studies",
                 "Physical Education", "Visual Arts", "Computer Science", "Spanish"]
GRADE_BANDS   = ["K-2", "3-5", "6-8", "9-12"]
PROGRAMS      = ["STEM Academy", "Dual Language Program", "Advanced Placement",
                 "Career & Technical Education", "Special Education Support Services",
                 "After-School Tutoring", "Early Childhood Education", "ESOL Program",
                 "Gifted & Talented", "Summer Bridge Program"]
PATHWAYS      = ["General Diploma", "College Preparatory", "Career & Technical",
                 "International Baccalaureate", "Honors Track"]
OUTCOMES      = ["exceeded targets", "met targets", "partially met targets",
                 "did not meet targets"]
RECOMMENDATIONS = [
    "Expand program enrollment by 15% next academic year.",
    "Increase professional development hours for instructors.",
    "Pilot additional support sessions for struggling participants.",
    "Review assessment alignment with state standards.",
    "Allocate supplemental budget for materials and resources.",
    "Collect quarterly feedback from program participants.",
    "Benchmark against peer districts using state data portal.",
]

# ── Template 1: Assessment Rubric (20 files) ─────────────────────────────────
def make_assessment_rubric(i):
    subject    = random.choice(SUBJECTS)
    grade_band = random.choice(GRADE_BANDS)
    year       = random.randint(2021, 2025)
    version    = random.randint(1, 4)
    cutoff_4   = random.randint(88, 95)
    cutoff_3   = random.randint(74, 87)
    cutoff_2   = random.randint(60, 73)

    return f"""WICHITA PUBLIC SCHOOLS — ASSESSMENT RUBRIC
Document ID: AR-{i:03d}
Subject: {subject}
Grade Band: {grade_band}
Academic Year: {year}-{year+1}
Version: {version}.0
Approved By: {fake.name()}, Director of Curriculum
Approval Date: {fake.date_between(start_date='-3y', end_date='today')}

---
PURPOSE
This rubric defines scoring criteria for {subject} assessments administered
to students in grades {grade_band} during the {year}-{year+1} academic year.
All assessments are aligned to Kansas State Standards.

---
SCORING LEVELS
Level 4 — Advanced:        {cutoff_4}–100  — Student demonstrates mastery and
    applies concepts independently in novel contexts.
Level 3 — Proficient:      {cutoff_3}–{cutoff_4-1}  — Student meets grade-level
    expectations consistently.
Level 2 — Developing:      {cutoff_2}–{cutoff_3-1}  — Student shows partial
    understanding; requires guided support.
Level 1 — Beginning:       Below {cutoff_2}        — Student requires intensive
    intervention and reteaching.

---
ASSESSMENT COMPONENTS
1. Formative Assessments   — 30% of overall score
   Administered weekly; scored by classroom teacher using this rubric.
2. Summative Assessment    — 50% of overall score
   End-of-unit exam; scored by department lead and verified by curriculum office.
3. Performance Task        — 20% of overall score
   Project-based demonstration; scored using attached performance task checklist.

---
CRITERIA DETAILS — {subject.upper()}
Criterion A: Content Knowledge
    4: Demonstrates comprehensive understanding of all {subject} standards
       for grade band {grade_band}.
    3: Demonstrates solid understanding of most {subject} standards.
    2: Demonstrates partial understanding; gaps in key concept areas.
    1: Demonstrates limited understanding; significant gaps present.

Criterion B: Application & Problem Solving
    4: Applies concepts to unfamiliar problems accurately and independently.
    3: Applies concepts to familiar problem types with minor errors.
    2: Attempts application; requires prompting or makes significant errors.
    1: Unable to apply concepts without direct teacher guidance.

Criterion C: Communication of Reasoning
    4: Clearly and precisely explains reasoning using appropriate vocabulary.
    3: Explains reasoning adequately; minor clarity issues.
    2: Provides incomplete or unclear explanation of reasoning.
    1: Unable to explain reasoning or explanation is missing.

---
REPORTING
Results are aggregated at the classroom and school level only.
No individual student scores are retained in this document.
Department chairs review aggregate data quarterly.

Rubric Revision Schedule: Annual review each June.
Next Review Date: June {year+1}
Contact: {fake.name()}, Assessment Coordinator, ext. {fake.numerify('####')}
"""

# ── Template 2: Graduation Requirement Policy Memo (20 files) ────────────────
def make_graduation_policy(i):
    pathway    = random.choice(PATHWAYS)
    year       = random.randint(2021, 2025)
    credits    = random.randint(22, 28)
    math_cr    = random.randint(3, 4)
    ela_cr     = random.randint(3, 4)
    sci_cr     = random.randint(2, 3)
    ss_cr      = random.randint(2, 3)
    elective   = credits - math_cr - ela_cr - sci_cr - ss_cr - 2

    return f"""WICHITA PUBLIC SCHOOLS — GRADUATION REQUIREMENTS POLICY MEMO
Document ID: GP-{i:03d}
Pathway: {pathway}
Effective Year: {year}-{year+1}
Issued By: {fake.name()}, Assistant Superintendent for Secondary Education
Issue Date: {fake.date_between(start_date='-3y', end_date='today')}
Replaces: GP-{i:03d} Version {random.randint(1,3)}.0

---
PURPOSE
This memo outlines the credit requirements and graduation conditions for
students enrolled in the {pathway} pathway, effective for the {year}-{year+1}
cohort and subsequent cohorts until further notice.

---
TOTAL CREDIT REQUIREMENT: {credits} CREDITS

REQUIRED COURSE AREAS:
  Mathematics                  {math_cr} credits
    (including Algebra I or equivalent)
  English Language Arts        {ela_cr} credits
  Science                      {sci_cr} credits
    (including one lab science)
  Social Studies               {ss_cr} credits
    (including U.S. History and Government)
  Physical Education / Health  1 credit
  Fine Arts or CTE             1 credit
  Electives                    {elective} credits

---
ADDITIONAL REQUIREMENTS — {pathway.upper()} PATHWAY
{"- Minimum 3.0 GPA for course completion in core subject areas." if "College" in pathway or "Honors" in pathway or "IB" in pathway else "- Minimum 2.0 GPA for course completion in core subject areas."}
{"- Completion of at least two AP or IB courses." if "Advanced" in pathway or "IB" in pathway else "- Completion of one approved capstone project or senior seminar."}
{"- Community service: 40 hours documented by senior year." if random.random() > 0.5 else "- Portfolio submission required in senior year."}
- State assessment participation as required by Kansas statute.
- Attendance: No more than {random.randint(8,15)} unexcused absences per semester.

---
WAIVER PROVISIONS
Students may petition for credit waivers under the following conditions:
1. Transfer Credit: Credits earned at accredited institutions accepted on
   case-by-case basis reviewed by the Registrar's Office.
2. Dual Enrollment: College coursework completed while enrolled in high school
   may substitute for up to {random.randint(2,4)} elective credits.
3. Medical Waiver: Students with documented medical conditions may petition
   for modified PE requirements through the Special Services office.

---
APPEAL PROCESS
Families may appeal credit decisions within 30 days of the end of each
semester. Appeals are reviewed by the Academic Review Committee.
Contact: {fake.name()}, Registrar, ext. {fake.numerify('####')}

Next Policy Review: June {year+1}
Board Approval Reference: Resolution {fake.numerify('####')}-{year}
"""

# ── Template 3: Annual Program Evaluation Summary (20 files) ─────────────────
def make_program_evaluation(i):
    program    = random.choice(PROGRAMS)
    year       = random.randint(2021, 2025)
    enrollment = random.randint(80, 600)
    outcome    = random.choice(OUTCOMES)
    budget     = random.randint(40000, 250000)
    rec1, rec2 = random.sample(RECOMMENDATIONS, 2)

    return f"""WICHITA PUBLIC SCHOOLS — ANNUAL PROGRAM EVALUATION SUMMARY
Document ID: PE-{i:03d}
Program: {program}
Academic Year: {year}-{year+1}
Evaluator: {fake.name()}, Program Evaluation Office
Report Date: {fake.date_between(start_date='-2y', end_date='today')}

---
EXECUTIVE SUMMARY
The {program} served {enrollment} participants during the {year}-{year+1}
academic year. Overall, the program {outcome} based on the district's
established performance benchmarks. This report summarizes program
activities, outcomes, budget utilization, and recommendations for the
upcoming academic year.

---
PROGRAM OVERVIEW
Description: {program} is designed to provide targeted academic and
developmental support aligned with district strategic priorities.
Program Lead: {fake.name()}
Program Sites: {random.randint(2, 8)} school locations across the district
Budget Allocated: ${budget:,}
Budget Utilized: ${int(budget * random.uniform(0.78, 0.99)):,}

---
PERFORMANCE OUTCOMES
Benchmark 1 — Participation Rate
  Target: 85% of enrolled participants complete the program.
  Actual: {random.randint(72, 97)}%
  Status: {"Met" if random.random() > 0.4 else "Not Met"}

Benchmark 2 — Academic Progress
  Target: 70% of participants demonstrate measurable academic growth.
  Actual: {random.randint(58, 89)}%
  Status: {"Met" if random.random() > 0.35 else "Not Met"}

Benchmark 3 — Stakeholder Satisfaction
  Target: 80% of surveyed stakeholders rate program as effective or better.
  Actual: {random.randint(65, 95)}%
  Status: {"Met" if random.random() > 0.3 else "Not Met"}

---
KEY FINDINGS
1. Staffing: {random.choice(["Fully staffed throughout the year.",
   "Experienced mid-year turnover in two program sites.",
   "Recruitment challenges delayed program launch by three weeks."])}
2. Resources: {random.choice(["Materials and technology were adequate.",
   "Technology infrastructure needs upgrading at two sites.",
   "Additional materials were procured mid-year from supplemental funds."])}
3. Community Engagement: {random.choice(["Family engagement events exceeded prior year attendance.",
   "Attendance at community events remained below target.",
   "New partnership with local nonprofit strengthened outreach efforts."])}

---
RECOMMENDATIONS FOR {year+1}-{year+2}
1. {rec1}
2. {rec2}

---
APPROVAL
Reviewed By: {fake.name()}, Deputy Superintendent
Review Date: {fake.date_between(start_date='-6m', end_date='today')}
Distribution: Superintendent's Cabinet, Board of Education (summary only)

Note: Aggregate data only. No individual student or staff PII included.
"""

# ── Generate all 60 files ────────────────────────────────────────────────────
print("Generating documents...")

for i in range(1, 21):
    fname = os.path.join(OUTPUT_DIR, f"assessment_rubric_{i:03d}.txt")
    with open(fname, "w") as f:
        f.write(make_assessment_rubric(i))

for i in range(1, 21):
    fname = os.path.join(OUTPUT_DIR, f"graduation_policy_{i:03d}.txt")
    with open(fname, "w") as f:
        f.write(make_graduation_policy(i))

for i in range(1, 21):
    fname = os.path.join(OUTPUT_DIR, f"program_evaluation_{i:03d}.txt")
    with open(fname, "w") as f:
        f.write(make_program_evaluation(i))

files = os.listdir(OUTPUT_DIR)
print(f"✅ Done — {len(files)} documents created in {OUTPUT_DIR}/")
print(f"   AR: {sum(1 for f in files if f.startswith('assessment'))} files")
print(f"   GP: {sum(1 for f in files if f.startswith('graduation'))} files")
print(f"   PE: {sum(1 for f in files if f.startswith('program'))} files")
