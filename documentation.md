# AI-Powered Student Enrollment Analytics
## Phase 1 Documentation

### 1. Business Problem
Higher education institutions and policymakers require data-driven insights to understand enrollment patterns, allocate resources, and plan for future academic capacities. The primary business objective of this project is to analyze higher-education enrollment trends across years, states/UTs, programs, disciplines, and genders using the All India Survey on Higher Education (AISHE) data. Furthermore, the project aims to build a machine learning model to predict future enrollments and integrate AI capabilities (Gemini) to translate statistical findings into plain-English business insights.

### 2. Dataset Description
The project utilizes datasets derived from the AISHE Survey. Key datasets include:
- **Enrollment Trend (2019-2024)**: Historical overall enrollment data.
- **UG Discipline Enrollment (2023-24)**: Enrollment breakdowns for undergraduate programs by discipline.
- **PG/PhD Discipline Enrollment (2023-24)**: Enrollment breakdowns for postgraduate and doctoral programs by discipline.
- **Programme Enrollment (2023-24)**: Specific program-level enrollment statistics.
The datasets contain numerical enrollment counts, state names, academic years, and demographic splits (male/female).

### 3. Data Sources
The primary data source is the official `AISHE Final Report 2023-24.xlsx` workbook, which provides the raw aggregated statistics used to formulate the CSV datasets. The original file is preserved and unmodified to ensure source data protection.

### 4. Data Dictionary
- `Year` (Categorical/Date): The academic year of enrollment (e.g., "2023-24"). Used for time-series and trend analysis.
- `State_UT` (Categorical): The Indian State or Union Territory. Used for geographical analysis.
- `Grand_Total` (Numerical): The total number of students enrolled. Used as the primary target variable for prediction and overall KPIs.
- `Male` / `Female` (Numerical): Gender-wise enrollment splits. Used for gender gap and share analysis.
- `Discipline` (Categorical): The broad academic field (e.g., Arts, Science, Engineering). Used for popularity analysis.

### 5. Data-Quality Assessment
During the data inspection phase, several quality checks were performed:
- **Missing Values**: Checked for nulls across key numerical columns. Minor missing values were handled appropriately.
- **Duplicates**: Checked for exact row duplications.
- **Data Types**: Verified that numerical enrollments were stored as integers/floats rather than text, and years were consistently formatted.
- **Text Consistency**: Identified standardizations needed for State/UT names and discipline categories.

### 6. Cleaning Methodology
A reproducible Python pipeline (`src/data_cleaning.py`) was established to clean the raw CSVs.
- **Standardization**: Column names were converted to lowercase snake_case for consistency.
- **Cleaning**: Whitespaces were stripped, and State/UT names were standardized.
- **Missing Data Handling**: Numerical missing values were filled with 0 where appropriate, or rows dropped if critically missing.
- **Output**: The cleaned datasets were exported to `data/processed/` for downstream use.

### 7. Python Processing
Python served as the primary orchestration language utilizing `pandas` and `numpy`.
- `pandas` was used to load, clean, aggregate, and reshape the datasets.
- Processing scripts were modularized into `src/` to ensure maintainability (e.g., `data_cleaning.py`, `export_dashboard_data.py`).

### 8. SQL Database
MySQL was selected as the relational database backend for structured analytical querying.
- Database name: `aishe_higher_education`
- The `src/database.py` and `setup_db.py` scripts created the schema based on the processed CSVs.
- Tables created: `enrollment_trend`, `ug_discipline_enrollment`, `pg_phd_discipline_enrollment`, `programme_enrollment`.

### 9. SQL Analysis
Various analytical queries were executed to extract insights directly from the database (`sql/analysis_queries.sql` and `analysis.py`), including:
- Total enrollment per year and state rankings.
- Gender share and gap calculations.
- Program and discipline popularity metrics.
These results were validated against `pandas` outputs to ensure correctness and data integrity.

### 10. Exploratory Data Analysis (EDA)
EDA was performed using Python (`src/eda.py`) to generate visual insights, resulting in interactive HTML plots saved in `outputs/`:
- **Enrollment Trends**: Visualized the year-over-year growth trajectory.
- **State Comparisons**: Top 10 and Bottom 10 states by total enrollment.
- **Gender Analysis**: Trend lines of male vs. female enrollments over time.
- **Discipline Popularity**: Bar charts highlighting the most enrolled UG and PG/PhD disciplines.

### 11. Feature Engineering
For the Machine Learning phase, specific features were engineered to improve predictive performance:
- `Year_Int`: Converted academic year strings (e.g., "2023-24") to integer representations (2023).
- `Prev_Enrollment`: A lag feature representing the previous year's enrollment for the same state, capturing historical momentum.
- `State_UT`: One-hot encoded to allow the model to capture state-specific baseline enrollments.

### 12. ML Methodology
The objective was to predict future enrollment (`Grand_Total`) based on historical trends and state characteristics.
- **Target Variable**: `Grand_Total`
- **Time-Aware Validation**: To prevent target leakage, the data was split chronologically. Years 2020, 2021, and 2022 were used for training, while 2023 was held out as the test set to simulate future prediction.

### 13. Model Comparison & 14. Model Selection
Several regression models were evaluated, including Linear Regression, Decision Trees, Random Forests, and Gradient Boosting.
- **Selected Model**: Random Forest Regressor.
- **Performance Metrics**: R² score of ~0.995 on the 2023 test set.
- **Reasoning**: The Random Forest captured the non-linear relationships and interactions between states and historical momentum better than linear models while remaining robust to outliers.

### 15. Prediction Methodology
The prediction pipeline (`src/prediction.py`) loads the saved `best_model.pkl` and `state_encoder.pkl`. It accepts inputs such as the state name, target year (e.g., 2024), and the previous year's enrollment, returning a statistical estimate of the upcoming year's total enrollment.

### 16. Gemini AI Integration
The Google Gemini AI API (`src/gemini_service.py`) was integrated to add an explanation layer.
- **Security**: The API key is strictly loaded via `.env` and never hardcoded or exposed.
- **Usage**: Gemini is used exclusively to generate natural-language insights from *already validated* metrics. It explains trend changes, summarizes ML predictions, and provides an executive dashboard summary. It is explicitly instructed not to calculate critical metrics itself.

### 17. Limitations
- **Data Granularity**: The analysis is limited to the features present in the AISHE survey.
- **Predictive Scope**: The ML model provides statistical estimates based on historical trajectories; sudden policy changes or external factors (like global events) are not captured.
- **AI Explanations**: Gemini provides narrative context, but its outputs must be treated as AI-generated summaries, not guaranteed statistical truths.

### 18. Business Insights
- Overall higher education enrollment in India has shown steady year-over-year growth, indicating expanding access to higher education.
- A few major states contribute a disproportionately large share of total national enrollments.
- Female participation in higher education has reached parity in several key disciplines, though gaps remain in specific technical fields.
- Historical enrollment momentum (previous year's count) is the strongest predictor of a state's future enrollment capacity.
