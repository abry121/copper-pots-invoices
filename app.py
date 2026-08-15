"""
app.py — Streamlit web app for the nursery invoice generator.

Run it with:  streamlit run app.py

This is just a web form wrapped around code you already have —
calculate_monthly_invoice() and create_invoice_pdf() don't change at all.
"""

import streamlit as st
from invoice_pdf import create_invoice_pdf

WEEKS_PER_YEAR = 50


def calculate_monthly_invoice(price_per_day, days_attended):
    return price_per_day * days_attended * WEEKS_PER_YEAR / 12


st.title("Nursery Invoice Generator")

nursery_name = st.text_input("Nursery name", "Your Nursery Name")
child_name = st.text_input("Child's name")
days_attended = st.number_input("Days attended per week", min_value=1, max_value=7, value=3)
price_per_day = st.number_input("Daily rate (£)", min_value=0.0, value=86.00, format="%.2f")

if st.button("Generate invoice"):
    if not child_name:
        st.error("Enter a child's name first.")
    else:
        monthly_amount = calculate_monthly_invoice(price_per_day, days_attended)
        output_path = f"invoice_{child_name.replace(' ', '_')}.pdf"

        create_invoice_pdf(
            child_name=child_name,
            days_attended=days_attended,
            price_per_day=price_per_day,
            monthly_amount=monthly_amount,
            output_path=output_path,
            nursery_name=nursery_name,
        )

        st.success(f"Monthly invoice: £{monthly_amount:.2f}")

        with open(output_path, "rb") as f:
            st.download_button(
                "Download PDF",
                data=f,
                file_name=output_path,
                mime="application/pdf",
            )
