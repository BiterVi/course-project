from openpyxl.styles import Font, Border, Alignment, Side


class Styles:
    full_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

    alignment_center = Alignment(horizontal="center",
                                 vertical="center")

    bold_font = Font(bold=True)
