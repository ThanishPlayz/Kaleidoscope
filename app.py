import json
import re
from PIL import Image, ImageDraw, ImageFont
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# Replace these with your actual email details
sender_email = 'aiprojects.boazpublicschool@gmail.com'      # Your Gmail address
sender_password = 'Kaleidoscope'  # Your Gmail password or app password


# Load participant data
def load_data(filename='responses.json'):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Extract email IDs and names
def extract_emails(data):
    participants = []
    for entry in data:
        email = entry.get('email')
        name = entry.get('name')
        if email and re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Simple email validation
            participants.append({'name': name, 'email': email})
    return participants

# Generate a personalized certificate using PNG template
def generate_certificate(name, template_path='certificate_template.png', output_path='certificates/'):
    # Make sure the output path exists
    import os
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Load the certificate template
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)

    # Load a font (You may need to download a suitable .ttf font file)
    font = ImageFont.truetype("arial.ttf", 60)  # Adjust the font size and type as needed

    # Set the position where the name should be placed (adjust coordinates based on your template)
    name_position = (500, 300)  # (x, y) coordinates - adjust these for your PNG template
    name_color = (0, 0, 0)  # Color of the text (black)

    # Draw the participant's name onto the certificate
    draw.text(name_position, name, fill=name_color, font=font)

    # Define the output filename
    filename = f"{output_path}{name.replace(' ', '_')}_certificate.png"
    image.save(filename)

    return filename

# Send an email with the certificate attached
def send_email(to_address, name, certificate_path, smtp_server, smtp_port, sender_email, sender_password):
    # Email setup
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_address
    msg['Subject'] = "Certificate of Participation"

    # Email body
    body = f"Dear {name},\n\nThank you for participating in our SECULARISM QUIZ! Please find your certificate attached.\n\nBest Regards,\nQuiz Organizers"
    msg.attach(MIMEText(body, 'plain'))

    # Attach certificate
    with open(certificate_path, "rb") as attachment:
        part = MIMEApplication(attachment.read(), _subtype="png")
        part.add_header('Content-Disposition', 'attachment', filename=f'{name}_certificate.png')
        msg.attach(part)

    # Send email
    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Main function to process participants and send emails
def main():
    # Load data from JSON
    data = load_data('responses.json')
    participants = extract_emails(data)
    
    # SMTP configuration (use your email details)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'your_email@gmail.com'
    sender_password = 'your_email_password'

    # Iterate through each participant, generate certificates, and send emails
    for participant in participants:
        name = participant['name']
        email = participant['email']

        # Generate certificate
        certificate_path = generate_certificate(name)
        
        # Send email
        send_email(email, name, certificate_path, smtp_server, smtp_port, sender_email, sender_password)
        print(f"Email sent to {name} at {email}")

if __name__ == "__main__":
    main()
