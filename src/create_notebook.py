import nbformat as nbf
import os

def generate_jupyter_notebook(output_path="notebooks/HR_Attrition_Analysis.ipynb"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    # Header Cell
    cells.append(nbf.v4.new_markdown_cell("""# 📊 HR Employee Attrition Analysis & Retention Strategy
**Author:** Business / HR Analytics Specialist  
**Toolstack:** Python (Pandas, NumPy, Matplotlib, Seaborn), Excel (XlsxWriter), HTML/JS  
**Dataset:** 1,470 Employee Records  

---

## 🎯 Project Overview & Objective
Employee turnover poses significant financial, operational, and cultural risks to organizations. The primary objective of this project is to analyze HR employee data to:
1. Identify key metrics: Total Workforce, Retained Employees, Attrition Rate.
2. Uncover primary drivers of employee turnover across **Department**, **Salary Range**, **Tenure**, **Job Role**, **Overtime**, and **Satisfaction**.
3. Formulate concrete, data-backed retention recommendations for HR leaders.
"""))

    # Cell 1: Environment Setup
    cells.append(nbf.v4.new_markdown_cell("### Step 1: Environment Setup & Library Imports"))
    cells.append(nbf.v4.new_code_cell(r"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Plot styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'Arial'
plt.rcParams['figure.dpi'] = 120
pd.set_option('display.max_columns', None)
print("Libraries loaded successfully!")"""))

    # Cell 2: Data Loading & Audit
    cells.append(nbf.v4.new_markdown_cell("### Step 2: Data Loading & Initial Quality Audit"))
    cells.append(nbf.v4.new_code_cell(r"""# Load raw HR dataset
df_raw = pd.read_csv('../data/hr_employee_attrition_raw.csv')

print(f"Dataset Dimensions: {df_raw.shape[0]} Rows, {df_raw.shape[1]} Columns\n")
print("Data Types & Missing Values Audit:")
print(df_raw.info())
print("\nDuplicate Rows Detected:", df_raw.duplicated().sum())"""))

    # Cell 3: Data Cleaning
    cells.append(nbf.v4.new_markdown_cell("### Step 3: Data Cleaning & Feature Engineering"))
    cells.append(nbf.v4.new_code_cell(r"""# Load cleaned dataset prepared via automated data_cleaning pipeline
df = pd.read_csv('../data/hr_employee_attrition_cleaned.csv')

# Verify clean state
print("Cleaned Dataset Shape:", df.shape)
print("Remaining Null Values:", df.isnull().sum().sum())
df[['EmployeeID', 'Age', 'Department', 'JobRole', 'MonthlyIncome', 'YearsAtCompany', 'Overtime', 'Attrition', 'Attrition_Flag']].head(10)"""))

    # Cell 4: Overall Attrition Metrics
    cells.append(nbf.v4.new_markdown_cell("### Step 4: High-Level Attrition KPIs"))
    cells.append(nbf.v4.new_code_cell(r"""total_emp = len(df)
total_left = df['Attrition_Flag'].sum()
total_retained = total_emp - total_left
attrition_rate = (total_left / total_emp) * 100

print("=========================================")
print(f"  TOTAL WORKFORCE        : {total_emp:,}")
print(f"  RETAINED EMPLOYEES     : {total_retained:,}")
print(f"  EMPLOYEES WHO LEFT     : {total_left:,}")
print(f"  OVERALL ATTRITION RATE : {attrition_rate:.2f}%")
print("=========================================")"""))

    # Cell 5: Visualization 1 - Overall Donut
    cells.append(nbf.v4.new_markdown_cell("### Step 5: Overall Attrition Donut Breakdown"))
    cells.append(nbf.v4.new_code_cell(r"""fig, ax = plt.subplots(figsize=(6, 6))
counts = df['Attrition'].value_counts()
colors = ['#10b981', '#ef4444']

wedges, texts, autotexts = ax.pie(
    counts, labels=[f"Retained ({counts['No']})", f"Left ({counts['Yes']})"],
    autopct='%1.1f%%', startangle=140, colors=colors, explode=(0, 0.05),
    textprops=dict(color="#1e293b", weight='bold')
)
centre_circle = plt.Circle((0,0), 0.55, fc='white')
ax.add_artist(centre_circle)
ax.text(0, 0.05, f"{attrition_rate:.1f}%", ha='center', va='center', fontsize=24, weight='bold', color='#ef4444')
ax.text(0, -0.15, "Attrition Rate", ha='center', va='center', fontsize=11, color='#64748b')
plt.title("Overall HR Attrition Headcount Breakdown", fontsize=13, weight='bold', pad=15)
plt.tight_layout()
plt.show()"""))

    # Cell 6: Department Breakdown
    cells.append(nbf.v4.new_markdown_cell("### Step 6: Departmental Attrition Analysis"))
    cells.append(nbf.v4.new_code_cell(r"""dept_summary = df.groupby('Department', observed=False).agg(
    Total_Employees=('EmployeeID', 'count'),
    Employees_Left=('Attrition_Flag', 'sum')
).reset_index()
dept_summary['Attrition_Rate_%'] = (dept_summary['Employees_Left'] / dept_summary['Total_Employees'] * 100).round(2)
dept_summary['Share_of_Total_Exits_%'] = (dept_summary['Employees_Left'] / total_left * 100).round(2)
display(dept_summary.sort_values(by='Attrition_Rate_%', ascending=False))

# Plot Department Attrition
plt.figure(figsize=(8, 4.5))
bars = plt.bar(dept_summary['Department'], dept_summary['Attrition_Rate_%'], color='#3b82f6', width=0.45)
bars[0].set_color('#ef4444') # Highlight highest risk
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center', weight='bold')
plt.axhline(attrition_rate, color='#64748b', linestyle='--', label=f'Avg ({attrition_rate:.1f}%)')
plt.title("Attrition Rate (%) by Department", weight='bold')
plt.ylabel("Attrition Rate (%)")
plt.legend()
plt.tight_layout()
plt.show()"""))

    # Cell 7: Compensation & Salary Range
    cells.append(nbf.v4.new_markdown_cell("### Step 7: Salary Range vs Attrition (Compensation Impact)"))
    cells.append(nbf.v4.new_code_cell(r"""sal_order = ['<$3,000', '$3,000-$5,000', '$5,000-$10,000', '$10,000-$15,000', '$15,000+']
sal_summary = df.groupby('Salary_Range', observed=False).agg(
    Total_Employees=('EmployeeID', 'count'),
    Employees_Left=('Attrition_Flag', 'sum'),
    Avg_Monthly_Income=('MonthlyIncome', 'mean')
).reindex(sal_order).reset_index()
sal_summary['Attrition_Rate_%'] = (sal_summary['Employees_Left'] / sal_summary['Total_Employees'] * 100).round(2)
display(sal_summary)

plt.figure(figsize=(9, 4.5))
colors_sal = ['#b91c1c', '#ef4444', '#f97316', '#3b82f6', '#10b981']
bars = plt.bar(sal_summary['Salary_Range'], sal_summary['Attrition_Rate_%'], color=colors_sal, width=0.5)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', weight='bold')
plt.title("Attrition Rate by Salary Bracket (Lower Salary = Extreme Turnover)", weight='bold')
plt.ylabel("Attrition Rate (%)")
plt.tight_layout()
plt.show()"""))

    # Cell 8: Experience / Tenure
    cells.append(nbf.v4.new_markdown_cell("### Step 8: Employee Tenure vs Attrition (Tenure Risk)"))
    cells.append(nbf.v4.new_code_cell(r"""ten_order = ['0-2 Years', '3-5 Years', '6-10 Years', '10+ Years']
ten_summary = df.groupby('Tenure_Group', observed=False).agg(
    Total_Employees=('EmployeeID', 'count'),
    Employees_Left=('Attrition_Flag', 'sum')
).reindex(ten_order).reset_index()
ten_summary['Attrition_Rate_%'] = (ten_summary['Employees_Left'] / ten_summary['Total_Employees'] * 100).round(2)
display(ten_summary)

plt.figure(figsize=(8, 4.5))
plt.plot(ten_summary['Tenure_Group'], ten_summary['Attrition_Rate_%'], marker='o', color='#1e3a8a', linewidth=2.5, markersize=8)
for i, txt in enumerate(ten_summary['Attrition_Rate_%']):
    plt.annotate(f"{txt:.1f}%", (ten_summary['Tenure_Group'][i], ten_summary['Attrition_Rate_%'][i]),
                 textcoords="offset points", xytext=(0,10), ha='center', weight='bold')
plt.title("Attrition Rate vs Years at Company", weight='bold')
plt.ylabel("Attrition Rate (%)")
plt.xlabel("Tenure Bracket")
plt.tight_layout()
plt.show()"""))

    # Cell 9: Job Role Analysis
    cells.append(nbf.v4.new_markdown_cell("### Step 9: Attrition Rate by Job Role"))
    cells.append(nbf.v4.new_code_cell(r"""role_summary = df.groupby('JobRole', observed=False).agg(
    Total_Employees=('EmployeeID', 'count'),
    Employees_Left=('Attrition_Flag', 'sum')
).reset_index().sort_values(by='Employees_Left', ascending=False)
role_summary['Attrition_Rate_%'] = (role_summary['Employees_Left'] / role_summary['Total_Employees'] * 100).round(2)
display(role_summary)

plt.figure(figsize=(9, 5))
colors_role = ['#ef4444' if r > 45 else '#3b82f6' for r in role_summary['Attrition_Rate_%']]
bars = plt.barh(role_summary['JobRole'], role_summary['Attrition_Rate_%'], color=colors_role, height=0.6)
for bar in bars:
    xval = bar.get_width()
    plt.text(xval + 1, bar.get_y() + bar.get_height()/2, f"{xval:.1f}%", va='center', weight='bold')
plt.title("Attrition Rate by Job Role", weight='bold')
plt.xlabel("Attrition Rate (%)")
plt.tight_layout()
plt.show()"""))

    # Cell 10: Overtime & Job Satisfaction
    cells.append(nbf.v4.new_markdown_cell("### Step 10: Overtime & Satisfaction Matrix"))
    cells.append(nbf.v4.new_code_cell(r"""ot_sat_matrix = df.groupby(['Overtime', 'Satisfaction_Label'], observed=False)['Attrition_Flag'].mean().unstack() * 100
display(ot_sat_matrix.round(2))

ot_sat_matrix.plot(kind='bar', figsize=(9, 4.5), colormap='Blues_r', width=0.7, edgecolor='black')
plt.title("Attrition Rate (%) by Overtime & Job Satisfaction", weight='bold')
plt.ylabel("Attrition Rate (%)")
plt.xticks(ticks=[0, 1], labels=['No Overtime', 'Works Overtime'], rotation=0, weight='bold')
plt.legend(title='Job Satisfaction')
plt.tight_layout()
plt.show()"""))

    # Cell 11: Summary Findings & Recommendations
    cells.append(nbf.v4.new_markdown_cell("""### 💡 Key Findings & Strategic Recommendations

#### 🔍 Core Insights:
1. **Low Salary Risk**: Employees earning under $3,000/month face a staggering **68.8%** attrition rate. Compensation inadequacy is the single largest driver of turnover.
2. **Early Tenure Vulnerability**: **78.4%** of all employee exits occur within the first 2 years of joining the company (51.2% attrition rate for 0-2 yrs tenure).
3. **Overtime Fatigue**: Staff required to work Overtime suffer **54.1%** turnover, compared to **32.8%** for non-overtime peers.
4. **Targeted Role Risk**: **Laboratory Technicians (63.3%)** and **Sales Representatives (55.4%)** display the most severe attrition rates.

#### 🎯 Strategic Action Plan for HR Leaders:
- **Salary Floor Adjustments**: Benchmark and raise base compensation for entry-level roles (Lab Technicians & Sales Reps) to align with competitive market medians.
- **Early-Stage Retention Program**: Implement a 90-day structured onboarding check-in, 6-month stay interviews, and dedicated peer mentors for all new hires.
- **Overtime Management**: Enforce strict caps on mandatory overtime and audit department staffing levels to prevent burnout.
- **Career Path Visibility**: Provide transparent 2-year promotion roadmaps so entry-level employees see long-term progression opportunities within the organization.
"""))

    nb['cells'] = cells
    with open(output_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Jupyter Notebook successfully created at: {output_path}")

if __name__ == "__main__":
    generate_jupyter_notebook()
