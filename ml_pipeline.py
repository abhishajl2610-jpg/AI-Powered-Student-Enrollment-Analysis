import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import plotly.express as px

print("--- EDA & MACHINE LEARNING PIPELINE ---")

# 1. Load Data
df = pd.read_csv('AISHE_Enrollment_Trend_2019_2024.csv')
# Exclude 'All India' to focus on State-level predictions
df = df[df['State_UT'] != 'All India'].copy()

# 2. EDA (using Plotly)
print("Generating EDA Visualizations...")
# Total Enrollment Trend
yearly_total = df.groupby('Year')['Grand_Total'].sum().reset_index()
fig1 = px.line(yearly_total, x='Year', y='Grand_Total', title='Total Higher Education Enrollment (State-level sum) over Years')
fig1.write_html('eda_total_enrollment_trend.html')

# State-wise Enrollment for 2023-24
df_2023 = df[df['Year'] == '2023-24'].sort_values('Grand_Total', ascending=False).head(10)
fig2 = px.bar(df_2023, x='State_UT', y='Grand_Total', title='Top 10 States by Enrollment (2023-24)')
fig2.write_html('eda_top10_states.html')

# 3. Feature Engineering
print("Performing Feature Engineering...")
# Sort chronologically to compute lags
year_mapping = {'2019-20': 2019, '2020-21': 2020, '2021-22': 2021, '2022-23': 2022, '2023-24': 2023}
df['Year_Int'] = df['Year'].map(year_mapping)
df = df.sort_values(by=['State_UT', 'Year_Int'])

# Calculate previous year enrollment and growth rate
df['Prev_Enrollment'] = df.groupby('State_UT')['Grand_Total'].shift(1)
df['Growth_Rate'] = (df['Grand_Total'] - df['Prev_Enrollment']) / df['Prev_Enrollment']

# Drop the first year (2019) since it has no previous year data
df_ml = df.dropna(subset=['Prev_Enrollment']).copy()

# 4. Chronological Train/Test Split
print("Splitting Data (Train: 2020-2022, Test: 2023)...")
# Train on 2020-21, 2021-22, 2022-23. Test on 2023-24.
train_df = df_ml[df_ml['Year_Int'] < 2023].copy()
test_df = df_ml[df_ml['Year_Int'] == 2023].copy()

# Features and Target
features = ['Year_Int', 'Prev_Enrollment', 'State_UT']
target = 'Grand_Total'

X_train = train_df[features]
y_train = train_df[target]
X_test = test_df[features]
y_test = test_df[target]

# One-hot encode State_UT
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoded_states_train = pd.DataFrame(encoder.fit_transform(X_train[['State_UT']]), columns=encoder.get_feature_names_out())
encoded_states_test = pd.DataFrame(encoder.transform(X_test[['State_UT']]), columns=encoder.get_feature_names_out())

X_train_processed = pd.concat([X_train.drop('State_UT', axis=1).reset_index(drop=True), encoded_states_train], axis=1)
X_test_processed = pd.concat([X_test.drop('State_UT', axis=1).reset_index(drop=True), encoded_states_test], axis=1)

# 5. Model Training & Evaluation
print("Training Models...")

def evaluate_model(name, model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"--- {name} ---")
    print(f"RMSE: {rmse:,.2f}")
    print(f"MAE:  {mae:,.2f}")
    print(f"R²:   {r2:.4f}")
    return model, r2

lr_model, lr_r2 = evaluate_model("Linear Regression", LinearRegression(), X_train_processed, y_train, X_test_processed, y_test)
rf_model, rf_r2 = evaluate_model("Random Forest", RandomForestRegressor(random_state=42), X_train_processed, y_train, X_test_processed, y_test)

best_model = "Random Forest" if rf_r2 > lr_r2 else "Linear Regression"
print(f"\nBest Model: {best_model}")

print("\nML Pipeline completed successfully.")
