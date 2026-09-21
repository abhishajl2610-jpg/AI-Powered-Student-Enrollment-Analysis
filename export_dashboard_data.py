"""
export_dashboard_data.py
Exports all necessary data as JSON for the dashboard to consume.
This script MUST be run before opening dashboard.html.
Reads from processed CSVs and saved ML models.
"""
import os
import sys
import json
import pickle
import pandas as pd
import numpy as np

sys.path.insert(0, 'src')
from config import DATA_PROCESSED_DIR, MODELS_DIR, CSV_FILES, OUTPUTS_DIR


def load_data():
    """Load cleaned CSVs, fallback to raw if not available."""
    def _load(name, raw_key):
        path = os.path.join(DATA_PROCESSED_DIR, f'{name}_cleaned.csv')
        return pd.read_csv(path) if os.path.exists(path) else pd.read_csv(CSV_FILES[raw_key])

    return {
        'trend':       _load('enrollment_trend', 'enrollment_trend'),
        'ug':          _load('ug_discipline_enrollment', 'ug_discipline_enrollment'),
        'pg':          _load('pg_phd_discipline_enrollment', 'pg_phd_discipline_enrollment'),
        'programme':   _load('programme_enrollment', 'programme_enrollment'),
    }


def col(df, options):
    """Return first matching column name from options."""
    for o in options:
        if o in df.columns:
            return o
    return None


def nan_safe(val):
    """Convert NaN/inf to None for JSON serialisation."""
    if val is None:
        return None
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    return val


