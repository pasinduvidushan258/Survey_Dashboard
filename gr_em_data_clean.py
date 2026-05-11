import pandas as pd
from duplicate_data import remove_survey_duplicates

# ==========================================
# GRADUATE EMPLOYABILITY — CLEANING MODULE
# ==========================================

IGNORE_COLUMNS = [
    # REDCap system fields
    'record_id',
    'redcap_survey_identifier',
    'graduate_employability_survey_timestamp',
    'graduate_employability_survey_complete',
    'response_id',

    # Conditional "other" text fields
    'fcms_other',
    'fct_other',
    'fhu_other',
    'fmed_other',
    'fsc_other',
    'fsosc_other',
    'other_comp_konwledge',
    'other_targets',
    'other_reason',
    'other_status',
    'other_sector',
    'other_aspects',
    'economic_sector_other',
    'other_finding_job',

    # Conditional fields only shown to unemployed respondents
    'reason_unemployment___1',
    'reason_unemployment___2',
    'reason_unemployment___3',
    'reason_unemployment___4',
    'reason_unemployment___5',
    'reason_unemployment___6',
    'expected_job',
    'reason_rejection',
    'reason_resign',
    'main_obstacles',

    # Conditional fields only shown to employed respondents
    'current_status_your_employment',
    'timing',
    'appointment_date',
    'organization',
    'employment_sector',
    'current_position',
    'rank_position',
    'economic_sector',
    'salary',
    'job_finding_method___1',
    'job_finding_method___2',
    'job_finding_method___3',
    'job_finding_method___4',
    'job_finding_method___5',
    'job_finding_method___6',
    'job_finding_method___7',
    'job_finding_method___8',
    'job_aspects___1',
    'job_aspects___2',
    'job_aspects___3',
    'job_aspects___4',
    'job_aspects___5',
    'job_aspects___6',
    'job_aspects___7',
    'job_aspects___8',
    'job_aspects___9',
    'job_aspects___10',
    'job_aspects___11',
    'job_aspects___12',
    'relation_to_job',
    'job_satisfaction',
    'comments',
    'comment_better_employment',

    # Tracer study contact fields — all optional
    'involve_trace_studies',
    'name_initial',
    'contact_details',
    'contact_details_2',

    # Optional free-text fields
    'reson_not_recommend_uok',
    'facilitate_employment',
    'linkedin_url',
    'internship_training_type',
    'extra_activities_1',
    'vocational_training_1',
    'other_courses_1',
]

STUDENT_ID_COL = 'student_number'
COMPLETION_THRESHOLD = 50


# ==========================================
# DEGREE LABEL MAPS  (code → label)
# ==========================================

DEGREE_FCMS = {
    1:  'BBM Honours in Accountancy',
    2:  'BBM Honours in Auditing and Forensic Accounting',
    3:  'BBM Honours in Banking',
    4:  'BBM Honours in Finance',
    5:  'BBM Honours in Financial Engineering',
    6:  'BBM Honours in Human Resource',
    7:  'BBM Honours in Insurance',
    8:  'BBM Honours in Marketing',
    9:  'Bachelor of Commerce Honours',
    10: 'Bachelor of Commerce Honours in Business Technology',
    11: 'Bachelor of Commerce Honours in Entrepreneurship',
    12: 'Bachelor of Commerce Honours in Financial Management',
    13: 'Other (FCMS)',
}

DEGREE_FCT = {
    1: 'BET Honours',
    2: 'BICT Honours',
    3: 'BSc Honours in Computer Science',
    4: 'Other (FCT)',
}

DEGREE_FHU = {
    1:  'BA (General Degree)',
    2:  'BA Honours in Buddhist Culture',
    3:  'BA Honours in Buddhist Philosophy',
    4:  'BA Honours in Buddhist Psychology',
    5:  'BA Honours in Business and Academic Chinese',
    6:  'BA Honours in Christian Culture',
    7:  'BA Honours in Drama and Theatre',
    8:  'BA Honours in English',
    9:  'BA Honours in Film & Television',
    10: 'BA Honours in French Studies',
    11: 'BA Honours in German Studies',
    12: 'BA Honours in Hindi Studies',
    13: 'BA Honours in Image Arts',
    14: 'BA Honours in Japanese Studies',
    15: 'BA Honours in Korean Studies',
    16: 'BA Honours in Linguistics',
    17: 'BA Honours in Literary Criticism',
    18: 'BA Honours in Pali',
    19: 'BA Honours in Performing Arts (Dance)',
    20: 'BA Honours in Performing Arts (Music)',
    21: 'BA Honours in Russian',
    22: 'BA Honours in Sanskrit',
    23: 'BA Honours in Sinhala',
    24: 'BA Honours in Teaching English as a Second Language',
    25: 'BA Honours in Translational Studies',
    26: 'BA Honours in Vastu Vidya',
    27: 'BA Honours in Visual Arts and Design',
    28: 'BA Honours in Western Classical Culture',
    29: 'Other (FHU)',
}

