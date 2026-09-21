import os
import pandas as pd
import mysql.connector

# Parse .env manually
env_vars = {}
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
except FileNotFoundError:
    pass

db_host = env_vars.get('DB_HOST', 'localhost')
db_user = env_vars.get('DB_USER', 'root')
db_pass = env_vars.get('DB_PASSWORD', '')

print("--- SQL BUSINESS ANALYSIS & VALIDATION ---\n")

try:
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database='aishe_higher_education'
    )
    
    # Python/Pandas Data
    df_trend = pd.read_csv('AISHE_Enrollment_Trend_2019_2024.csv')
    df_ug = pd.read_csv('AISHE_UG_Discipline_Enrollment_2023_24.csv')
    
    def compare_metric(name, sql_val, pd_val):
        match = "MATCH" if str(sql_val) == str(pd_val) or (isinstance(sql_val, (int, float)) and isinstance(pd_val, (int, float)) and abs(sql_val - pd_val) < 1) else "MISMATCH"
        print(f"[{match}] {name} | SQL: {sql_val} | Pandas: {pd_val}")

    # 1. Total Enrollment for All India in 2023-24
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Grand_Total FROM enrollment_trend WHERE State_UT = 'All India' AND Year = '2023-24'")
    sql_total = cursor.fetchone()['Grand_Total']
    
    pd_total = df_trend[(df_trend['State_UT'] == 'All India') & (df_trend['Year'] == '2023-24')]['Grand_Total'].values[0]
    compare_metric("All India Total Enrollment (2023-24)", sql_total, pd_total)
    
    # 2. Total Male vs Female UG Enrollment 2023-24
    cursor.execute("SELECT SUM(Male) as Total_Male, SUM(Female) as Total_Female FROM ug_discipline_enrollment")
    sql_ug_gender = cursor.fetchone()
    
    pd_ug_male = df_ug['Male'].sum()
    pd_ug_female = df_ug['Female'].sum()
    
    compare_metric("UG Total Male (2023-24)", sql_ug_gender['Total_Male'], pd_ug_male)
    compare_metric("UG Total Female (2023-24)", sql_ug_gender['Total_Female'], pd_ug_female)

    # 3. Top 3 States by Total Enrollment in 2023-24 (excluding All India)
    cursor.execute("""
        SELECT State_UT, Grand_Total 
        FROM enrollment_trend 
        WHERE Year = '2023-24' AND State_UT != 'All India'
        ORDER BY Grand_Total DESC LIMIT 3
    """)
    sql_top_states = [row['State_UT'] for row in cursor.fetchall()]
    
    pd_top_states = df_trend[(df_trend['Year'] == '2023-24') & (df_trend['State_UT'] != 'All India')].sort_values(by='Grand_Total', ascending=False).head(3)['State_UT'].tolist()
    
    print(f"[MATCH if equal] Top 3 States | SQL: {sql_top_states} | Pandas: {pd_top_states}")
    
    cursor.close()
    conn.close()
    print("\nValidation completed.")

except Exception as e:
    print(f'Error during validation: {str(e)}')
