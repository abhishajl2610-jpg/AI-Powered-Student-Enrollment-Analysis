-- ============================================================
-- AISHE Higher Education Enrollment Analytics
-- SQL Business Analysis Queries
-- Database: aishe_higher_education
-- ============================================================

USE aishe_higher_education;

-- ============================================================
-- SECTION 1: OVERALL ENROLLMENT
-- ============================================================

-- 1.1 All India enrollment by year
SELECT
    Year,
    Grand_Total AS Total_Enrollment,
    Grand_Total_Male AS Male_Enrollment,
    Grand_Total_Female AS Female_Enrollment,
    ROUND(Grand_Total_Female / Grand_Total * 100, 2) AS Female_Share_Pct
FROM enrollment_trend
WHERE State_UT = 'All India'
ORDER BY Year;

-- 1.2 Year-over-year enrollment growth (All India)
WITH ai_trend AS (
    SELECT
        Year,
        Grand_Total,
        LAG(Grand_Total) OVER (ORDER BY Year) AS Prev_Year_Total
    FROM enrollment_trend
    WHERE State_UT = 'All India'
)
SELECT
    Year,
    ROUND(Grand_Total, 0)               AS Total_Enrollment,
    ROUND(Prev_Year_Total, 0)           AS Prev_Year_Enrollment,
    ROUND(Grand_Total - Prev_Year_Total, 0) AS Absolute_Growth,
    ROUND((Grand_Total - Prev_Year_Total) / Prev_Year_Total * 100, 2) AS YoY_Growth_Pct
FROM ai_trend
WHERE Prev_Year_Total IS NOT NULL
ORDER BY Year;

-- 1.3 Total enrollment sum across all years (state level, excluding All India)
SELECT
    Year,
    ROUND(SUM(Grand_Total), 0) AS Sum_State_Enrollments
FROM enrollment_trend
WHERE State_UT != 'All India'
GROUP BY Year
ORDER BY Year;


-- ============================================================
-- SECTION 2: STATE / UT ANALYSIS
-- ============================================================

-- 2.1 State ranking by enrollment in 2023-24
SELECT
    RANK() OVER (ORDER BY Grand_Total DESC) AS State_Rank,
    State_UT,
    ROUND(Grand_Total, 0)  AS Total_Enrollment,
    ROUND(Grand_Total_Male, 0) AS Male_Enrollment,
    ROUND(Grand_Total_Female, 0) AS Female_Enrollment
FROM enrollment_trend
WHERE Year = '2023-24'
  AND State_UT != 'All India'
ORDER BY Grand_Total DESC;

-- 2.2 Top 10 states by enrollment (2023-24)
SELECT
    State_UT,
    ROUND(Grand_Total, 0) AS Total_Enrollment
FROM enrollment_trend
WHERE Year = '2023-24'
  AND State_UT != 'All India'
ORDER BY Grand_Total DESC
LIMIT 10;

-- 2.3 Bottom 10 states by enrollment (2023-24)
SELECT
    State_UT,
    ROUND(Grand_Total, 0) AS Total_Enrollment
FROM enrollment_trend
WHERE Year = '2023-24'
  AND State_UT != 'All India'
ORDER BY Grand_Total ASC
LIMIT 10;

-- 2.4 State enrollment growth from 2019-20 to 2023-24
SELECT
    a.State_UT,
    ROUND(a.Grand_Total, 0) AS Enrollment_2019_20,
    ROUND(b.Grand_Total, 0) AS Enrollment_2023_24,
    ROUND(b.Grand_Total - a.Grand_Total, 0) AS Absolute_Growth,
    ROUND((b.Grand_Total - a.Grand_Total) / a.Grand_Total * 100, 2) AS Growth_Pct_5yr
FROM enrollment_trend a
JOIN enrollment_trend b
  ON a.State_UT = b.State_UT
WHERE a.Year = '2019-20'
  AND b.Year = '2023-24'
  AND a.State_UT != 'All India'
ORDER BY Growth_Pct_5yr DESC;

-- 2.5 States where female enrollment exceeds male (2023-24)
SELECT
    State_UT,
    ROUND(Grand_Total_Male, 0)   AS Male_Enrollment,
    ROUND(Grand_Total_Female, 0) AS Female_Enrollment,
    ROUND(Grand_Total_Female - Grand_Total_Male, 0) AS Female_Surplus
FROM enrollment_trend
WHERE Year = '2023-24'
  AND State_UT != 'All India'
  AND Grand_Total_Female > Grand_Total_Male
ORDER BY Female_Surplus DESC;


-- ============================================================
-- SECTION 3: GENDER ANALYSIS
-- ============================================================

