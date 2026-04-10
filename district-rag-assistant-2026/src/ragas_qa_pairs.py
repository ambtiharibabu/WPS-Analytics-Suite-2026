"""
ragas_qa_pairs.py
20 synthetic QA pairs for evaluating the RAG pipeline.
Each pair has: question, ground_truth answer, and relevant document prefix.
"""

QA_PAIRS = [
    {
        "question": "What are the graduation credit requirements for the College Preparatory pathway?",
        "ground_truth": "The College Preparatory pathway requires between 22 and 28 total credits including Mathematics, English Language Arts, Science, Social Studies, Physical Education, Fine Arts or CTE, and Electives.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "What scoring levels are used in Mathematics assessment rubrics?",
        "ground_truth": "Mathematics assessment rubrics use four scoring levels: Level 4 Advanced, Level 3 Proficient, Level 2 Developing, and Level 1 Beginning.",
        "doc_type": "assessment_rubric",
    },
    {
        "question": "How did the STEM Academy perform against its benchmarks?",
        "ground_truth": "The STEM Academy program performance is evaluated against benchmarks including participation rate, academic progress, and stakeholder satisfaction targets.",
        "doc_type": "program_evaluation",
    },
    {
        "question": "What waiver provisions exist for graduation requirements?",
        "ground_truth": "Waiver provisions include transfer credit from accredited institutions, dual enrollment college coursework substituting for elective credits, and medical waivers for PE requirements.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "What is the assessment component weighting in rubrics?",
        "ground_truth": "Assessment components are weighted as follows: Formative Assessments 30%, Summative Assessment 50%, and Performance Task 20% of the overall score.",
        "doc_type": "assessment_rubric",
    },
    {
        "question": "What recommendations were made for district programs?",
        "ground_truth": "Recommendations include expanding program enrollment, increasing professional development hours, piloting additional support sessions, and reviewing assessment alignment with state standards.",
        "doc_type": "program_evaluation",
    },
    {
        "question": "What is the credit requirement for the International Baccalaureate pathway?",
        "ground_truth": "The International Baccalaureate pathway requires between 22 and 28 total credits with a minimum 3.0 GPA and completion of at least two IB courses.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "How are performance tasks scored in assessment rubrics?",
        "ground_truth": "Performance tasks account for 20% of the overall score and are scored using a performance task checklist attached to the rubric.",
        "doc_type": "assessment_rubric",
    },
    {
        "question": "What attendance requirements exist for graduation?",
        "ground_truth": "Graduation requirements include an attendance provision allowing no more than 8 to 15 unexcused absences per semester depending on the pathway.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "How is program budget utilization reported?",
        "ground_truth": "Program evaluation summaries report both budget allocated and budget utilized, typically showing utilization between 78% and 99% of allocated funds.",
        "doc_type": "program_evaluation",
    },
    {
        "question": "What criteria are used to evaluate student content knowledge in rubrics?",
        "ground_truth": "Criterion A Content Knowledge is scored on a 4-point scale: Level 4 demonstrates comprehensive understanding, Level 3 solid understanding, Level 2 partial understanding, Level 1 limited understanding.",
        "doc_type": "assessment_rubric",
    },
    {
        "question": "What community service requirements exist for graduation pathways?",
        "ground_truth": "Some graduation pathways require 40 hours of documented community service by senior year, while others require a portfolio submission instead.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "What is the stakeholder satisfaction benchmark for program evaluations?",
        "ground_truth": "The stakeholder satisfaction benchmark target is 80% of surveyed stakeholders rating the program as effective or better.",
        "doc_type": "program_evaluation",
    },
    {
        "question": "How are assessment results reported at the district level?",
        "ground_truth": "Assessment results are aggregated at the classroom and school level only. No individual student scores are retained in rubric documents.",
        "doc_type": "assessment_rubric",
    },
    {
        "question": "What is the dual enrollment credit substitution limit?",
        "ground_truth": "College coursework completed through dual enrollment may substitute for up to 2 to 4 elective credits toward graduation requirements.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "What is the academic progress benchmark for program evaluations?",
        "ground_truth": "The academic progress benchmark target is 70% of participants demonstrating measurable academic growth during the program year.",
        "doc_type": "program_evaluation",
    },
    {
        "question": "How often are assessment rubrics reviewed?",
        "ground_truth": "Assessment rubrics are reviewed annually each June according to the rubric revision schedule.",
        "doc_type": "assessment_rubric",
    },
    {
        "question": "What appeal process exists for graduation credit decisions?",
        "ground_truth": "Families may appeal credit decisions within 30 days of the end of each semester. Appeals are reviewed by the Academic Review Committee.",
        "doc_type": "graduation_policy",
    },
    {
        "question": "What staffing challenges are noted in program evaluations?",
        "ground_truth": "Program evaluations note staffing challenges including mid-year turnover at program sites and recruitment delays that postponed program launches.",
        "doc_type": "program_evaluation",
    },
    {
        "question": "What communication of reasoning criteria is used in rubrics?",
        "ground_truth": "Criterion C Communication of Reasoning scores Level 4 for clearly explaining reasoning with appropriate vocabulary, down to Level 1 for missing or unable to explain reasoning.",
        "doc_type": "assessment_rubric",
    },
]