DEGREE_FMED = {
    1: 'MBBS',
    2: 'BSc Honours in Occupational Therapy',
    3: 'BSc Honours in Speech & Hearing Sciences (Speech & Language Therapy)',
    4: 'BSc Honours in Speech & Hearing Sciences (Audiology)',
    5: 'Other (FMED)',
}

DEGREE_FSC = {
    1:  'BSc (Biological Science - General Degree)',
    2:  'BSc (Physical Science - General Degree)',
    3:  'BSc Honours in Biochemistry',
    4:  'BSc Honours in Botany',
    5:  'BSc Honours in Chemistry',
    6:  'BSc Honours in Computer Science',
    7:  'BSc Honours in Computer Studies',
    8:  'BSc Honours in Environmental Conservation and Management',
    9:  'BSc Honours in Management and Information Technology',
    10: 'BSc Honours in Mathematical Physics',
    11: 'BSc Honours in Mathematics',
    12: 'BSc Honours in Microbiology',
    13: 'BSc Honours in Molecular Biology and Plant Biotechnology',
    14: 'BSc Honours in Physics',
    15: 'BSc Honours in Software Engineering',
    16: 'BSc Honours in Statistics',
    17: 'BSc Honours in Zoology',
    18: 'BSc in Environmental Conservation and Management (General Degree)',
    19: 'BSc in Management and Information Technology (General Degree)',
    20: 'BSc in Physics and Electronics',
    21: 'Other (FSC)',
}

DEGREE_FSOSC = {
    1:  'BA Honours in Archaeology',
    2:  'BA Honours in Development Studies',
    3:  'BA Honours in Economics',
    4:  'BA Honours in Geography',
    5:  'BA Honours in History',
    6:  'BA Honours in International Studies',
    7:  'BA Honours in Library and Media Management',
    8:  'BA Honours in Mass Communication',
    9:  'BA Honours in Peace and Conflict Resolution',
    10: 'BA Honours in Philosophy',
    11: 'BA Honours in Political Science',
    12: 'BA Honours in Psychology',
    13: 'BA Honours in Public Relations and Media Management',
    14: 'BA Honours in Social Statistics',
    15: 'BA Honours in Sociology',
    16: 'BA Honours in Sports and Recreation Management',
    17: 'BA Honours in Tourism and Cultural Resource Management',
    18: 'BA in Tourism and Cultural Resource Management (General Degree)',
    19: 'BA (General Degree) - Social Sciences',
    20: 'Other (FSOSC)',
}


# ==========================================
# DEPARTMENT LABEL MAPS  (code → label)
# ==========================================

DEPT_FCMS = {
    1: 'Department of Accountancy',
    2: 'Department of Commerce & Financial Management',
    3: 'Department of Finance',
    4: 'Department of Human Resources',
    5: 'Department of Marketing Management',
}

DEPT_FCT = {
    1: 'Department of Applied Computing',
    2: 'Department of Computer Systems Engineering',
    3: 'Department of Software Engineering',
}

DEPT_FHU = {
    1:  'Department of English',
    2:  'Department of English Language Teaching',
    3:  'Department of Fine Arts',
    4:  'Department of Hindi Studies',
    5:  'Department of Linguistics',
    6:  'Department of Modern Languages',
    7:  'Department of Pali & Buddhist Studies',
    8:  'Department of Sanskrit',
    9:  'Department of Sinhala',
    10: 'Department of Western Classical Culture & Christian Culture',
}

DEPT_FSC = {
    1: 'Department of Plant & Molecular Biology',
    2: 'Department of Chemistry',
    3: 'Department of Industrial Management',
    4: 'Department of Mathematics',
    5: 'Department of Microbiology',
    6: 'Department of Physics',
    7: 'Department of Statistics & Computer Science',
    8: 'Department of Zoology & Environmental Management',
    9: 'Software Engineering Teaching Unit',
}

DEPT_FSOSC = {
    1:  'Department of Archaeology',
    2:  'Department of Economics',
    3:  'Department of Geography',
    4:  'Department of History',
    5:  'Department of International Studies',
    6:  'Department of Library & Information Science',
    7:  'Department of Mass Communication',
    8:  'Department of Philosophy',
    9:  'Department of Political Science',
    10: 'Department of Social Statistics',
    11: 'Department of Sociology',
    12: 'Department of Sports Science & Physical Education',
}


# ==========================================
# CONSOLIDATION FUNCTIONS
# ==========================================

