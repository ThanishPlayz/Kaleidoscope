import json
import re
import base64
from PIL import Image, ImageDraw, ImageFont
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

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

# Send an email with the certificate using SendGrid API
def send_email_via_sendgrid(to_address, name, certificate_path, sendgrid_api_key):
    with open(certificate_path, 'rb') as f:
        file_data = f.read()
        encoded_file = base64.b64encode(file_data).decode()

    # Prepare the email content
    message = Mail(
        from_email='your_email@domain.com',  # Replace with your verified sender email
        to_emails=to_address,
        subject="Certificate of Participation",
        html_content=f"Dear {name},<br><br>Thank you for participating in our SECULARISM QUIZ!<br>Please find your certificate attached.<br><br>Best Regards,<br>Quiz Organizers"
    )

    # Add the certificate as an attachment
    attachment = Attachment(
        FileContent(encoded_file),
        FileName(f'{name}_certificate.png'),
        FileType('application/png'),
        Disposition('attachment')
    )
    message.attachment = attachment

    # Send the email using SendGrid API
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent to {name} at {to_address} with status code {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending email to {to_address}: {e}")

# Main function to process participants and send emails
def main():
    # Load data from JSON
    data = load_data('responses.json')
    participants = extract_emails(data)
    
    # Your SendGrid API key (replace with your actual API key)
    sendgrid_api_key = 'YOUR_SENDGRID_API_KEY'  # Replace with your SendGrid API Key

    # Iterate through each participant, generate certificates, and send emails
    for participant in participants:
        name = participant['name']
        email = participant['email']

        # Generate certificate
        certificate_path = generate_certificate(name)
        
        # Send email via SendGrid
        send_email_via_sendgrid(email, name, certificate_path, sendgrid_api_key)

if __name__ == "__main__":
    main()
