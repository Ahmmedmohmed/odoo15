from odoo import models


class AppraisalXlsx(models.AbstractModel):
    _name = 'report.nile_air_appraisal.appraisal_xlsx_report'  # استبدل nile_air_appraisal باسم موديولك
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        # 1. إنشاء صفحة العمل وتنسيقها
        sheet = workbook.add_worksheet('Appraisal Report')
        sheet.set_column('A:A', 20)  # Submission Date
        sheet.set_column('B:B', 30)  # Employee
        sheet.set_column('C:C', 25)  # Department
        sheet.set_column('D:D', 20)  # Title
        sheet.set_column('E:F', 15)  # Ranks
        sheet.set_column('G:H', 18)  # Performance
        sheet.set_column('I:L', 15)  # Wages & Diff

        # 2. تعريف التنسيقات (Styles)
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#D3D3D3', 'border': 1
        })
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'center', 'border': 1})
        text_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        number_format = workbook.add_format({'num_format': '#,##0.00', 'align': 'center', 'border': 1})
        percent_format = workbook.add_format({'num_format': '0.00%', 'align': 'center', 'border': 1})

        # 3. كتابة رؤوس الأعمدة (Headers)
        headers = [
            'Submission Date', 'Employee', 'Department', 'Title',
            'Last Rank', 'Rank', 'Last Performance', 'Total Performance',
            'Last Wage', 'Actual Wage', 'Difference', 'Percentage'
        ]

        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, header_format)

        # 4. تعبئة البيانات
        row = 1
        for rec in records:
            # --- منطق جلب Last Rank (غير موجود في الموديل مباشرة) ---
            last_rank = ''
            last_appraisal = self.env['appraisal.appraisal'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('id', '!=', rec.id),
                ('state', '=', 'done')
            ], order='id desc', limit=1)

            if last_appraisal and last_appraisal.rank:
                last_rank = last_appraisal.rank
            # -----------------------------------------------------

            # حساب الفرق والنسبة
            last_wage = rec.employee_wage or 0.0
            actual_wage = rec.estimate_salary or 0.0  # الراتب الجديد المقترح
            difference = actual_wage - last_wage
            percentage = (difference / last_wage) if last_wage > 0 else 0.0

            # كتابة البيانات في الخلايا
            sheet.write(row, 0, rec.appraisal_date or '', date_format)
            sheet.write(row, 1, rec.employee_id.name or '', text_format)
            sheet.write(row, 2, rec.department_id.name or '', text_format)
            sheet.write(row, 3, rec.title or '', text_format)
            sheet.write(row, 4, last_rank, text_format)
            sheet.write(row, 5, rec.rank or '', text_format)

            # نسب الأداء
            sheet.write(row, 6, rec.last_performance_percentage or 0, number_format)
            sheet.write(row, 7, rec.total_performance_percentage or 0, number_format)

            # الرواتب
            sheet.write(row, 8, last_wage, number_format)
            sheet.write(row, 9, actual_wage, number_format)
            sheet.write(row, 10, difference, number_format)
            sheet.write(row, 11, percentage, percent_format)

            row += 1