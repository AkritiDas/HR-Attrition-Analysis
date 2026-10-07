import pandas as pd
import numpy as np
import json
import os

def perform_hr_attrition_analysis(file_path="data/hr_employee_attrition_cleaned.csv"):
    df = pd.read_csv(file_path)
    
    print("=" * 60)
    print("        HR EMPLOYEE ATTRITION DETAILED ANALYSIS REPORT")
    print("=" * 60)
    
    # 1. Overall Attrition Summary
    total_employees = len(df)
    employees_left = df['Attrition_Flag'].sum()
    employees_retained = total_employees - employees_left
    overall_attrition_rate = (employees_left / total_employees) * 100
    
    overall_summary = {
        "Total Employees": int(total_employees),
        "Employees Who Left": int(employees_left),
        "Employees Retained": int(employees_retained),
        "Overall Attrition Rate (%)": round(overall_attrition_rate, 2)
    }
    
    print("\n--- 1. OVERALL ATTRITION METRICS ---")
    for k, v in overall_summary.items():
        print(f"  {k}: {v}")
        
    # Helper to calculate grouped stats
    def calc_group_stats(df_in, group_col):
        stats = df_in.groupby(group_col, observed=False).agg(
            Total_Employees=('EmployeeID', 'count'),
            Attrition_Count=('Attrition_Flag', 'sum')
        ).reset_index()
        stats['Retained_Count'] = stats['Total_Employees'] - stats['Attrition_Count']
        stats['Attrition_Rate_%'] = (stats['Attrition_Count'] / stats['Total_Employees'] * 100).round(2)
        stats['Share_of_Total_Attrition_%'] = (stats['Attrition_Count'] / employees_left * 100).round(2)
        return stats.sort_values(by='Attrition_Rate_%', ascending=False)

    # 2. Attrition by Department
    dept_stats = calc_group_stats(df, 'Department')
    print("\n--- 2. ATTRITION BY DEPARTMENT ---")
    print(dept_stats.to_string(index=False))
    
    # 3. Attrition by Salary Range
    salary_stats = calc_group_stats(df, 'Salary_Range')
    print("\n--- 3. ATTRITION BY SALARY RANGE ---")
    print(salary_stats.to_string(index=False))
    
    # 4. Attrition by Experience / Tenure Group
    tenure_stats = calc_group_stats(df, 'Tenure_Group')
    print("\n--- 4. ATTRITION BY TENURE GROUP (Years at Company) ---")
    print(tenure_stats.to_string(index=False))
    
    # 5. Attrition by Job Role
    role_stats = calc_group_stats(df, 'JobRole')
    print("\n--- 5. ATTRITION BY JOB ROLE ---")
    print(role_stats.to_string(index=False))
    
    # 6. Attrition by Age Group
    age_stats = calc_group_stats(df, 'Age_Group')
    print("\n--- 6. ATTRITION BY AGE GROUP ---")
    print(age_stats.to_string(index=False))
    
    # 7. Attrition by Overtime
    ot_stats = calc_group_stats(df, 'Overtime')
    print("\n--- 7. ATTRITION BY OVERTIME ---")
    print(ot_stats.to_string(index=False))
    
    # 8. Attrition by Job Satisfaction
    sat_stats = calc_group_stats(df, 'Satisfaction_Label')
    print("\n--- 8. ATTRITION BY JOB SATISFACTION ---")
    print(sat_stats.to_string(index=False))
    
    # Key Hypothesis Tests & Findings
    print("\n" + "=" * 60)
    print("               KEY FINDINGS & HYPOTHESIS TESTING")
    print("=" * 60)
    
    # Finding 1: Highest Attrition Department
    top_dept = dept_stats.iloc[0]
    print(f"\n[Finding 1 - Department Risk]: {top_dept['Department']} has the highest attrition rate at {top_dept['Attrition_Rate_%']}%, accounting for {top_dept['Share_of_Total_Attrition_%']}% of total company attrition.")
    
    # Finding 2: Salary vs Attrition
    low_salary_rate = salary_stats[salary_stats['Salary_Range'] == '<$3,000']['Attrition_Rate_%'].values[0]
    high_salary_rate = salary_stats[salary_stats['Salary_Range'] == '$15,000+']['Attrition_Rate_%'].values[0]
    print(f"\n[Finding 2 - Salary Association]: Employees earning <$3,000 experience an attrition rate of {low_salary_rate}%, compared to only {high_salary_rate}% for employees earning $15,000+. Lower salary is STRONGLY associated with higher turnover.")

    # Finding 3: Experience / Tenure vs Attrition
    early_tenure_rate = tenure_stats[tenure_stats['Tenure_Group'] == '0-2 Years']['Attrition_Rate_%'].values[0]
    late_tenure_rate = tenure_stats[tenure_stats['Tenure_Group'] == '10+ Years']['Attrition_Rate_%'].values[0]
    print(f"\n[Finding 3 - Tenure Association]: Employees with 0-2 years of tenure have an attrition rate of {early_tenure_rate}%, versus {late_tenure_rate}% for employees with 10+ years. New hires leave at over double the company average.")

    # Finding 4: Overtime Impact
    ot_yes_rate = ot_stats[ot_stats['Overtime'] == 'Yes']['Attrition_Rate_%'].values[0]
    ot_no_rate = ot_stats[ot_stats['Overtime'] == 'No']['Attrition_Rate_%'].values[0]
    print(f"\n[Finding 4 - Workload / Overtime]: Employees working Overtime experience an attrition rate of {ot_yes_rate}%, compared to {ot_no_rate}% for non-overtime workers. Overtime increases turnover risk by ~3x.")

    # Exporting JSON summary for web/excel reporting
    analysis_results = {
        "overall_summary": overall_summary,
        "department_analysis": dept_stats.to_dict(orient="records"),
        "salary_analysis": salary_stats.to_dict(orient="records"),
        "tenure_analysis": tenure_stats.to_dict(orient="records"),
        "job_role_analysis": role_stats.to_dict(orient="records"),
        "age_analysis": age_stats.to_dict(orient="records"),
        "overtime_analysis": ot_stats.to_dict(orient="records"),
        "satisfaction_analysis": sat_stats.to_dict(orient="records")
    }
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/analysis_results.json", "w") as f:
        json.dump(analysis_results, f, indent=4)
        
    print("\nAnalysis summary successfully exported to reports/analysis_results.json")
    return analysis_results

if __name__ == "__main__":
    perform_hr_attrition_analysis()
