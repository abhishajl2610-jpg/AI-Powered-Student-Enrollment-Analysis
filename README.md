# AI Powered Student Enrollment Analysis

## Overview
An exploratory data analysis and machine learning pipeline on higher
education enrolment in India, using AISHE (All India Survey on Higher
Education) data from 2019-20 to 2023-24. The project explores enrolment
trends and predicts state-wise enrolment using regression models.

## How This Project Was Built
This project was built using an AI-assisted workflow. I used the
**Antigravity IDE** and guided the AI with prompts to generate the code,
visualisations and analysis, then reviewed and ran the results. It shows how
I use generative AI tools to speed up a data analysis and modelling workflow.

## Dataset
- File: `AISHE_Enrollment_Trend_2019_2024.csv`
- State/UT-wise total enrolment by year (2019-20 to 2023-24)
- The "All India" rows were excluded so the models focus on state-level predictions

## Project Workflow
1. **Load and filter data**: removed the "All India" total rows
2. **Exploratory data analysis** (Plotly, saved as interactive HTML):
   - Total enrolment trend over the years
   - Top 10 states by enrolment in 2023-24
3. **Feature engineering**:
   - Converted academic years to numeric values
   - Created previous year enrolment (lag feature) and growth rate for each state
4. **Chronological train/test split**:
   - Train: 2020-21 to 2022-23
   - Test: 2023-24
   - This avoids using future data to predict the past
5. **Preprocessing**: one-hot encoding of State/UT
6. **Modelling**: Linear Regression and Random Forest Regressor
7. **Evaluation**: RMSE, MAE and R², with the best model chosen by R²

## Results
| Model | RMSE | MAE | R² |
|---|---|---|---|
| Linear Regression | 112,239.96 | 58,133.77 | 0.9948 |
| Random Forest | 100,835.23 | 60,721.00 | 0.9958 |

Best model: (add)

## Tools Used
Python, pandas, NumPy, scikit-learn, Plotly, Antigravity IDE

## How to Run
1. Install the libraries:
   `pip install pandas numpy scikit-learn plotly`
2. Keep the CSV in the same folder as the script
3. Run:
   `AI Powered Student Enrollment Analytics.py`
