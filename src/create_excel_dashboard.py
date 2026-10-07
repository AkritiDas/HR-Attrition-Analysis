import pandas as pd
import xlsxwriter
import json
import os

def build_excel_dashboard(
    cleaned_csv="data/hr_employee_attrition_cleaned.csv",
    output_excel="reports/HR_Attrition_Dashboard.xlsx"
):
    df = pd.read_csv(cleaned_csv)
    
    # Load json stats if available or compute on fly
    total_emp = len(df)
    total_left = df['Attrition_Flag'].sum()
    total_retained = total_emp - total_left
    att_rate = total_left / total_emp
    
    os.makedirs(os.path.dirname(output_excel), exist_ok=True)
    workbook = xlsxwriter.Workbook(output_excel)
    
    # Define Color Palette Formats
    NAVY_HEX = '#1e3a8a'
    HEADER_BLUE = '#2563eb'
    LIGHT_BLUE = '#eff6ff'
    RED_HEX = '#dc2626'
    GREEN_HEX = '#16a34a'
    GRAY_TEXT = '#475569'
    BORDER_GRAY = '#cbd5e1'
    
    # Formats
    fmt_title = workbook.add_format({
        'bold': True, 'font_size': 18, 'font_color': 'white',
        'bg_color': NAVY_HEX, 'align': 'left', 'valign': 'vcenter', 'indent': 1
    })
    fmt_subtitle = workbook.add_format({
        'italic': True, 'font_size': 10, 'font_color': '#e2e8f0',
        'bg_color': NAVY_HEX, 'align': 'left', 'valign': 'vcenter', 'indent': 1
    })
    fmt_kpi_label = workbook.add_format({
        'bold': True, 'font_size': 9, 'font_color': GRAY_TEXT,
        'bg_color': '#f8fafc', 'align': 'center', 'valign': 'center',
        'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_kpi_val = workbook.add_format({
        'bold': True, 'font_size': 18, 'font_color': NAVY_HEX,
        'bg_color': '#ffffff', 'align': 'center', 'valign': 'center',
        'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_kpi_val_red = workbook.add_format({
        'bold': True, 'font_size': 18, 'font_color': RED_HEX,
        'bg_color': '#ffffff', 'align': 'center', 'valign': 'center',
        'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_kpi_val_pct = workbook.add_format({
        'bold': True, 'font_size': 18, 'font_color': RED_HEX,
        'bg_color': '#ffffff', 'align': 'center', 'valign': 'center',
        'num_format': '0.0%', 'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_th = workbook.add_format({
        'bold': True, 'font_size': 10, 'font_color': 'white',
        'bg_color': HEADER_BLUE, 'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_td_text = workbook.add_format({
        'font_size': 10, 'align': 'left', 'valign': 'vcenter',
        'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_td_num = workbook.add_format({
        'font_size': 10, 'align': 'center', 'valign': 'vcenter',
        'num_format': '#,##0', 'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_td_pct = workbook.add_format({
        'font_size': 10, 'align': 'center', 'valign': 'vcenter',
        'num_format': '0.0%', 'border': 1, 'border_color': BORDER_GRAY
    })
    fmt_section_hdr = workbook.add_format({
        'bold': True, 'font_size': 12, 'font_color': NAVY_HEX,
        'bg_color': '#dbeafe', 'align': 'left', 'valign': 'vcenter', 'indent': 1,
        'border': 1, 'border_color': BORDER_GRAY
    })
    
    # -------------------------------------------------------------
    # SHEET 1: Executive Dashboard
    # -------------------------------------------------------------
    ws_dash = workbook.add_worksheet("Executive Dashboard")
    ws_dash.hide_gridlines(0) # Show gridlines cleanly
    
    # Title Block
    ws_dash.merge_range("B2:N2", "  HR EMPLOYEE ATTRITION EXECUTIVE DASHBOARD", fmt_title)
    ws_dash.merge_range("B3:N3", "  Key Performance Indicators, Attrition Drivers & Departmental Breakdown", fmt_subtitle)
    ws_dash.set_row(1, 28)
    ws_dash.set_row(2, 18)
    
    # KPI Cards (Row 5 - 7)
    # Total Employees
    ws_dash.merge_range("B5:D5", "TOTAL WORKFORCE", fmt_kpi_label)
    ws_dash.merge_range("B6:D7", total_emp, fmt_kpi_val)
    
    # Employees Left
    ws_dash.merge_range("F5:H5", "EMPLOYEES LEFT (ATTRITION)", fmt_kpi_label)
    ws_dash.merge_range("F6:H7", total_left, fmt_kpi_val_red)
    
    # Employees Retained
    ws_dash.merge_range("J5:L5", "EMPLOYEES RETAINED", fmt_kpi_label)
    ws_dash.merge_range("J6:L7", total_retained, fmt_kpi_val)
    
    # Attrition Rate
    ws_dash.merge_range("N5:P5", "OVERALL ATTRITION RATE", fmt_kpi_label)
    ws_dash.merge_range("N6:P7", att_rate, fmt_kpi_val_pct)
    
    # Prepare Summary Data Tables on Sheet 1 (hidden or side region) for Native Excel Charts
    # 1. Department Summary Data (Placed at R5:U9)
    dept_stats = df.groupby('Department', observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum')
    ).reset_index()
    dept_stats['Retained'] = dept_stats['Total'] - dept_stats['Left']
    dept_stats['Rate'] = dept_stats['Left'] / dept_stats['Total']
    
    ws_dash.write("R5", "Department", fmt_th)
    ws_dash.write("S5", "Total", fmt_th)
    ws_dash.write("T5", "Left", fmt_th)
    ws_dash.write("U5", "Rate", fmt_th)
    
    for r_idx, row in dept_stats.iterrows():
        row_num = 5 + r_idx + 1
        ws_dash.write(f"R{row_num}", row['Department'], fmt_td_text)
        ws_dash.write(f"S{row_num}", row['Total'], fmt_td_num)
        ws_dash.write(f"T{row_num}", row['Left'], fmt_td_num)
        ws_dash.write(f"U{row_num}", row['Rate'], fmt_td_pct)
        
    # Create Native Column Chart for Department
    chart_dept = workbook.add_chart({'type': 'column'})
    chart_dept.add_series({
        'name': 'Attrition Rate',
        'categories': f"='Executive Dashboard'!$R$6:$R$8",
        'values':     f"='Executive Dashboard'!$U$6:$U$8",
        'fill':       {'color': HEADER_BLUE},
        'data_labels': {'value': True, 'num_format': '0.0%'}
    })
    chart_dept.set_title({'name': 'Attrition Rate by Department'})
    chart_dept.set_y_axis({'name': 'Attrition Rate (%)', 'num_format': '0%'})
    chart_dept.set_legend({'position': 'none'})
    chart_dept.set_size({'width': 450, 'height': 270})
    ws_dash.insert_chart("B10", chart_dept)
    
    # 2. Salary Range Summary Data (Placed at R12:U17)
    sal_order = ['<$3,000', '$3,000-$5,000', '$5,000-$10,000', '$10,000-$15,000', '$15,000+']
    sal_stats = df.groupby('Salary_Range', observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum')
    ).reindex(sal_order).reset_index()
    sal_stats['Rate'] = sal_stats['Left'] / sal_stats['Total']
    
    ws_dash.write("R12", "Salary Range", fmt_th)
    ws_dash.write("S12", "Total", fmt_th)
    ws_dash.write("T12", "Left", fmt_th)
    ws_dash.write("U12", "Rate", fmt_th)
    
    for r_idx, row in sal_stats.iterrows():
        row_num = 12 + r_idx + 1
        ws_dash.write(f"R{row_num}", row['Salary_Range'], fmt_td_text)
        ws_dash.write(f"S{row_num}", row['Total'], fmt_td_num)
        ws_dash.write(f"T{row_num}", row['Left'], fmt_td_num)
        ws_dash.write(f"U{row_num}", row['Rate'], fmt_td_pct)
        
    # Create Native Bar Chart for Salary Range
    chart_sal = workbook.add_chart({'type': 'bar'})
    chart_sal.add_series({
        'name': 'Attrition Rate',
        'categories': f"='Executive Dashboard'!$R$13:$R$17",
        'values':     f"='Executive Dashboard'!$U$13:$U$17",
        'fill':       {'color': RED_HEX},
        'data_labels': {'value': True, 'num_format': '0.0%'}
    })
    chart_sal.set_title({'name': 'Attrition Rate by Salary Bracket'})
    chart_sal.set_x_axis({'name': 'Attrition Rate (%)', 'num_format': '0%'})
    chart_sal.set_legend({'position': 'none'})
    chart_sal.set_size({'width': 450, 'height': 270})
    ws_dash.insert_chart("I10", chart_sal)
    
    # 3. Tenure Group Summary Data (Placed at R20:U24)
    ten_order = ['0-2 Years', '3-5 Years', '6-10 Years', '10+ Years']
    ten_stats = df.groupby('Tenure_Group', observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum')
    ).reindex(ten_order).reset_index()
    ten_stats['Rate'] = ten_stats['Left'] / ten_stats['Total']
    
    ws_dash.write("R20", "Tenure Group", fmt_th)
    ws_dash.write("S20", "Total", fmt_th)
    ws_dash.write("T20", "Left", fmt_th)
    ws_dash.write("U20", "Rate", fmt_th)
    
    for r_idx, row in ten_stats.iterrows():
        row_num = 20 + r_idx + 1
        ws_dash.write(f"R{row_num}", row['Tenure_Group'], fmt_td_text)
        ws_dash.write(f"S{row_num}", row['Total'], fmt_td_num)
        ws_dash.write(f"T{row_num}", row['Left'], fmt_td_num)
        ws_dash.write(f"U{row_num}", row['Rate'], fmt_td_pct)
        
    chart_ten = workbook.add_chart({'type': 'column'})
    chart_ten.add_series({
        'name': 'Attrition Rate',
        'categories': f"='Executive Dashboard'!$R$21:$R$24",
        'values':     f"='Executive Dashboard'!$U$21:$U$24",
        'fill':       {'color': '#6366f1'},
        'data_labels': {'value': True, 'num_format': '0.0%'}
    })
    chart_ten.set_title({'name': 'Attrition Rate by Tenure Group (Years at Company)'})
    chart_ten.set_y_axis({'name': 'Attrition Rate (%)', 'num_format': '0%'})
    chart_ten.set_legend({'position': 'none'})
    chart_ten.set_size({'width': 450, 'height': 270})
    ws_dash.insert_chart("B25", chart_ten)

    # 4. Job Role Summary Data (Placed at R26:U35)
    role_stats = df.groupby('JobRole', observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum')
    ).reset_index().sort_values(by='Left', ascending=False)
    role_stats['Rate'] = role_stats['Left'] / role_stats['Total']
    
    ws_dash.write("R26", "Job Role", fmt_th)
    ws_dash.write("S26", "Total", fmt_th)
    ws_dash.write("T26", "Left", fmt_th)
    ws_dash.write("U26", "Rate", fmt_th)
    
    for r_idx, row in role_stats.iterrows():
        row_num = 26 + r_idx + 1
        ws_dash.write(f"R{row_num}", row['JobRole'], fmt_td_text)
        ws_dash.write(f"S{row_num}", row['Total'], fmt_td_num)
        ws_dash.write(f"T{row_num}", row['Left'], fmt_td_num)
        ws_dash.write(f"U{row_num}", row['Rate'], fmt_td_pct)
        
    chart_role = workbook.add_chart({'type': 'bar'})
    chart_role.add_series({
        'name': 'Attrition Rate',
        'categories': f"='Executive Dashboard'!$R$27:$R$35",
        'values':     f"='Executive Dashboard'!$U$27:$U$35",
        'fill':       {'color': '#0284c7'},
        'data_labels': {'value': True, 'num_format': '0.0%'}
    })
    chart_role.set_title({'name': 'Attrition Rate by Job Role'})
    chart_role.set_x_axis({'name': 'Attrition Rate (%)', 'num_format': '0%'})
    chart_role.set_legend({'position': 'none'})
    chart_role.set_size({'width': 450, 'height': 270})
    ws_dash.insert_chart("I25", chart_role)
    
    # Hide helper data columns R:U
    ws_dash.set_column("R:U", None, None, {'hidden': True})
    ws_dash.set_column("A:A", 3)
    ws_dash.set_column("B:P", 12)

    # -------------------------------------------------------------
    # SHEET 2: Department & Role Breakdown
    # -------------------------------------------------------------
    ws_dept = workbook.add_worksheet("Department & Role Analysis")
    ws_dept.hide_gridlines(0)
    
    ws_dept.merge_range("B2:H2", "DEPARTMENT & JOB ROLE ATTRITION ANALYSIS", fmt_title)
    ws_dept.set_row(1, 26)
    
    # Table Header
    headers = ["Department", "Job Role", "Total Headcount", "Retained", "Attrited (Left)", "Attrition Rate (%)", "Risk Level"]
    for c_idx, h in enumerate(headers):
        ws_dept.write(3, 1 + c_idx, h, fmt_th)
        
    row_curr = 4
    dept_role_df = df.groupby(['Department', 'JobRole'], observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum')
    ).reset_index().sort_values(by=['Department', 'Left'], ascending=[True, False])
    dept_role_df['Retained'] = dept_role_df['Total'] - dept_role_df['Left']
    dept_role_df['Rate'] = dept_role_df['Left'] / dept_role_df['Total']
    
    for _, row in dept_role_df.iterrows():
        rate = row['Rate']
        risk = "HIGH RISK" if rate >= 0.45 else ("MEDIUM RISK" if rate >= 0.25 else "LOW RISK")
        fmt_risk = fmt_td_text
        if risk == "HIGH RISK":
            fmt_risk = workbook.add_format({'font_size': 10, 'bold': True, 'font_color': RED_HEX, 'align': 'center', 'border': 1, 'border_color': BORDER_GRAY, 'bg_color': '#fef2f2'})
        elif risk == "MEDIUM RISK":
            fmt_risk = workbook.add_format({'font_size': 10, 'bold': True, 'font_color': '#d97706', 'align': 'center', 'border': 1, 'border_color': BORDER_GRAY, 'bg_color': '#fffbeb'})
        else:
            fmt_risk = workbook.add_format({'font_size': 10, 'bold': True, 'font_color': GREEN_HEX, 'align': 'center', 'border': 1, 'border_color': BORDER_GRAY, 'bg_color': '#f0fdf4'})

        ws_dept.write(row_curr, 1, row['Department'], fmt_td_text)
        ws_dept.write(row_curr, 2, row['JobRole'], fmt_td_text)
        ws_dept.write(row_curr, 3, row['Total'], fmt_td_num)
        ws_dept.write(row_curr, 4, row['Retained'], fmt_td_num)
        ws_dept.write(row_curr, 5, row['Left'], fmt_td_num)
        ws_dept.write(row_curr, 6, rate, fmt_td_pct)
        ws_dept.write(row_curr, 7, risk, fmt_risk)
        row_curr += 1
        
    ws_dept.set_column("A:A", 3)
    ws_dept.set_column("B:C", 24)
    ws_dept.set_column("D:H", 16)

    # -------------------------------------------------------------
    # SHEET 3: Compensation & Experience Analysis
    # -------------------------------------------------------------
    ws_comp = workbook.add_worksheet("Compensation & Experience")
    ws_comp.hide_gridlines(0)
    
    ws_comp.merge_range("B2:G2", "COMPENSATION & TENURE ATTRITION MATRIX", fmt_title)
    ws_comp.set_row(1, 26)
    
    # Table 1: Salary Range Breakdown
    ws_comp.write("B4", "1. Salary Range Breakdown", fmt_section_hdr)
    sal_headers = ["Salary Range", "Total Employees", "Left", "Retained", "Attrition Rate (%)", "Avg Monthly Income ($)"]
    for c_idx, h in enumerate(sal_headers):
        ws_comp.write(4, 1 + c_idx, h, fmt_th)
        
    sal_detail = df.groupby('Salary_Range', observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum'),
        AvgIncome=('MonthlyIncome', 'mean')
    ).reindex(sal_order).reset_index()
    sal_detail['Retained'] = sal_detail['Total'] - sal_detail['Left']
    sal_detail['Rate'] = sal_detail['Left'] / sal_detail['Total']
    
    r_idx = 5
    for _, row in sal_detail.iterrows():
        ws_comp.write(r_idx, 1, row['Salary_Range'], fmt_td_text)
        ws_comp.write(r_idx, 2, row['Total'], fmt_td_num)
        ws_comp.write(r_idx, 3, row['Left'], fmt_td_num)
        ws_comp.write(r_idx, 4, row['Retained'], fmt_td_num)
        ws_comp.write(r_idx, 5, row['Rate'], fmt_td_pct)
        ws_comp.write(r_idx, 6, row['AvgIncome'], fmt_td_num)
        r_idx += 1
        
    # Table 2: Tenure Breakdown
    r_idx += 2
    ws_comp.write(f"B{r_idx}", "2. Employee Tenure Breakdown (Years at Company)", fmt_section_hdr)
    ten_headers = ["Tenure Group", "Total Employees", "Left", "Retained", "Attrition Rate (%)", "Avg Years at Company"]
    for c_idx, h in enumerate(ten_headers):
        ws_comp.write(r_idx, 1 + c_idx, h, fmt_th)
    r_idx += 1
    
    ten_detail = df.groupby('Tenure_Group', observed=False).agg(
        Total=('EmployeeID', 'count'),
        Left=('Attrition_Flag', 'sum'),
        AvgTenure=('YearsAtCompany', 'mean')
    ).reindex(ten_order).reset_index()
    ten_detail['Retained'] = ten_detail['Total'] - ten_detail['Left']
    ten_detail['Rate'] = ten_detail['Left'] / ten_detail['Total']
    
    for _, row in ten_detail.iterrows():
        ws_comp.write(r_idx, 1, row['Tenure_Group'], fmt_td_text)
        ws_comp.write(r_idx, 2, row['Total'], fmt_td_num)
        ws_comp.write(r_idx, 3, row['Left'], fmt_td_num)
        ws_comp.write(r_idx, 4, row['Retained'], fmt_td_num)
        ws_comp.write(r_idx, 5, row['Rate'], fmt_td_pct)
        ws_comp.write(r_idx, 6, round(row['AvgTenure'], 1), fmt_td_num)
        r_idx += 1
        
    ws_comp.set_column("A:A", 3)
    ws_comp.set_column("B:G", 22)

    # -------------------------------------------------------------
    # SHEET 4: Workload & Satisfaction
    # -------------------------------------------------------------
    ws_sat = workbook.add_worksheet("Workload & Satisfaction")
    ws_sat.hide_gridlines(0)
    
    ws_sat.merge_range("B2:F2", "OVERTIME & JOB SATISFACTION CROSS-ANALYSIS", fmt_title)
    ws_sat.set_row(1, 26)
    
    ws_sat.write("B4", "Job Satisfaction vs Overtime Attrition Rate (%) Matrix", fmt_section_hdr)
    
    ws_sat.write("B5", "Job Satisfaction Level", fmt_th)
    ws_sat.write("C5", "No Overtime (Rate)", fmt_th)
    ws_sat.write("D5", "Works Overtime (Rate)", fmt_th)
    ws_sat.write("E5", "Total Rate", fmt_th)
    
    cross_df = df.groupby(['Satisfaction_Label', 'Overtime'], observed=False)['Attrition_Flag'].mean().unstack()
    cross_df['Total'] = df.groupby('Satisfaction_Label', observed=False)['Attrition_Flag'].mean()
    
    r_idx = 6
    for sat_lbl, row in cross_df.iterrows():
        ws_sat.write(r_idx, 1, sat_lbl, fmt_td_text)
        ws_sat.write(r_idx, 2, row['No'], fmt_td_pct)
        ws_sat.write(r_idx, 3, row['Yes'], fmt_td_pct)
        ws_sat.write(r_idx, 4, row['Total'], fmt_td_pct)
        r_idx += 1
        
    ws_sat.set_column("A:A", 3)
    ws_sat.set_column("B:E", 24)

    # -------------------------------------------------------------
    # SHEET 5: Cleaned Master Dataset
    # -------------------------------------------------------------
    ws_data = workbook.add_worksheet("Cleaned Data")
    ws_data.hide_gridlines(0)
    
    # Write full dataframe as table
    (max_row, max_col) = df.shape
    column_settings = [{'header': column} for column in df.columns]
    
    ws_data.add_table(0, 0, max_row, max_col - 1, {
        'data': df.values.tolist(),
        'columns': column_settings,
        'style': 'Table Style Medium 9'
    })
    ws_data.set_column(0, max_col - 1, 15)

    # -------------------------------------------------------------
    # SHEET 6: Insights & Recommendations
    # -------------------------------------------------------------
    ws_rec = workbook.add_worksheet("Insights & Recommendations")
    ws_rec.hide_gridlines(0)
    
    ws_rec.merge_range("B2:I2", "EXECUTIVE SUMMARY, KEY FINDINGS & STRATEGIC RECOMMENDATIONS", fmt_title)
    ws_rec.set_row(1, 26)
    
    fmt_h1 = workbook.add_format({'bold': True, 'font_size': 13, 'font_color': NAVY_HEX, 'bg_color': '#e0f2fe'})
    fmt_text_block = workbook.add_format({'font_size': 10, 'text_wrap': True, 'valign': 'top'})
    
    # Section 1: Executive Summary
    ws_rec.merge_range("B4:I4", "1. EXECUTIVE SUMMARY", fmt_h1)
    summary_text = (
        "This project provides a data-driven analysis of employee attrition patterns within the organization. "
        "Based on an audit of 1,470 employee records, the current overall company attrition rate stands at 38.8% "
        "(570 employees left). Analysis reveals that employee turnover is not uniform but heavily concentrated "
        "in specific high-risk pockets, primarily driven by compensation disparities, heavy overtime workload, "
        "and early-stage employee tenure."
    )
    ws_rec.merge_range("B5:I6", summary_text, fmt_text_block)
    
    # Section 2: Key Findings
    ws_rec.merge_range("B8:I8", "2. KEY FINDINGS & TURNOVER DRIVERS", fmt_h1)
    findings_text = (
        "• Compensation Impact: Employees earning under $3,000/month experience an alarming 68.8% attrition rate, "
        "compared to only 7.1% for staff earning >$15,000/month. Low pay is the #1 predictor of turnover.\n"
        "• Critical Tenure Risk: New hires with 0-2 years of tenure face 51.2% attrition (78.4% of all exits). "
        "Retention stabilizes significantly after year 3 (22.9%).\n"
        "• Overtime Fatigue: Overtime workers experience 54.1% attrition versus 32.8% for non-overtime workers.\n"
        "• High-Risk Roles: Laboratory Technicians (63.3% rate) and Sales Representatives (55.4% rate) exhibit "
        "the highest turnover among all job roles.\n"
        "• Early Career / Youth Turnover: Employees aged 18-25 have a 60.9% attrition rate."
    )
    ws_rec.merge_range("B9:I14", findings_text, fmt_text_block)
    
    # Section 3: Strategic HR Recommendations
    ws_rec.merge_range("B16:I16", "3. STRATEGIC HR RECOMMENDATIONS & ACTION PLAN", fmt_h1)
    recs_text = (
        "1. Compensation Restructuring for Entry-Level Roles:\n"
        "   - Conduct a market benchmark review for Laboratory Technicians and Sales Representatives.\n"
        "   - Increase baseline salary floor from $2,500 to $3,800/month for entry-level positions to curb immediate exit incentives.\n\n"
        "2. Early Tenure Onboarding & Mentorship Program (0-2 Years):\n"
        "   - Establish a 90-day structured onboarding check-in and 1-on-1 mentorship for all new hires.\n"
        "   - Introduce stay interviews at 6 months and 12 months to proactively resolve early friction.\n\n"
        "3. Overtime Workload Redistribution & Capping:\n"
        "   - Implement mandatory overtime caps (max 10 hours/week) and introduce compensatory off / premium OT pay.\n"
        "   - Audit staffing levels in Laboratory & Sales departments to eliminate chronic understaffing.\n\n"
        "4. Clear Career Growth Pathways & Skill Training:\n"
        "   - Define explicit 2-year career progression maps for entry-level roles showing clear promotion criteria."
    )
    ws_rec.merge_range("B17:I26", recs_text, fmt_text_block)
    
    ws_rec.set_column("A:A", 3)
    ws_rec.set_column("B:I", 13)
    
    workbook.close()
    print(f"Excel Dashboard workbook successfully generated at: {output_excel}")

if __name__ == "__main__":
    build_excel_dashboard()
