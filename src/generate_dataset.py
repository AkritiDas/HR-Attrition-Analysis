import numpy as np
import pandas as pd
import os

def generate_hr_dataset(seed=42, num_records=1470):
    np.random.seed(seed)
    
    # 1. Basic Demographics
    emp_ids = [f"EMP-{1001 + i}" for i in range(num_records)]
    ages = np.random.randint(18, 61, size=num_records)
    genders = np.random.choice(["Male", "Female"], size=num_records, p=[0.60, 0.40])
    marital_statuses = np.random.choice(["Single", "Married", "Divorced"], size=num_records, p=[0.32, 0.46, 0.22])
    education_levels = np.random.choice([1, 2, 3, 4, 5], size=num_records, p=[0.12, 0.19, 0.39, 0.27, 0.03])
    
    # 2. Departments and Job Roles
    departments = np.random.choice(["Research & Development", "Sales", "Human Resources"], size=num_records, p=[0.65, 0.28, 0.07])
    
    job_roles = []
    job_levels = []
    monthly_incomes = []
    
    for dept in departments:
        if dept == "Research & Development":
            role = np.random.choice(
                ["Research Scientist", "Laboratory Technician", "Manufacturing Director", "Healthcare Representative", "Research Director", "Manager"],
                p=[0.35, 0.32, 0.14, 0.12, 0.04, 0.03]
            )
        elif dept == "Sales":
            role = np.random.choice(
                ["Sales Executive", "Sales Representative", "Manager"],
                p=[0.65, 0.28, 0.07]
            )
        else: # HR
            role = np.random.choice(
                ["Human Resources", "Manager"],
                p=[0.80, 0.20]
            )
        job_roles.append(role)
        
        # Assign job level based on role
        if role in ["Manager", "Research Director"]:
            level = np.random.choice([4, 5], p=[0.6, 0.4])
            income = np.random.randint(14000, 20001)
        elif role in ["Manufacturing Director", "Healthcare Representative"]:
            level = np.random.choice([2, 3], p=[0.4, 0.6])
            income = np.random.randint(6000, 13500)
        elif role in ["Sales Executive", "Research Scientist"]:
            level = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
            income = np.random.randint(4000, 9500)
        elif role in ["Sales Representative", "Laboratory Technician", "Human Resources"]:
            level = 1
            income = np.random.randint(2000, 4800)
        else:
            level = 2
            income = np.random.randint(3500, 7500)
            
        job_levels.append(level)
        monthly_incomes.append(income)
        
    # 3. Work Experience & Tenure
    total_working_years = []
    years_at_company = []
    
    for age, level in zip(ages, job_levels):
        max_possible_work = max(0, age - 18)
        work_years = min(max_possible_work, int(np.random.gamma(shape=2.2 + level*0.8, scale=2.5)))
        company_years = min(work_years, int(np.random.beta(a=1.2, b=2.2) * (work_years + 1)))
        total_working_years.append(work_years)
        years_at_company.append(company_years)
        
    # 4. Satisfaction & Workload
    job_satisfaction = np.random.choice([1, 2, 3, 4], size=num_records, p=[0.19, 0.19, 0.31, 0.31])
    work_life_balance = np.random.choice([1, 2, 3, 4], size=num_records, p=[0.06, 0.23, 0.61, 0.10])
    overtime = np.random.choice(["Yes", "No"], size=num_records, p=[0.28, 0.72])
    performance_rating = np.random.choice([3, 4], size=num_records, p=[0.84, 0.16])
    
    # 5. Realistic HR Attrition Logic (Target overall attrition rate ~16.1%)
    attrition = []
    for i in range(num_records):
        base_log_odds = -2.4  # Baseline ~8%
        
        # Overtime effect
        if overtime[i] == "Yes":
            base_log_odds += 1.45  # ~3.5x higher odds
            
        # Monthly Income effect
        if monthly_incomes[i] < 3000:
            base_log_odds += 1.2
        elif monthly_incomes[i] < 5000:
            base_log_odds += 0.6
        elif monthly_incomes[i] > 12000:
            base_log_odds -= 0.9
            
        # Years at Company effect
        if years_at_company[i] <= 2:
            base_log_odds += 1.1
        elif years_at_company[i] >= 8:
            base_log_odds -= 0.8
            
        # Job Satisfaction effect
        if job_satisfaction[i] == 1:
            base_log_odds += 1.2
        elif job_satisfaction[i] == 2:
            base_log_odds += 0.5
        elif job_satisfaction[i] == 4:
            base_log_odds -= 0.6
            
        # Role & Department risk factors
        if job_roles[i] in ["Sales Representative", "Laboratory Technician"]:
            base_log_odds += 0.75
        elif job_roles[i] in ["Manager", "Research Director"]:
            base_log_odds -= 0.7
            
        # Age group risk factors (Younger employees job hop more)
        if ages[i] <= 25:
            base_log_odds += 0.8
        elif ages[i] >= 50:
            base_log_odds -= 0.4
            
        # Work life balance risk
        if work_life_balance[i] == 1:
            base_log_odds += 0.9
            
        prob = 1 / (1 + np.exp(-base_log_odds))
        att_val = "Yes" if np.random.rand() < prob else "No"
        attrition.append(att_val)
        
    df = pd.DataFrame({
        "EmployeeID": emp_ids,
        "Age": ages,
        "Gender": genders,
        "Department": departments,
        "JobRole": job_roles,
        "MonthlyIncome": monthly_incomes,
        "YearsAtCompany": years_at_company,
        "TotalWorkingYears": total_working_years,
        "JobLevel": job_levels,
        "JobSatisfaction": job_satisfaction,
        "WorkLifeBalance": work_life_balance,
        "Overtime": overtime,
        "MaritalStatus": marital_statuses,
        "Education": education_levels,
        "PerformanceRating": performance_rating,
        "Attrition": attrition
    })
    
    # Introduce deliberate noise/dirty data for cleaning demonstration:
    dirty_indices = np.random.choice(num_records, 25, replace=False)
    for idx in dirty_indices[:10]:
        df.loc[idx, "Department"] = df.loc[idx, "Department"] + " "
    for idx in dirty_indices[10:18]:
        df.loc[idx, "Overtime"] = df.loc[idx, "Overtime"].lower()
        
    missing_income_idx = np.random.choice(num_records, 12, replace=False)
    missing_wlb_idx = np.random.choice(num_records, 8, replace=False)
    df.loc[missing_income_idx, "MonthlyIncome"] = np.nan
    df.loc[missing_wlb_idx, "WorkLifeBalance"] = np.nan
    
    duplicates = df.iloc[:5].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    os.makedirs("data", exist_ok=True)
    raw_path = os.path.join("data", "hr_employee_attrition_raw.csv")
    df.to_csv(raw_path, index=False)
    print(f"Realistic HR dataset generated at {raw_path} (Shape: {df.shape})")

if __name__ == "__main__":
    generate_hr_dataset()
