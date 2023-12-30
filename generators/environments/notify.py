import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email(subject, message, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    body = MIMEText(message, 'plain')
    msg.attach(body)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def main():
    smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
    smtp_port = 587  # Replace with your SMTP port
    to_email = 'EMAIL_USER'  # Replace with the recipient's email address
    from_email = os.environ.get('EMAIL_USER')  # Sender's email address from environment variable
    smtp_user = os.environ.get('EMAIL_USER')  # SMTP user from environment variable
    smtp_password = os.environ.get('EMAIL_PASS')  # SMTP password from environment variable

    subject = 'Generation Complete'
    message = f'Generation process completed on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.'

    send_email(subject, message, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password)

if __name__ == '__main__':
    main()