def consolidate_degree(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a single 'degree' column by reading the one filled
    faculty-specific degree column per row and mapping its numeric
    code to a human-readable label.
    The original degree_xxx columns are dropped after consolidation.
    """
    faculty_degree_map = {
        'degree_fcms':  DEGREE_FCMS,
        'degree_fct':   DEGREE_FCT,
        'degree_fhu':   DEGREE_FHU,
        'degree_fmed':  DEGREE_FMED,
        'degree_fsc':   DEGREE_FSC,
        'degree_fsosc': DEGREE_FSOSC,
    }

    def get_degree(row):
        for col, mapping in faculty_degree_map.items():
            if col in row and pd.notna(row[col]):
                code = int(row[col])
                return mapping.get(code, f'Unknown ({col}={code})')
        return None

    df['degree'] = df.apply(get_degree, axis=1)

    cols_to_drop = [c for c in faculty_degree_map if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    return df


def consolidate_department(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a single 'department' column by reading the one filled
    faculty-specific department column per row and mapping its numeric
    code to a human-readable label.
    The original department_xxx columns are dropped after consolidation.
    """
    faculty_dept_map = {
        'department_fcms':  DEPT_FCMS,
        'department_fct':   DEPT_FCT,
        'department_fhu':   DEPT_FHU,
        'department_fsc':   DEPT_FSC,
        'department_fsosc': DEPT_FSOSC,
    }

    def get_department(row):
        for col, mapping in faculty_dept_map.items():
            if col in row and pd.notna(row[col]):
                code = int(row[col])
                return mapping.get(code, f'Unknown ({col}={code})')
        return None

    df['department'] = df.apply(get_department, axis=1)

    cols_to_drop = [c for c in faculty_dept_map if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    return df


# ==========================================
# LOW COMPLETION — INLINE FUNCTION
# ==========================================

def remove_low_completion_rows(df, ignore_columns=None, required_pct=50):
    """
    Removes rows where the percentage of filled values is below required_pct.
    """
    if ignore_columns is None:
        ignore_columns = []

    check_columns = [col for col in df.columns if col not in ignore_columns]

    filled_fraction = df[check_columns].apply(
        lambda x: x.astype(str)
                   .str.strip()
                   .replace(['nan', 'None', ''], pd.NA)
    ).notnull().mean(axis=1)

    mask = (filled_fraction * 100) >= required_pct

    cleaned_df = df[mask].copy()
    removed_df = df[~mask].copy()

    if not removed_df.empty:
        removed_df['reason'] = f'Filled < {required_pct}%'
    else:
        removed_df = pd.DataFrame(columns=list(df.columns) + ['reason'])

    return cleaned_df, removed_df


# ==========================================
# MAIN CLEANING FUNCTION
# ==========================================

def clean_graduate_employability_data(df: pd.DataFrame):
    """
    Cleans the Graduate Employability Survey dataset.

    Steps:
        1. Remove fully duplicate rows
        2. Remove duplicate student numbers (keep first)
        3. Remove low-completion rows (< 50% filled)
        4. Consolidate degree_xxx columns into single 'degree' column
        5. Consolidate department_xxx columns into single 'department' column

    Returns:
        cleaned_df, removed_df, status (bool), msg (str), metadata (dict)
    """
    try:
        removed_all = pd.DataFrame(columns=list(df.columns) + ['reason'])
        original_count = len(df)

        # --- Step 1: Remove fully duplicate rows ---
        df, removed_dupes = remove_survey_duplicates(df, ignore_columns=IGNORE_COLUMNS)
        removed_all = pd.concat([removed_all, removed_dupes], ignore_index=True)

        # --- Step 2: Remove duplicate student numbers ---
        if STUDENT_ID_COL in df.columns:
            dup_student_mask = df.duplicated(subset=[STUDENT_ID_COL], keep='first')
            dup_students = df[dup_student_mask].copy()

            if not dup_students.empty:
                dup_students['reason'] = f'Duplicate student number ({STUDENT_ID_COL})'
                removed_all = pd.concat([removed_all, dup_students], ignore_index=True)

            df = df[~dup_student_mask].reset_index(drop=True)
            dup_student_count = len(dup_students)
        else:
            dup_student_count = 0

        # --- Step 3: Remove low-completion rows ---
        df, removed_low = remove_low_completion_rows(
            df,
            ignore_columns=IGNORE_COLUMNS,
            required_pct=COMPLETION_THRESHOLD
        )
        removed_all = pd.concat([removed_all, removed_low], ignore_index=True)

        # --- Step 4 & 5: Consolidate degree and department columns ---
        degree_cols_present = [c for c in df.columns if c.startswith('degree_') and c != 'degree_type']
        dept_cols_present   = [c for c in df.columns if c.startswith('department_')]

        df = consolidate_degree(df)
        df = consolidate_department(df)

        combined_cols = degree_cols_present + dept_cols_present

        # --- Build metadata for Review Dashboard ---
        metadata = {
            'original_row_count'        : original_count,
            'final_row_count'           : len(df),
            'total_rows_removed'        : len(removed_all),
            'removed_duplicates_count'  : len(removed_dupes) + dup_student_count,
            'duplicate_students_removed': dup_student_count,
            'removed_empty_count'       : len(removed_low),
            'removed_columns'           : [],
            'combined_columns'          : combined_cols,
        }

        msg = (
            f"Graduate Employability cleaning complete. "
            f"{original_count} → {len(df)} rows kept. "
            f"{len(removed_all)} rows removed "
            f"({len(removed_dupes)} duplicate rows, "
            f"{dup_student_count} duplicate student numbers, "
            f"{len(removed_low)} low-completion rows). "
            f"{len(combined_cols)} columns consolidated into 'degree' and 'department'."
        )

        return df, removed_all, True, msg, metadata

    except Exception as e:
        empty_removed = pd.DataFrame(columns=list(df.columns) + ['reason'])
        return df, empty_removed, False, f'Graduate Employability cleaning error: {e}', {}