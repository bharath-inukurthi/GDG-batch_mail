import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time
import logging
import argparse
import os
from datetime import datetime

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

def read_csv_data(csv_file_path, int_column='reg'):
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
                int_value = (row.get(int_column) or '').strip()
                if name and int_value:
                    recipients.append({'name': name, 'int': int_value})
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
    current_date = datetime.now().strftime('%B %d, %Y')
    html = """ HTML Template """
    return html

def send_email(smtp_server, port, sender_email, password, recipient_email, subject,
               html_content, recipient_name, attachment_path=None):
    """
    Send a confirmation email with HTML content.
    """
    try:
        # Use 'mixed' to allow attachments
        message = MIMEMultipart('mixed')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email

        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        # Optionally attach a file (e.g., <int>.png)
        if attachment_path and os.path.isfile(attachment_path):
            try:
                with open(attachment_path, 'rb') as file_handle:
                    payload = MIMEBase('application', 'octet-stream')
                    payload.set_payload(file_handle.read())
                encoders.encode_base64(payload)
                filename_only = os.path.basename(attachment_path)
                payload.add_header('Content-Disposition', f'attachment; filename="{filename_only}"')
                message.attach(payload)
                logger.info(f"Attached file: {filename_only} to {recipient_email}")
            except Exception as attach_error:
                logger.warning(f"Could not attach file {attachment_path} for {recipient_email}: {attach_error}")

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

def process_csv_recipients(csv_file_path, smtp_settings, dry_run=False, images_dir=None, int_column='reg'):
    """
    Process recipients from CSV file and send confirmation emails.
    """
    recipients = read_csv_data(csv_file_path, int_column=int_column)

    if not recipients:
        logger.error(f"No valid recipients found in CSV file: {csv_file_path}")
        return

    logger.info(f"Found {len(recipients)} recipients to process")

    success_count = 0
    failed_count = 0

    for recipient in recipients:
        name = recipient['name']
        int_value = (recipient.get('int') or '').strip()
        email = f"{int_value}@klu.ac.in" if int_value else ''

        html_content = create_html_email(name)
        subject = f"Certificate for AgentSpeak Workshop - Prompt! Plan! Perform!"

        logger.info(f"Processing: {name} -> {email}")

        # Determine attachment path if images_dir and int are provided
        attachment_path = None
        if images_dir and int_value:
            candidate = os.path.join(images_dir, f"{int_value}.png")
            if os.path.isfile(candidate):
                attachment_path = candidate
            else:
                logger.warning(f"Image not found for int '{int_value}' at {candidate}. Proceeding without attachment.")

        if dry_run:
            if attachment_path:
                logger.info(f"[DRY RUN] Would send email to {email} ({name}) with attachment {os.path.basename(attachment_path)}")
            else:
                logger.info(f"[DRY RUN] Would send email to {email} ({name}) without attachment")
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
                name,
                attachment_path
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
    parser.add_argument('--csv', '-c', required=True, help='CSV file containing names and emails (columns: name, email,reg)')
    parser.add_argument('--email', '-e', required=True, help='Sender email address')
    parser.add_argument('--password', '-p', required=True, help='Email password')
    parser.add_argument('--server', '-s', default='smtp.gmail.com', help='SMTP server address')
    parser.add_argument('--port', '-pt', type=int, default=587, help='SMTP server port')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Perform a dry run without sending emails')
    parser.add_argument('--images', '-i', help='Directory containing images named as <int>.png to attach')
    parser.add_argument('--int-col', '-ic', default='reg', help='CSV column name that contains the int used to pick the image (default: reg)')

    args = parser.parse_args()

    smtp_settings = {
        'server': args.server,
        'port': args.port,
        'email': args.email,
        'password': args.password
    }
    process_csv_recipients(args.csv, smtp_settings, args.dry_run, args.images, args.int_col)

if __name__ == "__main__":
    main()
