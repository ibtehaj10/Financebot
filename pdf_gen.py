
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.layout_element import Alignment
from datetime import datetime
import random
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.pdf import PDF
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from decimal import Decimal
from borb.pdf import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.color.color import HexColor, X11Color

class InvoiceGenerator:
    def __init__(self, company_name, company_address, client_name, client_email, client_address, items, note, bank, account_number, currency):
        self.company_name = company_name
        self.company_address = company_address
        self.client_name = client_name
        self.client_email = client_email
        self.client_address = client_address
        self.items = items
        self.note = note
        self.bank = bank
        self.account_number = account_number
        self.currency = currency

    def build_invoice_information(self):
        table_001 = Table(number_of_rows=5, number_of_columns=2)
        table_001.add(Paragraph("Company", font="Helvetica-Bold", font_color=X11Color("Black")))
        table_001.add(Paragraph(self.company_name))
        
        table_001.add(Paragraph("Address", font="Helvetica-Bold"))
        table_001.add(Paragraph(self.company_address))
        
        table_001.add(Paragraph("Date", font="Helvetica-Bold"))
        now = datetime.now()
        table_001.add(Paragraph("%d/%d/%d" % (now.day, now.month, now.year)))
        
        table_001.add(Paragraph("Invoice #", font="Helvetica-Bold"))
        table_001.add(Paragraph("%d" % random.randint(1000, 10000)))
        
        table_001.add(Paragraph("Due Date", font="Helvetica-Bold"))
        table_001.add(Paragraph("%d/%d/%d" % (now.day, now.month, now.year)))

        table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        table_001.no_borders()
        return table_001

    def build_billing_and_shipping_information(self):
        table_001 = Table(number_of_rows=3, number_of_columns=2)
        table_001.add(Paragraph("BILL TO", font="Helvetica-Bold", font_color=X11Color("Black")))
        table_001.add(Paragraph(self.client_name))
        table_001.add(Paragraph("Email", font="Helvetica-Bold", font_color=X11Color("Black")))
        table_001.add(Paragraph(self.client_email))
        table_001.add(Paragraph("Address", font="Helvetica-Bold", font_color=X11Color("Black")))
        table_001.add(Paragraph(self.client_address))
        
        table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        table_001.no_borders()
        return table_001
    
    def build_itemized_description_table(self):
        table_001 = Table(number_of_rows=len(self.items) + 3, number_of_columns=4)
        for h in ["DESCRIPTION", "QTY", "UNIT PRICE", "AMOUNT"]:
            table_001.add(TableCell(Paragraph(h, font_color=X11Color("White")), background_color=HexColor("5a88b1")))

        odd_color = HexColor("BBBBBB")
        even_color = HexColor("FFFFFF")
        subtotal = 0

        for row_number, item in enumerate(self.items):
            c = even_color if row_number % 2 == 0 else odd_color
            description, qty, unit_price = item["name"], item["quantity"], item["price"]
            amount = qty * unit_price
            subtotal += amount

            table_001.add(TableCell(Paragraph(description), background_color=c))
            table_001.add(TableCell(Paragraph(str(qty)), background_color=c))
            table_001.add(TableCell(Paragraph(f"{self.currency} {unit_price:.2f}"), background_color=c))
            table_001.add(TableCell(Paragraph(f"{self.currency} {amount:.2f}"), background_color=c))

        subtotal_cell = TableCell(Paragraph("Subtotal", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))
        subtotal_value = TableCell(Paragraph(f"{self.currency} {subtotal:.2f}", horizontal_alignment=Alignment.RIGHT))

        tax_rate = 0.075  # 7.5% tax rate
        discount_rate = 0.05  # 5% discount rate

        discount_amount = subtotal * discount_rate
        discount_cell = TableCell(Paragraph("Discounts", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))
        discount_value = TableCell(Paragraph(f"{self.currency} {discount_amount:.2f}", horizontal_alignment=Alignment.RIGHT))

        tax_amount = (subtotal - discount_amount) * tax_rate
        tax_cell = TableCell(Paragraph("Taxes", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))
        tax_value = TableCell(Paragraph(f"{self.currency} {tax_amount:.2f}", horizontal_alignment=Alignment.RIGHT))

        total = subtotal - discount_amount + tax_amount
        total_cell = TableCell(Paragraph("Total", font="Helvetica-Bold", horizontal_alignment=Alignment.RIGHT))
        total_value = TableCell(Paragraph(f"{self.currency} {total:.2f}", horizontal_alignment=Alignment.RIGHT))
        
        table_001.add(subtotal_cell)
        table_001.add(subtotal_value)
        table_001.add(discount_cell)
        table_001.add(discount_value)
        table_001.add(tax_cell)
        table_001.add(tax_value)
        table_001.add(total_cell)
        table_001.add(total_value)

        table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        table_001.no_borders()
        return table_001

    def build_some_notices(self):
        table_001 = Table(number_of_rows=5, number_of_columns=1)
        table_001.add(TableCell(Paragraph("Notes", font="Helvetica-Bold")))
        table_001.add(Paragraph(self.note))
        table_001.add(Paragraph("Bank Details", font="Helvetica-Bold"))
        table_001.add(Paragraph(self.bank))
        table_001.add(Paragraph(self.account_number))
        
        table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        table_001.no_borders()
        return table_001

    def call(self):
        pdf = Document()
        page = Page()
        pdf.add_page(page)
        page_layout = SingleColumnLayout(page)
        page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

        invoice_heading = Paragraph("Invoice", font_size=20)
        page_layout.add(invoice_heading)

        page_layout.add(self.build_invoice_information())
        page_layout.add(Paragraph(" "))
        page_layout.add(self.build_billing_and_shipping_information())
        page_layout.add(Paragraph(" "))
        page_layout.add(self.build_itemized_description_table())
        page_layout.add(Paragraph(" "))
        page_layout.add(self.build_some_notices())
        page_layout.add(Paragraph("\nThank You for Your Business", font_size=12))

        with open("Invoices.pdf", "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, pdf)
