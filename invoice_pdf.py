"""
invoice_pdf.py

Turns a calculated monthly invoice amount into a branded PDF invoice.

Deliberately kept separate from calculate_monthly_invoice() — the maths
and the output format are two different jobs. If you ever swap PDF for,
say, an HTML invoice or an email, this file changes and your calculation
logic doesn't.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER
from datetime import date
import os

# Copper Pots brand palette — copper/terracotta to match the name,
# warm cream background tone, soft sage as an accent (Montessori /
# home-from-home feel rather than a corporate blue-and-grey invoice).
COPPER = colors.HexColor("#B5651D")
COPPER_DARK = colors.HexColor("#7C4A1E")
CREAM = colors.HexColor("#FBF3EA")
SAGE = colors.HexColor("#8A9A5B")
INK = colors.HexColor("#3A2E27")


def create_invoice_pdf(
        child_name,
        days_attended,
        price_per_day,
        monthly_amount,
        output_path,
        nursery_name="Copper Pots Day Nursery",
        tagline="A home-from-home where curiosity leads learning",
        phone="01224 681276",
        email="admin@copperpotsmontessori.co.uk",
        logo_path="logo.png",
        invoice_date=None,
):
        """
            Build one branded invoice PDF for one child.

                monthly_amount is passed in already-calculated — this function's job
                    is layout, not maths.

                        logo_path: optional path to a logo image file. If None or the file
                            doesn't exist, the header just uses text — no error.
                                """
        if invoice_date is None:
                    invoice_date = date.today()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
        )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
                "InvoiceTitle", parent=styles["Title"], fontSize=22,
                textColor=COPPER_DARK, spaceAfter=2, fontName="Helvetica-Bold",
    )
    tagline_style = ParagraphStyle(
                "Tagline", parent=styles["Normal"], fontSize=10,
                textColor=SAGE, fontName="Helvetica-Oblique", spaceAfter=2,
    )
    small_grey = ParagraphStyle(
                "SmallGrey", parent=styles["Normal"], fontSize=9, textColor=colors.grey,
    )
    footer_style = ParagraphStyle(
                "Footer", parent=styles["Normal"], fontSize=9,
                textColor=INK, alignment=TA_CENTER, leading=13,
    )

    story = []

    centered_tagline = ParagraphStyle(
                "TaglineCentered", parent=tagline_style, alignment=TA_CENTER,
    )
    centered_title = ParagraphStyle(
                "TitleCentered", parent=title_style, alignment=TA_CENTER,
    )

    # Header — the logo artwork already has the nursery name arced into
    # it, so when a logo is present we centre it alone (no redundant
    # text title next to it) and just add the tagline beneath.
    if logo_path and os.path.exists(logo_path):
                story.append(Image(logo_path, width=45 * mm, height=36.6 * mm, hAlign="CENTER"))
                story.append(Spacer(1, 2 * mm))
                story.append(Paragraph(tagline, centered_tagline))
else:
            story.append(Paragraph(nursery_name, centered_title))
            story.append(Paragraph(tagline, centered_tagline))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1.2, color=COPPER))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Monthly Invoice", styles["Heading2"]))
    story.append(Paragraph(f"Date: {invoice_date.strftime('%d %B %Y')}", small_grey))
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph(f"Invoice for: {child_name}", styles["Heading3"]))
    story.append(Spacer(1, 6 * mm))

    # Line item table
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
                                                    ("BACKGROUND", (0, 0), (-1, 0), COPPER_DARK),
                                                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                                                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                                                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2d6c8")),
                                                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM]),
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

    story.append(Spacer(1, 16 * mm))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#e2d6c8")))
    story.append(Spacer(1, 6 * mm))

    # Footer — doubles as light advertising: contact details + referral
    # prompt, so the invoice does a bit of marketing work too, without
    # crowding out the actual invoice information.
    story.append(
                Paragraph(
                                f'"What the hand does, the mind remembers" — Montessori & Reggio Emilia approach',
                                footer_style,
                )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
                Paragraph(
                                f"Know a family who'd love a home-from-home for their little one? "
                                f"We'd love to welcome them — get in touch on {phone} or {email}.",
                                footer_style,
                )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
                Paragraph(
                                f"{nursery_name} · {phone} · {email}",
                                footer_style,
                )
    )

    doc.build(story)


if __name__ == "__main__":
        # Quick manual test using the same numbers you already confirmed
        # correct (£86/day -> £1791.67/month).
        create_invoice_pdf(
                    child_name="Test Child",
                    days_attended=3,
                    price_per_day=86.00,
                    monthly_amount=1791.67,
                    output_path="/home/claude/test_invoice.pdf",
        )
        print("Test invoice created.")
    
