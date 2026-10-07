import pandas as pd
import numpy as np
import os

def clean_hr_data(raw_path="data/hr_employee_attrition_raw.csv", cleaned_path="data/hr_employee_attrition_cleaned.csv"):
    print("=== STEP 1: Loading Raw Data ===")
    df = pd.read_csv(raw_path)
    initial_shape = df.shape
    print(f"Raw Data Shape: {initial_shape[0]} rows, {initial_shape[1]} columns")
    
    print("\n=== STEP 2: Data Quality Audit ===")
    missing_before = df.isnull().sum()
    print("Missing values per column:\n", missing_before[missing_before > 0])
    
    duplicates_before = df.duplicated().sum()
    print(f"Duplicate rows detected: {duplicates_before}")
    
    print("\n=== STEP 3: Cleaning Whitespace & Formatting ===")
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Standardize Overtime and Department capitalization
    df['Overtime'] = df['Overtime'].str.title()
    df['Department'] = df['Department'].str.title()
    # Correct capitalization for R&D if affected
    df['Department'] = df['Department'].replace({'Research & Development': 'Research & Development'})
    
    print("\n=== STEP 4: Handling Duplicates ===")
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Rows after removing duplicates: {len(df)}")
    
    print("\n=== STEP 5: Imputing Missing Values ===")
    # Convert MonthlyIncome back to numeric (in case of string NaNs)
    df['MonthlyIncome'] = pd.to_numeric(df['MonthlyIncome'], errors='coerce')
    df['WorkLifeBalance'] = pd.to_numeric(df['WorkLifeBalance'], errors='coerce')
    
    # Impute MonthlyIncome using JobRole & JobLevel median
    income_medians = df.groupby(['JobRole', 'JobLevel'])['MonthlyIncome'].transform('median')
    df['MonthlyIncome'] = df['MonthlyIncome'].fillna(income_medians)
    # Fallback if any remains
    df['MonthlyIncome'] = df['MonthlyIncome'].fillna(df['MonthlyIncome'].median())
    
    # Impute WorkLifeBalance with mode
    wlb_mode = df['WorkLifeBalance'].mode()[0]
    df['WorkLifeBalance'] = df['WorkLifeBalance'].fillna(wlb_mode)
    
    # Ensure correct integer types
    int_cols = ['Age', 'MonthlyIncome', 'YearsAtCompany', 'TotalWorkingYears', 'JobLevel', 'JobSatisfaction', 'WorkLifeBalance', 'Education', 'PerformanceRating']
    for col in int_cols:
        df[col] = df[col].astype(int)
        
    print("\n=== STEP 6: Feature Engineering (Derived Bins & Flags) ===")
    # 1. Attrition Flag (Numeric 1/0 for easy aggregation)
    df['Attrition_Flag'] = df['Attrition'].apply(lambda x: 1 if str(x).strip().title() == 'Yes' else 0)
    
    # 2. Age Group
    age_bins = [17, 25, 35, 45, 55, 100]
    age_labels = ['18-25', '26-35', '36-45', '46-55', '55+']
    df['Age_Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels)
    
    # 3. Salary Range
    income_bins = [0, 3000, 5000, 10000, 15000, 100000]
    income_labels = ['<$3,000', '$3,000-$5,000', '$5,000-$10,000', '$10,000-$15,000', '$15,000+']
    df['Salary_Range'] = pd.cut(df['MonthlyIncome'], bins=income_bins, labels=income_labels)
    
    # 4. Tenure Group (Years at Company)
    tenure_bins = [-1, 2, 5, 10, 100]
    tenure_labels = ['0-2 Years', '3-5 Years', '6-10 Years', '10+ Years']
    df['Tenure_Group'] = pd.cut(df['YearsAtCompany'], bins=tenure_bins, labels=tenure_labels)
    
    # 5. Satisfaction Label
    satisfaction_map = {1: '1-Low', 2: '2-Medium', 3: '3-High', 4: '4-Very High'}
    df['Satisfaction_Label'] = df['JobSatisfaction'].map(satisfaction_map)
    
    print("\n=== STEP 7: Exporting Cleaned Data ===")
    os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
    df.to_csv(cleaned_path, index=False)
    print(f"Cleaned dataset saved to: {cleaned_path}")
    print(f"Final Cleaned Data Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Total Missing Values Remaining: {df.isnull().sum().sum()}")
    return df

if __name__ == "__main__":
    clean_hr_data()
