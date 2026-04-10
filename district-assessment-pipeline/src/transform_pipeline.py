import pandas as pd
import sqlite3
import os

# ── LOAD RAW CSVs ────────────────────────────────────────────────────────────
assess_df = pd.read_csv('data/raw/assessments.csv')
attend_df = pd.read_csv('data/raw/attendance.csv')
demo_df   = pd.read_csv('data/raw/demographics.csv')

# ── CREATE SQLITE DATABASE ───────────────────────────────────────────────────
# sqlite3.connect creates a .db file on disk if it doesn't exist
conn = sqlite3.connect('data/district.db')

# Load all 3 dataframes into the SQLite database as tables
assess_df.to_sql('assessments',  conn, if_exists='replace', index=False)
attend_df.to_sql('attendance',   conn, if_exists='replace', index=False)
demo_df.to_sql(  'demographics', conn, if_exists='replace', index=False)

print("Tables loaded into SQLite.")

# ── SQL JOIN: assessments LEFT JOIN demographics ──────────────────────────────
# LEFT JOIN keeps ALL rows from assessments even if no matching student in demographics
# Unmatched rows get NaN in the demographic columns — we log those below
query = """
    SELECT
        a.student_id,
        a.school_id,
        a.grade_level,
        a.subject,
        a.assessment_date,
        a.score,
        a.pass_fail,
        d.ethnicity,
        d.gender,
        d.free_lunch_eligible,
        d.special_ed_flag
    FROM assessments a
    LEFT JOIN demographics d
        ON a.student_id = d.student_id
"""

fact_df = pd.read_sql_query(query, conn)
conn.close()

print(f"Joined fact table: {len(fact_df):,} rows")

# ── LOG JOIN MISMATCHES ───────────────────────────────────────────────────────
# Rows where ethnicity is null = student had no matching demographics record
unmatched = fact_df['ethnicity'].isna().sum()
matched   = len(fact_df) - unmatched
print(f"Matched rows   : {matched:,}")
print(f"Unmatched rows : {unmatched:,}  (no demographics record found)")

# ── STEP 1 CLEANING: DROP DUPLICATES ─────────────────────────────────────────
before_dedup = len(fact_df)
# A true duplicate = same student, school, subject, date, and score
fact_df = fact_df.drop_duplicates(
    subset=['student_id', 'school_id', 'subject', 'assessment_date', 'score']
)
dupes_dropped = before_dedup - len(fact_df)
print(f"Duplicates dropped: {dupes_dropped}")

# ── STEP 2 CLEANING: HANDLE NULLS ────────────────────────────────────────────
# score: drop rows where score is null (can't analyze without a score)
before_null = len(fact_df)
fact_df = fact_df.dropna(subset=['score'])
score_nulls_dropped = before_null - len(fact_df)

# pass_fail: derive from score instead of dropping (score >= 60 = Pass)
fact_df['pass_fail'] = fact_df['score'].apply(lambda x: 'Pass' if x >= 60 else 'Fail')

# demographic nulls: keep rows, fill with 'Unknown' — don't lose assessment data
fact_df['ethnicity']  = fact_df['ethnicity'].fillna('Unknown')
fact_df['gender']     = fact_df['gender'].fillna('Unknown')
fact_df['free_lunch_eligible'] = fact_df['free_lunch_eligible'].fillna(0)
fact_df['special_ed_flag']     = fact_df['special_ed_flag'].fillna(0)

print(f"Null scores dropped: {score_nulls_dropped}")
print(f"pass_fail rebuilt from score for all rows")

# ── STEP 3: ADD DERIVED COLUMNS ───────────────────────────────────────────────
# at_risk_flag = 1 if score < 60 (failing threshold used by most districts)
fact_df['at_risk_flag'] = (fact_df['score'] < 60).astype(int)

# Standardize column names to snake_case (already are — confirming convention)
fact_df.columns = [c.lower().replace(' ', '_') for c in fact_df.columns]

# ── SAVE CLEANED FACT TABLE ───────────────────────────────────────────────────
os.makedirs('data/processed', exist_ok=True)
fact_df.to_csv('data/processed/fact_assessments.csv', index=False)

print(f"\nCleaned fact table saved: {len(fact_df):,} rows")
print(f"At-risk students flagged: {fact_df['at_risk_flag'].sum():,}")

# ── WRITE PIPELINE LOG ────────────────────────────────────────────────────────
os.makedirs('outputs', exist_ok=True)
with open('outputs/pipeline_log.txt', 'w') as log:
    log.write("=== DISTRICT ASSESSMENT PIPELINE LOG ===\n\n")
    log.write(f"RAW DATA LOADED:\n")
    log.write(f"  assessments : 1,545 rows\n")
    log.write(f"  attendance  : 1,000 rows\n")
    log.write(f"  demographics:   600 rows\n\n")
    log.write(f"JOIN RESULTS:\n")
    log.write(f"  Matched rows   : {matched:,}\n")
    log.write(f"  Unmatched rows : {unmatched:,} — demographics had 100 fake IDs\n\n")
    log.write(f"CLEANING DECISIONS:\n")
    log.write(f"  Duplicates dropped : {dupes_dropped} — exact match on student+school+subject+date+score\n")
    log.write(f"  Null scores dropped: {score_nulls_dropped} — cannot impute a test score\n")
    log.write(f"  pass_fail rebuilt  : derived from score >= 60 threshold\n")
    log.write(f"  Demographic nulls  : filled with 'Unknown'/0 — preserve assessment records\n\n")
    log.write(f"FINAL FACT TABLE:\n")
    log.write(f"  Total rows  : {len(fact_df):,}\n")
    log.write(f"  At-risk rows: {fact_df['at_risk_flag'].sum():,}\n")
    log.write(f"  Columns     : {list(fact_df.columns)}\n")

print("pipeline_log.txt written to outputs/")