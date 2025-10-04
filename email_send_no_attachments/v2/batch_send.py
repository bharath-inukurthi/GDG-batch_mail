import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import logging
import argparse
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn
)
from rich.console import Console
from rich.table import Table

# ---------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------
log_file_handler = logging.FileHandler("email_sender.log", encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[log_file_handler],
)
logger = logging.getLogger()
console = Console()

# ---------------------------------------------
# CSV READER
# ---------------------------------------------
def read_csv_data(csv_file_path):
    recipients = []
    try:
        with open(csv_file_path, "r", newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("name", "").strip()
                email = row.get("email", "").strip()
                if name and email:
                    recipients.append({"name": name, "email": email})
                else:
                    logger.warning(f"Skipping row with missing data: {row}")
        return recipients
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file_path}: {str(e)}")
        return []

# ---------------------------------------------
# HTML TEMPLATE
# ---------------------------------------------
def create_html_email(recipient_name):
    return f""" HTML Template """

# ---------------------------------------------
# EMAIL SENDER
# ---------------------------------------------
def send_email(smtp_server, port, sender_email, password, recipient_email, subject, html_content, recipient_name):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)

        logger.info(f"✅ Email sent successfully to {recipient_email} ({recipient_name})")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {recipient_email}: {str(e)}")
        return False

# ---------------------------------------------
# PROCESS FUNCTION
# ---------------------------------------------
def process_csv_recipients(csv_file_path, smtp_settings, dry_run=False):
    recipients = read_csv_data(csv_file_path)
    if not recipients:
        console.print("[red]No valid recipients found in CSV.[/]")
        return

    total = len(recipients)
    logger.info(f"Found {total} recipients to process")

    success, failed = 0, 0

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False  # remove progress bar after completion
    ) as progress:
        task = progress.add_task("Starting...", total=total)

        for r in recipients:
            name, email = r["name"], r["email"]

            # Only one active "Processing" line
            progress.update(task, description=f"📤 Sending to: {name} <{email}>")
            console.log(f"[cyan]Processing[/]: {name} <{email}>")

            html = create_html_email(name)
            subject = "Invitation for Study Jams WhatsApp Group"

            if dry_run:
                console.log(f"[yellow][DRY RUN][/]: Would send email to {email}")
                success += 1
            else:
                if send_email(
                    smtp_settings["server"],
                    smtp_settings["port"],
                    smtp_settings["email"],
                    smtp_settings["password"],
                    email,
                    subject,
                    html,
                    name,
                ):
                    success += 1
                else:
                    failed += 1
                time.sleep(1.2)  # polite delay

            progress.advance(task)

        # Final completion description
        progress.update(task, description="[green]✅ Completed sending all emails![/]")

    # Show summary
    table = Table(title="📧 Email Summary", show_lines=True)
    table.add_column("Status", justify="center")
    table.add_column("Count", justify="center")
    table.add_row("✅ Success", str(success))
    table.add_row("❌ Failed", str(failed))
    table.add_row("📊 Total", str(total))
    console.print(table)

    logger.info(f"Email sending complete. Success: {success}, Failed: {failed}")

# ---------------------------------------------
# MAIN ENTRY
# ---------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Send Study Jam invitation emails from CSV.")
    parser.add_argument("--csv", "-c", required=True, help="CSV path (columns: name,email)")
    parser.add_argument("--email", "-e", required=True, help="Sender email")
    parser.add_argument("--password", "-p", required=True, help="Sender password")
    parser.add_argument("--server", "-s", default="smtp.gmail.com", help="SMTP server")
    parser.add_argument("--port", "-pt", type=int, default=587, help="SMTP port")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run mode")

    args = parser.parse_args()

    smtp_settings = {
        "server": args.server,
        "port": args.port,
        "email": args.email,
        "password": args.password,
    }

    process_csv_recipients(args.csv, smtp_settings, args.dry_run)

if __name__ == "__main__":
    main()