def export_all():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    data = load_data()
    df_trend  = data['trend']
    df_ug     = data['ug']
    df_pg     = data['pg']
    df_prog   = data['programme']

    # Detect column names (cleaned vs raw)
    state_col  = col(df_trend, ['state_ut', 'State_UT'])
    year_col   = col(df_trend, ['year', 'Year'])
    total_col  = col(df_trend, ['grand_total', 'Grand_Total'])
    male_col   = col(df_trend, ['grand_total_male', 'Grand_Total_Male'])
    female_col = col(df_trend, ['grand_total_female', 'Grand_Total_Female'])

    # ── 1. KPI Summary ────────────────────────────────────────────────────────
    ai_2023 = df_trend[(df_trend[state_col] == 'All India') & (df_trend[year_col] == '2023-24')].iloc[0]
    ai_2022 = df_trend[(df_trend[state_col] == 'All India') & (df_trend[year_col] == '2022-23')].iloc[0]

    yoy_growth = (ai_2023[total_col] - ai_2022[total_col]) / ai_2022[total_col] * 100
    female_share = ai_2023[female_col] / ai_2023[total_col] * 100

    ug_disc_col  = col(df_ug,  ['discipline', 'broad_discipline_group', 'Broad_Discipline_Group'])
    ug_total_col = col(df_ug,  ['total', 'Total'])
    pg_disc_col  = col(df_pg,  ['discipline', 'broad_discipline_group', 'Broad_Discipline_Group'])
    pg_total_col = col(df_pg,  ['pg_total', 'total', 'Total'])  # cleaned PG uses pg_total
    prog_name_col  = col(df_prog, ['programme', 'Programme'])
    prog_total_col = col(df_prog, ['all_total', 'total', 'Total'])  # cleaned prog uses all_total

    n_states = int(df_trend[(df_trend[year_col] == '2023-24') & (df_trend[state_col] != 'All India')][state_col].nunique())

    kpis = {
        'total_enrollment_2023_24': round(float(ai_2023[total_col]), 0),
        'total_enrollment_2022_23': round(float(ai_2022[total_col]), 0),
        'yoy_growth_pct': round(float(yoy_growth), 2),
        'female_share_pct': round(float(female_share), 2),
        'male_enrollment': round(float(ai_2023[male_col]), 0),
        'female_enrollment': round(float(ai_2023[female_col]), 0),
        'n_states': n_states,
        'n_programmes': int(len(df_prog)),
        'n_ug_disciplines': int(len(df_ug)),
        'n_pg_disciplines': int(len(df_pg)),
        'top_state': df_trend[(df_trend[year_col] == '2023-24') & (df_trend[state_col] != 'All India')].nlargest(1, total_col).iloc[0][state_col],
        'top_ug_discipline': df_ug.nlargest(1, ug_total_col).iloc[0][ug_disc_col] if ug_disc_col and ug_total_col else 'N/A',
        'top_pg_discipline': df_pg.nlargest(1, pg_total_col).iloc[0][pg_disc_col] if pg_disc_col and pg_total_col else 'N/A',
    }

    # ── 2. Enrollment Trend (All India) ──────────────────────────────────────
    ai_trend = df_trend[df_trend[state_col] == 'All India'].copy().sort_values(year_col)
    ai_trend['prev'] = ai_trend[total_col].shift(1)
    ai_trend['yoy'] = ((ai_trend[total_col] - ai_trend['prev']) / ai_trend['prev'] * 100).round(2)

    trend_data = []
    for _, row in ai_trend.iterrows():
        trend_data.append({
            'year': row[year_col],
            'total': round(float(row[total_col]), 0),
            'male': round(float(row[male_col]), 0) if pd.notna(row[male_col]) else None,
            'female': round(float(row[female_col]), 0) if pd.notna(row[female_col]) else None,
            'yoy_growth': nan_safe(row['yoy']),
        })

    # ── 3. State Data (2023-24) ───────────────────────────────────────────────
    states_2023 = df_trend[(df_trend[year_col] == '2023-24') & (df_trend[state_col] != 'All India')].copy()
    states_2023 = states_2023.sort_values(total_col, ascending=False)
    state_data = []
    for i, (_, row) in enumerate(states_2023.iterrows()):
        state_data.append({
            'rank': i + 1,
            'state': row[state_col],
            'total': round(float(row[total_col]), 0),
            'male': round(float(row[male_col]), 0) if pd.notna(row.get(male_col)) else None,
            'female': round(float(row[female_col]), 0) if pd.notna(row.get(female_col)) else None,
        })

    # ── 4. UG Disciplines ────────────────────────────────────────────────────
    ug_male_col   = col(df_ug, ['male', 'Male'])
    ug_female_col = col(df_ug, ['female', 'Female'])

    ug_data = []
    if ug_disc_col and ug_total_col:
        for _, row in df_ug.dropna(subset=[ug_disc_col]).sort_values(ug_total_col, ascending=False).iterrows():
            ug_data.append({
                'discipline': row[ug_disc_col],
                'total': round(float(row[ug_total_col]), 0) if pd.notna(row[ug_total_col]) else None,
                'male':   round(float(row[ug_male_col]), 0) if ug_male_col and pd.notna(row.get(ug_male_col)) else None,
                'female': round(float(row[ug_female_col]), 0) if ug_female_col and pd.notna(row.get(ug_female_col)) else None,
            })

    # -- 5. PG/PhD Disciplines
    pg_male_col   = col(df_pg, ['pg_male', 'male', 'Male'])
    pg_female_col = col(df_pg, ['pg_female', 'female', 'Female'])

    pg_data = []
    if pg_disc_col and pg_total_col:
        for _, row in df_pg.dropna(subset=[pg_disc_col]).sort_values(pg_total_col, ascending=False).iterrows():
            pg_data.append({
                'discipline': row[pg_disc_col],
                'total': round(float(row[pg_total_col]), 0) if pd.notna(row[pg_total_col]) else None,
                'male':   round(float(row[pg_male_col]), 0)   if pg_male_col and pd.notna(row.get(pg_male_col)) else None,
                'female': round(float(row[pg_female_col]), 0) if pg_female_col and pd.notna(row.get(pg_female_col)) else None,
            })

    # ── 6. Programme Data ────────────────────────────────────────────────────
    prog_male_col   = col(df_prog, ['all_male', 'male', 'Male'])
    prog_female_col = col(df_prog, ['all_female', 'female', 'Female'])

    prog_data = []
    if prog_name_col and prog_total_col:
        for _, row in df_prog.dropna(subset=[prog_name_col]).sort_values(prog_total_col, ascending=False).head(30).iterrows():
            prog_data.append({
                'programme': row[prog_name_col],
                'total': round(float(row[prog_total_col]), 0) if pd.notna(row[prog_total_col]) else None,
                'male':   round(float(row[prog_male_col]), 0)   if prog_male_col and pd.notna(row.get(prog_male_col)) else None,
                'female': round(float(row[prog_female_col]), 0) if prog_female_col and pd.notna(row.get(prog_female_col)) else None,
            })

    # ── 7. ML Model Info ─────────────────────────────────────────────────────
    ml_meta = {}
    try:
        with open(os.path.join(MODELS_DIR, 'model_meta.pkl'), 'rb') as f:
            ml_meta = pickle.load(f)
    except Exception:
        ml_meta = {'model_name': 'Not available', 'r2': None}

    # ── 8. 2024-25 Predictions ───────────────────────────────────────────────
    predictions_2024 = []
    try:
        with open(os.path.join(MODELS_DIR, 'best_model.pkl'), 'rb') as f:
            model = pickle.load(f)
        with open(os.path.join(MODELS_DIR, 'state_encoder.pkl'), 'rb') as f:
            encoder = pickle.load(f)

        for row in state_data:
            st = row['state']
            prev_enr = row['total']
            inp = pd.DataFrame({'Year_Int': [2024], 'Prev_Enrollment': [prev_enr], 'State_UT': [st]})
            enc = pd.DataFrame(encoder.transform(inp[['State_UT']]), columns=encoder.get_feature_names_out())
            X = pd.concat([inp.drop('State_UT', axis=1).reset_index(drop=True), enc], axis=1)
            pred = max(0, float(model.predict(X)[0]))
            predictions_2024.append({
                'state': st,
                'actual_2023_24': prev_enr,
                'predicted_2024_25': round(pred, 0),
            })
    except Exception as e:
        predictions_2024 = []

    # ── Assemble and write JSON ───────────────────────────────────────────────
    dashboard_data = {
        'kpis':            kpis,
        'trend':           trend_data,
        'states':          state_data,
        'ug_disciplines':  ug_data,
        'pg_disciplines':  pg_data,
        'programmes':      prog_data,
        'ml_meta':         {k: (nan_safe(v) if isinstance(v, float) else v) for k, v in ml_meta.items() if k != 'model'},
        'predictions_2024': predictions_2024,
    }

    out_path = os.path.join(OUTPUTS_DIR, 'dashboard_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, default=str)

    print(f'Dashboard data exported: {out_path}')
    print(f'  KPIs                 : {len(kpis)} metrics')
    print(f'  Trend points         : {len(trend_data)} years')
    print(f'  States               : {len(state_data)}')
    print(f'  UG disciplines       : {len(ug_data)}')
    print(f'  PG/PhD disciplines   : {len(pg_data)}')
    print(f'  Programmes           : {len(prog_data)}')
    print(f'  2024-25 predictions  : {len(predictions_2024)} states')
    print(f'  Best model           : {ml_meta.get("model_name", "N/A")}')
    return out_path


if __name__ == '__main__':
    export_all()
