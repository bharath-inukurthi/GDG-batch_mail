# Email Batch Sender

This script sends personalized confirmation emails to workshop participants using data from a CSV file.

## Features

- Reads recipient data from CSV file (name and email columns)
- Sends personalized HTML emails with recipient names
- Supports dry-run mode for testing
- Comprehensive logging
- Rate limiting to avoid overwhelming SMTP servers

## Requirements

- Python 3.6+
- Access to an SMTP server (Gmail, Outlook, etc.)

## CSV File Format

The CSV file should have the following format with headers:

```csv
name,email
John Doe,john.doe@example.com
Jane Smith,jane.smith@example.com
Alice Johnson,alice.johnson@example.com
```

## Usage

### Basic Usage

```bash
python batch_send.py --csv recipients.csv --email your_email@gmail.com --password your_app_password
```

### With Custom SMTP Settings

```bash
python batch_send.py --csv recipients.csv --email your_email@gmail.com --password your_password --server smtp.gmail.com --port 587
```

### Dry Run (Test Mode)

```bash
python batch_send.py --csv recipients.csv --email your_email@gmail.com --password your_password --dry-run
```

## Command Line Arguments

- `--csv`, `-c`: Path to CSV file containing recipient data (required)
- `--email`, `-e`: Sender email address (required)
- `--password`, `-p`: Email password or app password (required)
- `--server`, `-s`: SMTP server address (default: smtp.gmail.com)
- `--port`, `-pt`: SMTP server port (default: 587)
- `--dry-run`, `-d`: Perform a dry run without sending emails

## Gmail Setup

For Gmail, you'll need to:

1. Enable 2-factor authentication
2. Generate an app password
3. Use the app password instead of your regular password

## Email Template

The script sends a personalized HTML email for the "Repo Ready" Git & GitHub workshop. The email includes:

- Personalized greeting with recipient's name
- Workshop details (venue, date, time)
- Requirements list
- Links to event page and WhatsApp group

## Logging

The script creates detailed logs in `email_sender.log` and displays progress in the console.

## Example

```bash
# Test with dry run first
python batch_send.py --csv sample_recipients.csv --email myemail@gmail.com --password myapppassword --dry-run

# Send actual emails
python batch_send.py --csv sample_recipients.csv --email myemail@gmail.com --password myapppassword
```