-- 3.1 National gender enrollment share by year
SELECT
    Year,
    ROUND(Grand_Total_Male, 0)   AS Male_Enrollment,
    ROUND(Grand_Total_Female, 0) AS Female_Enrollment,
    ROUND(Grand_Total_Male   / Grand_Total * 100, 2) AS Male_Share_Pct,
    ROUND(Grand_Total_Female / Grand_Total * 100, 2) AS Female_Share_Pct,
    ROUND(Grand_Total_Male - Grand_Total_Female, 0)  AS Gender_Gap
FROM enrollment_trend
WHERE State_UT = 'All India'
ORDER BY Year;

-- 3.2 Gender gap by state (2023-24)
SELECT
    State_UT,
    ROUND(Grand_Total_Male, 0)   AS Male_Enrollment,
    ROUND(Grand_Total_Female, 0) AS Female_Enrollment,
    ROUND(ABS(Grand_Total_Male - Grand_Total_Female), 0) AS Gender_Gap,
    CASE
        WHEN Grand_Total_Female > Grand_Total_Male THEN 'Female-dominant'
        WHEN Grand_Total_Male   > Grand_Total_Female THEN 'Male-dominant'
        ELSE 'Equal'
    END AS Gender_Status
FROM enrollment_trend
WHERE Year = '2023-24'
  AND State_UT != 'All India'
ORDER BY Gender_Gap DESC;


-- ============================================================
-- SECTION 4: PROGRAMME ANALYSIS
-- ============================================================

-- 4.1 Top 15 programmes by enrollment (2023-24)
SELECT
    Programme,
    ROUND(Total, 0) AS Total_Enrollment,
    ROUND(Male,  0) AS Male_Enrollment,
    ROUND(Female, 0) AS Female_Enrollment
FROM programme_enrollment
ORDER BY Total DESC
LIMIT 15;

-- 4.2 Programmes with female majority (2023-24)
SELECT
    Programme,
    ROUND(Total, 0) AS Total_Enrollment,
    ROUND(Female / Total * 100, 2) AS Female_Share_Pct
FROM programme_enrollment
WHERE Female > Male
ORDER BY Female_Share_Pct DESC;


-- ============================================================
-- SECTION 5: DISCIPLINE ANALYSIS
-- ============================================================

-- 5.1 UG disciplines by enrollment (2023-24)
SELECT
    `Broad_Discipline_Group`,
    ROUND(Total, 0) AS Total_Enrollment,
    ROUND(Male,  0) AS Male_Enrollment,
    ROUND(Female,0) AS Female_Enrollment,
    ROUND(Female / Total * 100, 2) AS Female_Share_Pct
FROM ug_discipline_enrollment
ORDER BY Total DESC;

-- 5.2 PG/PhD disciplines by enrollment (2023-24)
SELECT
    `Broad_Discipline_Group`,
    ROUND(Total, 0) AS Total_Enrollment,
    ROUND(Male,  0) AS Male_Enrollment,
    ROUND(Female,0) AS Female_Enrollment
FROM pg_phd_discipline_enrollment
ORDER BY Total DESC;

-- 5.3 UG disciplines where female enrollment is higher than male
SELECT
    `Broad_Discipline_Group`,
    ROUND(Male,   0) AS Male_Enrollment,
    ROUND(Female, 0) AS Female_Enrollment,
    ROUND(Female - Male, 0) AS Female_Surplus
FROM ug_discipline_enrollment
WHERE Female > Male
ORDER BY Female_Surplus DESC;


-- ============================================================
-- SECTION 6: ADVANCED — CTEs AND WINDOW FUNCTIONS
-- ============================================================

-- 6.1 Dense rank of states by enrollment each year
WITH ranked AS (
    SELECT
        Year,
        State_UT,
        Grand_Total,
        DENSE_RANK() OVER (PARTITION BY Year ORDER BY Grand_Total DESC) AS Yearly_Rank
    FROM enrollment_trend
    WHERE State_UT != 'All India'
)
SELECT Year, State_UT, ROUND(Grand_Total, 0) AS Enrollment, Yearly_Rank
FROM ranked
WHERE Yearly_Rank <= 5
ORDER BY Year, Yearly_Rank;

-- 6.2 Running total enrollment for All India across years
SELECT
    Year,
    ROUND(Grand_Total, 0) AS Yearly_Enrollment,
    ROUND(SUM(Grand_Total) OVER (ORDER BY Year), 0) AS Running_Total
FROM enrollment_trend
WHERE State_UT = 'All India'
ORDER BY Year;

-- 6.3 Average enrollment by UG discipline category (above-average vs below)
WITH ug_avg AS (
    SELECT AVG(Total) AS Avg_UG_Enrollment FROM ug_discipline_enrollment
)
SELECT
    u.`Broad_Discipline_Group`,
    ROUND(u.Total, 0) AS Total_Enrollment,
    CASE
        WHEN u.Total >= a.Avg_UG_Enrollment THEN 'Above Average'
        ELSE 'Below Average'
    END AS Vs_Average
FROM ug_discipline_enrollment u, ug_avg a
ORDER BY u.Total DESC;
