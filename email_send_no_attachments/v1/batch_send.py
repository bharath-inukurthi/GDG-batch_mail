import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_sender.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def read_csv_data(csv_file_path):
    """
    Read names and emails from a CSV file.
    Expected CSV format: name,email (with header row)
    """
    try:
        recipients = []
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get('name', 'name not given').strip()
                email = row.get('email', '').strip()
                if name and email:
                    recipients.append({'name': name, 'email': email})
                else:
                    logger.warning(f"Skipping row with missing data: {row}")
        return recipients
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file_path}: {str(e)}")
        return []
def create_html_email(recipient_name):
    """
    Create personalized HTML email content for the recipient.
    """
    # HTML Email Template with personalized greeting
    html = """HTML template
"""
    return html

def send_email(smtp_server, port, sender_email, password, recipient_email, subject,
               html_content, recipient_name):
    """
    Send a confirmation email with HTML content.
    """
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
            logger.info(f"Email sent successfully to {recipient_email} ({recipient_name})")
            return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False

def process_csv_recipients(csv_file_path, smtp_settings, dry_run=False):
    """
    Process recipients from CSV file and send confirmation emails.
    """
    recipients = read_csv_data(csv_file_path)

    if not recipients:
        logger.error(f"No valid recipients found in CSV file: {csv_file_path}")
        return

    logger.info(f"Found {len(recipients)} recipients to process")

    success_count = 0
    failed_count = 0

    for recipient in recipients:
        name = recipient['name']
        email = recipient['email']

        html_content = create_html_email(name)
        subject = f"Invitation for study jams whatsapp group"

        logger.info(f"Processing: {name} -> {email}")

        if dry_run:
            logger.info(f"[DRY RUN] Would send confirmation email to {email} ({name})")
            success_count += 1
        else:
            success = send_email(
                smtp_settings['server'],
                smtp_settings['port'],
                smtp_settings['email'],
                smtp_settings['password'],
                email,
                subject,
                html_content,
                name
            )

            if success:
                success_count += 1
            else:
                failed_count += 1

            # Sleep briefly to avoid overwhelming the SMTP server
            time.sleep(2)

    logger.info(f"Email sending complete. Success: {success_count}, Failed: {failed_count}")
def main():
    parser = argparse.ArgumentParser(description='Send confirmation emails to workshop participants from CSV file')
    parser.add_argument('--csv', '-c', required=True, help='CSV file containing names and emails (columns: name, email)')
    parser.add_argument('--email', '-e', required=True, help='Sender email address')
    parser.add_argument('--password', '-p', required=True, help='Email password')
    parser.add_argument('--server', '-s', default='smtp.gmail.com', help='SMTP server address')
    parser.add_argument('--port', '-pt', type=int, default=587, help='SMTP server port')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Perform a dry run without sending emails')

    args = parser.parse_args()

    smtp_settings = {
        'server': args.server,
        'port': args.port,
        'email': args.email,
        'password': args.password
    }

    process_csv_recipients(args.csv, smtp_settings, args.dry_run)

if __name__ == "__main__":
    main()
