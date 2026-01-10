from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self, title, client_name=""):
        super().__init__()
        self.report_title = title
        self.client_name = client_name
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Set font
        self.set_font('helvetica', 'B', 15)
        # Title
        self.cell(0, 10, self.report_title, border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        
        if self.client_name:
            self.set_font('helvetica', 'I', 10)
            self.cell(0, 5, f"Prepared for: {self.client_name}", border=0, align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # set font
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
        # Date
        self.set_x(-40)
        self.cell(30, 10, datetime.now().strftime("%Y-%m-%d"), align='R')

class PDFReportGenerator:
    def __init__(self):
        pass

    def generate_campaign_report(self, data, title, client_name, filename):
        """
        Generates a PDF report for a campaign.
        
        Args:
            data (list of dict): List of dictionaries containing lead/campaign data.
            title (str): Title of the report.
            client_name (str): Name of the client.
            filename (str): Output filename.
        """
        pdf = PDFReport(title, client_name)
        pdf.add_page()
        
        # Summary Section
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, 'Campaign Summary', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 5, f'Total Records: {len(data)}', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Data Table
        if data:
            # Table Header
            pdf.set_font('helvetica', 'B', 10)
            # Dynamic column width calculation could go here, for now using fixed basic ones
            # Assuming data keys are: Name, Company, Email, Status
            
            # Get headers from first item if available and standardizing
            headers = list(data[0].keys())
            # Limit to first 5 columns to fit page for now
            headers = headers[:5] 
            
            col_width = pdf.w / (len(headers) + 0.5) # simple logic
            
            for header in headers:
                pdf.cell(col_width, 10, str(header).capitalize(), border=1, align='C')
            pdf.ln()
            
            # Table Rows
            pdf.set_font('helvetica', '', 9)
            for row in data:
                for header in headers:
                    val = str(row.get(header, ''))
                    # Truncate if too long (very basic handling)
                    if len(val) > 25:
                        val = val[:22] + "..."
                    pdf.cell(col_width, 10, val, border=1)
                pdf.ln()

        pdf.output(filename)
        return filename
