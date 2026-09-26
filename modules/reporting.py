import pandas as pd
import io

def create_excel_report(records):
    output = io.BytesIO()
    
    df = pd.DataFrame(records)
    
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Audit Summary", index=False)
        
        workbook = writer.book
        worksheet = writer.sheets["Audit Summary"]
        
        # Style Formats
        header_format = workbook.add_format({
            'bold': True, 'text_wrap': True, 'valign': 'top',
            'fg_color': '#1F4E78', 'font_color': '#FFFFFF', 'border': 1
        })
        critical_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        high_format = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
        pass_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        
        # Apply Header Formatting
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_format)
            worksheet.set_column(col_num, col_num, 22)
            
        worksheet.set_column('D:D', 50)  # Expand Findings Column
        
        # Conditional Formatting for Priority
        worksheet.conditional_format(1, 1, len(df), 1, {
            'type': 'cell', 'criteria': 'equal', 'value': '"CRITICAL"', 'format': critical_format
        })
        worksheet.conditional_format(1, 1, len(df), 1, {
            'type': 'cell', 'criteria': 'equal', 'value': '"HIGH"', 'format': high_format
        })
        worksheet.conditional_format(1, 1, len(df), 1, {
            'type': 'cell', 'criteria': 'equal', 'value': '"LOW / COMPLIANT"', 'format': pass_format
        })
        
    output.seek(0)
    return output
