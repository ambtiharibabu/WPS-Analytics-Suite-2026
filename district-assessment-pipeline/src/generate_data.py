import pandas as pd
import numpy as np
from faker import Faker
import random
import os

fake = Faker()
np.random.seed(42)          # makes results repeatable every run
random.seed(42)

# ── CONFIG ──────────────────────────────────────────────────────────────────
N_ASSESS    = 1500          # rows in assessments table
N_ATTEND    = 1000          # rows in attendance table
N_DEMO      = 800           # rows in demographics table
N_STUDENTS  = 600           # real student universe
N_SCHOOLS   = 8             # number of schools in the district
SUBJECTS    = ['Math', 'Reading', 'Science', 'Writing']
GRADES      = [3, 4, 5, 6, 7, 8]
ETHNICITIES = ['Hispanic', 'White', 'Black', 'Asian', 'Two or More']
ABSENCE_REASONS = ['Illness', 'Family', 'Unknown', 'Vacation', None]

# ── STUDENT + SCHOOL ID POOLS ────────────────────────────────────────────────
student_ids = [f"STU{str(i).zfill(4)}" for i in range(1, N_STUDENTS + 1)]
school_ids  = [f"SCH{str(i).zfill(2)}"  for i in range(1, N_SCHOOLS + 1)]

# ── TABLE 1: ASSESSMENTS ─────────────────────────────────────────────────────
# 1,500 rows | ~8% nulls | ~3% duplicates

def make_assessments():
    rows = []
    for _ in range(N_ASSESS):
        rows.append({
            'student_id':      random.choice(student_ids),
            'school_id':       random.choice(school_ids),
            'grade_level':     random.choice(GRADES),
            'subject':         random.choice(SUBJECTS),
            'assessment_date': fake.date_between(start_date='-1y', end_date='today'),
            'score':           round(random.gauss(68, 15), 1),   # bell curve ~68 avg
            'pass_fail':       random.choice(['Pass', 'Fail'])
        })

    df = pd.DataFrame(rows)

    # Inject ~8% nulls randomly across score and pass_fail columns
    null_mask_score = np.random.random(len(df)) < 0.08
    null_mask_pf    = np.random.random(len(df)) < 0.08
    df.loc[null_mask_score, 'score']     = np.nan
    df.loc[null_mask_pf,    'pass_fail'] = np.nan

    # Inject ~3% duplicate rows (copy random rows and append)
    n_dupes = int(N_ASSESS * 0.03)
    dupes = df.sample(n=n_dupes, random_state=1)
    df = pd.concat([df, dupes], ignore_index=True)

    return df

# ── TABLE 2: ATTENDANCE ──────────────────────────────────────────────────────
# 1,000 rows | ~5% nulls in absence_reason

def make_attendance():
    rows = []
    for _ in range(N_ATTEND):
        present = random.random() > 0.12          # ~12% absent rate
        rows.append({
            'student_id':     random.choice(student_ids),
            'school_id':      random.choice(school_ids),
            'date':           fake.date_between(start_date='-1y', end_date='today'),
            'present_flag':   int(present),
            'absence_reason': None if present else random.choice(ABSENCE_REASONS)
        })

    df = pd.DataFrame(rows)

    # Inject ~5% nulls in absence_reason even for absent rows
    null_mask = np.random.random(len(df)) < 0.05
    df.loc[null_mask, 'absence_reason'] = np.nan

    return df

# ── TABLE 3: DEMOGRAPHICS ────────────────────────────────────────────────────
# 800 rows | intentional mismatched IDs (100 fake IDs not in student_ids pool)
# This simulates real-world join errors — some students in demographics
# won't match any record in assessments

def make_demographics():
    # 700 real IDs + 100 fake IDs that won't match
    real_sample  = random.sample(student_ids, 500)
    fake_ids     = [f"STU{str(i).zfill(4)}" for i in range(9000, 9100)]  # IDs that don't exist
    all_ids      = real_sample + fake_ids
    random.shuffle(all_ids)

    rows = []
    for sid in all_ids:
        rows.append({
            'student_id':        sid,
            'ethnicity':         random.choice(ETHNICITIES),
            'gender':            random.choice(['M', 'F', 'Non-binary']),
            'free_lunch_eligible': random.choice([0, 1]),
            'special_ed_flag':   random.choice([0, 0, 0, 1]),   # ~25% special ed
            'grade_level':       random.choice(GRADES)
        })

    return pd.DataFrame(rows)

# ── GENERATE + SAVE ──────────────────────────────────────────────────────────
assess_df = make_assessments()
attend_df = make_attendance()
demo_df   = make_demographics()

os.makedirs('data/raw', exist_ok=True)

assess_df.to_csv('data/raw/assessments.csv',  index=False)
attend_df.to_csv('data/raw/attendance.csv',   index=False)
demo_df.to_csv(  'data/raw/demographics.csv', index=False)

# ── SUMMARY PRINT ────────────────────────────────────────────────────────────
print("=== DATA GENERATION COMPLETE ===")
print(f"Assessments : {len(assess_df):,} rows | Nulls in score: {assess_df['score'].isna().sum()} | Nulls in pass_fail: {assess_df['pass_fail'].isna().sum()}")
print(f"Attendance  : {len(attend_df):,} rows | Nulls in absence_reason: {attend_df['absence_reason'].isna().sum()}")
print(f"Demographics: {len(demo_df):,} rows | Mismatched IDs (won't join): 100")
print("\nFiles saved to data/raw/")