import csv
from invoice_pdf import create_invoice_pdf

WEEKS_PER_YEAR = 50


def calculate_monthly_invoice(price_per_day, days_attended):
    return price_per_day * days_attended * WEEKS_PER_YEAR / 12


def generate_all_invoices(csv_path="children.csv"):
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            days = int(row["days_attended"])
            rate = float(row["price_per_day"])

            monthly_amount = calculate_monthly_invoice(rate, days)

            output_path = f"invoice_{name.replace(' ', '_')}.pdf"
            create_invoice_pdf(
                child_name=name,
                days_attended=days,
                price_per_day=rate,
                monthly_amount=monthly_amount,
                output_path=output_path,
            )
            print(f"Created {output_path} — £{monthly_amount:.2f}/month")


if __name__ == "__main__":
    generate_all_invoices()
