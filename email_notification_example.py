import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import random
import openai

openai.api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "text-davinci-003" 

response = openai.Completion.create(
  engine= "text-davinci-003" ,
  prompt="Write a brief email from Josh to the Delmar property management complaining about the condition of the dog park. Pick one thing to complain about; The park is dirty, trash is spread out, there are holes in the ground, there is a lack of grass. Express concern about the health of dogs using the park and how the park's appearance might be impacting potential and current residents.",
  temperature=0.5,
  max_tokens=200
)

email_body = response.choices[0].text.strip()

# Set up the email
msg = MIMEMultipart()
msg['From'] = "joshua9040@gmail.com"
msg['To'] = "joshua9040@gmail.com"
msg['Subject'] = "Concerns About the Condition of the Delmar Dog Park"

msg.attach(MIMEText(email_body, 'plain'))

# Choose a random picture from the directory
pictures_directory = "dogpark"
picture_filename = random.choice([
    x for x in os.listdir(pictures_directory) 
    if os.path.isfile(os.path.join(pictures_directory, x))
])

# Attach the picture
with open(os.path.join(pictures_directory, picture_filename), 'rb') as f:
    img = MIMEImage(f.read())
    img.add_header('Content-Disposition', 'attachment', filename=picture_filename)
    msg.attach(img)

# Send the email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("joshua9040@gmail.com", "dbtkldktfitkzzoy")
text = msg.as_string()
server.sendmail("joshua9040@gmail.com", "joshua9040@gmail.com", text)
server.quit()
