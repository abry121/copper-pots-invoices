"""
invoice_pdf.py

Turns a calculated monthly invoice amount into an actual PDF document.

Deliberately kept separate from calculate_monthly_invoice() — the maths
and the output format are two different jobs. If you ever swap PDF for,
say, an HTML invoice or an email, this file changes and your calculation
logic doesn't.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import date


def create_invoice_pdf(
    child_name,
    days_attended,
    price_per_day,
    monthly_amount,
    output_path,
    nursery_name="Your Nursery Name",
    invoice_date=None,
):
    """
    Build one invoice PDF for one child.

    monthly_amount is passed in already-calculated — this function's job
    is layout, not maths. Keeps it testable without touching your
    calculate_monthly_invoice() logic.
    """
    if invoice_date is None:
        invoice_date = date.today()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "InvoiceTitle", parent=styles["Title"], fontSize=20, spaceAfter=4
    )
    small_grey = ParagraphStyle(
        "SmallGrey", parent=styles["Normal"], fontSize=9, textColor=colors.grey
    )

    story = []

    # Header
    story.append(Paragraph(nursery_name, title_style))
    story.append(Paragraph("Monthly Invoice", styles["Heading2"]))
    story.append(Paragraph(f"Date: {invoice_date.strftime('%d %B %Y')}", small_grey))
    story.append(Spacer(1, 12 * mm))

    story.append(Paragraph(f"Invoice for: {child_name}", styles["Heading3"]))
    story.append(Spacer(1, 6 * mm))

    # Line item table — one row per charge. Even with a single row, a
    # Table keeps columns aligned properly, which raw drawString() text
    # doesn't do for you.
    table_data = [
        ["Description", "Days/week", "Daily rate", "Monthly charge"],
        [
            "Nursery fees (smoothed monthly rate)",
            str(days_attended),
            f"£{price_per_day:.2f}",
            f"£{monthly_amount:.2f}",
        ],
    ]
    table = Table(table_data, colWidths=[70 * mm, 30 * mm, 30 * mm, 40 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(f"<b>Total due: £{monthly_amount:.2f}</b>", styles["Heading3"])
    )
    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            "This amount is a smoothed monthly rate based on your child's "
            "weekly attendance pattern, averaged across the year — it does "
            "not vary by how many days are in a given calendar month.",
            small_grey,
        )
    )

    doc.build(story)


if __name__ == "__main__":
    # Quick manual test using the same numbers you already confirmed
    # correct in your terminal version (£86/day -> £1791.67/month).
    create_invoice_pdf(
        child_name="Test Child",
        days_attended=3,
        price_per_day=86.00,
        monthly_amount=1791.67,
        output_path="/home/claude/test_invoice.pdf",
    )
    print("Test invoice created.")
