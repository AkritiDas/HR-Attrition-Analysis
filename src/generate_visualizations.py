import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set global aesthetic style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# Palette definition
PRIMARY_COLOR = '#1e3a8a'     # Deep Navy
SECONDARY_COLOR = '#ef4444'   # Coral Red (Attrition)
RETAINED_COLOR = '#10b981'    # Emerald Green (Retained)
ACCENT_BLUE = '#3b82f6'       # Vibrant Blue
BG_CARD = '#f8fafc'

def create_all_visualizations(csv_path="data/hr_employee_attrition_cleaned.csv", output_dir="reports/figures"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)
    
    print("=== Generating High-Quality HR Attrition Charts ===")
    
    # -------------------------------------------------------------
    # 1. Overall Attrition Donut Chart
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 7), dpi=300)
    counts = df['Attrition'].value_counts()
    labels = [f"Retained ({counts.get('No', 0)})", f"Left ({counts.get('Yes', 0)})"]
    colors = [RETAINED_COLOR, SECONDARY_COLOR]
    
    wedges, texts, autotexts = ax.pie(
        [counts.get('No', 0), counts.get('Yes', 0)],
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        explode=(0, 0.05),
        textprops=dict(color="#1e293b", fontsize=11, weight='bold')
    )
    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.55, fc='white')
    ax.add_artist(centre_circle)
    
    # Text inside donut hole
    total = len(df)
    att_rate = (counts.get('Yes', 0) / total) * 100
    ax.text(0, 0.08, f"{att_rate:.1f}%", ha='center', va='center', fontsize=26, weight='bold', color=SECONDARY_COLOR)
    ax.text(0, -0.12, "Attrition Rate", ha='center', va='center', fontsize=12, color='#64748b', weight='bold')
    
    ax.set_title("Overall HR Employee Attrition Overview\n(Total Workforce: 1,470)", fontsize=14, weight='bold', pad=20, color=PRIMARY_COLOR)
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "01_overall_attrition_donut.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Chart 1 saved: {chart1_path}")
    
    # -------------------------------------------------------------
    # 2. Attrition Rate by Department
    # -------------------------------------------------------------
    dept_df = df.groupby('Department', observed=False)['Attrition_Flag'].agg(['count', 'mean']).reset_index()
    dept_df['Attrition_Rate'] = dept_df['mean'] * 100
    dept_df = dept_df.sort_values(by='Attrition_Rate', ascending=False)
    
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    bars = ax.bar(dept_df['Department'], dept_df['Attrition_Rate'], color=ACCENT_BLUE, width=0.5, edgecolor=PRIMARY_COLOR, linewidth=1)
    
    # Highlight top risk
    bars[0].set_color(SECONDARY_COLOR)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, weight='bold', color='#0f172a')
                    
    ax.set_ylim(0, max(dept_df['Attrition_Rate']) * 1.2)
    ax.set_ylabel("Attrition Rate (%)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_title("Employee Attrition Rate by Department", fontsize=14, weight='bold', pad=15, color=PRIMARY_COLOR)
    ax.axhline(att_rate, color=SECONDARY_COLOR, linestyle='--', linewidth=1.2, label=f'Company Average ({att_rate:.1f}%)')
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "02_attrition_by_department.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Chart 2 saved: {chart2_path}")

    # -------------------------------------------------------------
    # 3. Attrition Rate by Salary Range
    # -------------------------------------------------------------
    sal_order = ['<$3,000', '$3,000-$5,000', '$5,000-$10,000', '$10,000-$15,000', '$15,000+']
    sal_df = df.groupby('Salary_Range', observed=False)['Attrition_Flag'].agg(['count', 'mean']).reindex(sal_order).reset_index()
    sal_df['Attrition_Rate'] = sal_df['mean'] * 100
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    colors_sal = ['#b91c1c', '#ef4444', '#f97316', '#3b82f6', '#10b981']
    bars = ax.bar(sal_df['Salary_Range'], sal_df['Attrition_Rate'], color=colors_sal, width=0.55, edgecolor='#334155', linewidth=1)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, weight='bold')
                    
    ax.set_ylim(0, max(sal_df['Attrition_Rate']) * 1.18)
    ax.set_ylabel("Attrition Rate (%)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_xlabel("Monthly Salary Range", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_title("Attrition Rate by Salary Bracket\n(Lower Income Groups Experience Significantly Higher Turnover)", fontsize=13, weight='bold', pad=15, color=PRIMARY_COLOR)
    ax.axhline(att_rate, color='#64748b', linestyle='--', linewidth=1.2, label=f'Avg Attrition ({att_rate:.1f}%)')
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "03_attrition_by_salary_range.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Chart 3 saved: {chart3_path}")

    # -------------------------------------------------------------
    # 4. Attrition Rate by Experience/Tenure Group
    # -------------------------------------------------------------
    ten_order = ['0-2 Years', '3-5 Years', '6-10 Years', '10+ Years']
    ten_df = df.groupby('Tenure_Group', observed=False)['Attrition_Flag'].agg(['count', 'mean']).reindex(ten_order).reset_index()
    ten_df['Attrition_Rate'] = ten_df['mean'] * 100
    
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.plot(ten_df['Tenure_Group'], ten_df['Attrition_Rate'], marker='o', markersize=10, markerfacecolor=SECONDARY_COLOR, color=PRIMARY_COLOR, linewidth=3, label='Attrition Rate (%)')
    
    for i, txt in enumerate(ten_df['Attrition_Rate']):
        ax.annotate(f'{txt:.1f}%', (ten_df['Tenure_Group'][i], ten_df['Attrition_Rate'][i]),
                    textcoords="offset points", xytext=(0,12), ha='center', fontsize=11, weight='bold', color='#1e293b')
                    
    ax.set_ylim(0, max(ten_df['Attrition_Rate']) * 1.2)
    ax.set_ylabel("Attrition Rate (%)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_xlabel("Years at Company (Tenure Group)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_title("Attrition Rate vs Employee Tenure\n(New Hires <= 2 Years Face Critical Retention Risk)", fontsize=13, weight='bold', pad=15, color=PRIMARY_COLOR)
    ax.fill_between(ten_df['Tenure_Group'], ten_df['Attrition_Rate'], color=ACCENT_BLUE, alpha=0.15)
    plt.tight_layout()
    chart4_path = os.path.join(output_dir, "04_attrition_by_experience.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"Chart 4 saved: {chart4_path}")

    # -------------------------------------------------------------
    # 5. Attrition Rate by Job Role (Horizontal Bar Chart)
    # -------------------------------------------------------------
    role_df = df.groupby('JobRole', observed=False)['Attrition_Flag'].agg(['count', 'mean']).reset_index()
    role_df['Attrition_Rate'] = role_df['mean'] * 100
    role_df = role_df.sort_values(by='Attrition_Rate', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    colors_role = [SECONDARY_COLOR if val > 45 else ACCENT_BLUE for val in role_df['Attrition_Rate']]
    bars = ax.barh(role_df['JobRole'], role_df['Attrition_Rate'], color=colors_role, height=0.6, edgecolor=PRIMARY_COLOR, linewidth=0.8)
    
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(6, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10, weight='bold', color='#0f172a')
                    
    ax.set_xlim(0, max(role_df['Attrition_Rate']) * 1.18)
    ax.set_xlabel("Attrition Rate (%)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_title("Attrition Rate Breakdown by Job Role", fontsize=13, weight='bold', pad=15, color=PRIMARY_COLOR)
    ax.axvline(att_rate, color='#64748b', linestyle='--', linewidth=1.2, label=f'Avg Attrition ({att_rate:.1f}%)')
    ax.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    chart5_path = os.path.join(output_dir, "05_attrition_by_job_role.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f"Chart 5 saved: {chart5_path}")

    # -------------------------------------------------------------
    # 6. Attrition Rate by Overtime & Job Satisfaction
    # -------------------------------------------------------------
    ot_sat = df.groupby(['Overtime', 'Satisfaction_Label'], observed=False)['Attrition_Flag'].mean().unstack() * 100
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ot_sat.plot(kind='bar', ax=ax, colormap='Blues_r', width=0.7, edgecolor='#334155', linewidth=0.8)
    
    ax.set_ylabel("Attrition Rate (%)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_xlabel("Overtime Requirement", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_title("Attrition Rate by Overtime Status & Job Satisfaction Level", fontsize=13, weight='bold', pad=15, color=PRIMARY_COLOR)
    ax.set_xticklabels(['No Overtime', 'Works Overtime'], rotation=0, fontsize=11, weight='bold')
    ax.legend(title="Job Satisfaction", frameon=True)
    ax.set_ylim(0, max(ot_sat.max()) * 1.15)
    
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(f'{h:.1f}%', (p.get_x() + p.get_width() / 2., h),
                        ha='center', va='bottom', fontsize=9, xytext=(0, 3),
                        textcoords='offset points', weight='bold')
                        
    plt.tight_layout()
    chart6_path = os.path.join(output_dir, "06_attrition_by_overtime_satisfaction.png")
    plt.savefig(chart6_path, dpi=300)
    plt.close()
    print(f"Chart 6 saved: {chart6_path}")

    # -------------------------------------------------------------
    # 7. Attrition Rate by Age Group
    # -------------------------------------------------------------
    age_order = ['18-25', '26-35', '36-45', '46-55', '55+']
    age_df = df.groupby('Age_Group', observed=False)['Attrition_Flag'].agg(['count', 'mean']).reindex(age_order).reset_index()
    age_df['Attrition_Rate'] = age_df['mean'] * 100
    
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    bars = ax.bar(age_df['Age_Group'], age_df['Attrition_Rate'], color='#6366f1', width=0.55, edgecolor=PRIMARY_COLOR, linewidth=1)
    bars[0].set_color(SECONDARY_COLOR) # highlight 18-25
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, weight='bold')
                    
    ax.set_ylim(0, max(age_df['Attrition_Rate']) * 1.18)
    ax.set_ylabel("Attrition Rate (%)", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_xlabel("Age Group", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_title("Employee Attrition Rate by Age Bracket", fontsize=13, weight='bold', pad=15, color=PRIMARY_COLOR)
    ax.axhline(att_rate, color='#64748b', linestyle='--', linewidth=1.2, label=f'Avg Attrition ({att_rate:.1f}%)')
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    chart7_path = os.path.join(output_dir, "07_attrition_by_age_group.png")
    plt.savefig(chart7_path, dpi=300)
    plt.close()
    print(f"Chart 7 saved: {chart7_path}")

    # -------------------------------------------------------------
    # 8. Correlation Heatmap of Numeric Features with Attrition
    # -------------------------------------------------------------
    num_df = df[['Attrition_Flag', 'Age', 'MonthlyIncome', 'YearsAtCompany', 'TotalWorkingYears', 'JobSatisfaction', 'WorkLifeBalance', 'JobLevel']].copy()
    corr = num_df.corr()
    
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax, linewidths=0.5, vmin=-0.5, vmax=0.5, annot_kws={"weight": "bold", "size": 10})
    ax.set_title("Correlation Heatmap: Key HR Factors vs Attrition Flag", fontsize=13, weight='bold', pad=15, color=PRIMARY_COLOR)
    plt.tight_layout()
    chart8_path = os.path.join(output_dir, "08_correlation_heatmap.png")
    plt.savefig(chart8_path, dpi=300)
    plt.close()
    print(f"Chart 8 saved: {chart8_path}")

if __name__ == "__main__":
    create_all_visualizations()
