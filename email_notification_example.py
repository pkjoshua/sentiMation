import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up the email
msg = MIMEMultipart()
msg['From'] = "joshua9040@gmail.com"
msg['To'] = "joshua9040@gmail.com"
msg['Subject'] = "Concerns About the Condition of the Delmar Dog Park"

# Email body
email_body = "This is where your email body text goes."
msg.attach(MIMEText(email_body, 'plain'))

# Send the email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("joshua9040@gmail.com", "zavy rzqd ahar bdcv")
text = msg.as_string()
server.sendmail("joshua9040@gmail.com", "joshua9040@gmail.com", text)
server.quit()
