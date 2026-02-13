import streamlit as st
import subprocess
import os
import zipfile
import re
import smtplib
from email.message import EmailMessage
import sys  # <--- ADD THIS LINE
# --- HELPER FUNCTIONS ---

def is_valid_email(email):
    """Validates the email format using Regular Expressions."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

def zip_file(mp3_filename, zip_filename):
    """Compresses the MP3 file into a ZIP archive."""
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(mp3_filename)

def send_email(receiver_email, zip_filename):
    """Sends the ZIP file to the provided email address."""
    
    # Securely pulling credentials from .streamlit/secrets.toml
    sender_email = st.secrets["EMAIL_ADDRESS"]
    sender_password = st.secrets["EMAIL_PASSWORD"]

    msg = EmailMessage()
    msg['Subject'] = 'Your Youtube Mashup is Ready!'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Hi there!\n\nAttached is your requested YouTube audio mashup in ZIP format. Enjoy!\n\n- Mashup Web Service")

    # Attach the ZIP file
    with open(zip_filename, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='zip', filename=zip_filename)

    # Connect to Gmail's SMTP server and send
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
# --- STREAMLIT UI ---

st.title("🎵 YouTube Audio Mashup Generator")
st.markdown("Enter the details below to generate a custom mashup of your favorite artist and get it delivered straight to your inbox!")

# Input fields matching the assignment requirements
singer_name = st.text_input("Singer Name", placeholder="e.g., Sharry Mann")
num_videos = st.number_input("Number of Videos", min_value=11, step=1, value=20, help="Must be greater than 10")
duration = st.number_input("Duration of each video (seconds)", min_value=21, step=1, value=30, help="Must be greater than 20")
email_id = st.text_input("Email ID", placeholder="e.g., psrana@gmail.com")

if st.button("Submit"):
    # 1. Validation phase
    if not singer_name or not email_id:
        st.error("Please fill in all the fields.")
    elif not is_valid_email(email_id):
        st.error("Invalid Email ID. Please enter a correct email address.")
    else:
        # 2. Processing phase
        st.info("Validation successful! Starting the mashup process. This may take a few minutes...")
        
        output_mp3 = "102303658-output.mp3"
        output_zip = "102303658-output.zip"

        with st.spinner('Downloading and merging audio...'):
            try:
                # Run your Component 1 script via subprocess
                command = ["python", "102303658.py", singer_name, str(num_videos), str(duration), output_mp3]
                subprocess.run(command, check=True)
                
                st.success("Mashup generated successfully! Zipping the file...")
                
                # Zip the file
                zip_file(output_mp3, output_zip)
                
                st.success("File zipped! Sending email...")
                
                # Send the email
                send_email(email_id, output_zip)
                
                st.balloons()
                st.success(f"Done! The mashup has been sent to {email_id}.")
                
            except subprocess.CalledProcessError:
                st.error("An error occurred while generating the mashup. Check your command-line script.")
            except smtplib.SMTPAuthenticationError:
                st.error("Email Authentication Failed! Make sure you updated the sender_email and sender_password in the code.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            
            finally:
                # Cleanup: remove the generated files so the server doesn't get cluttered
                if os.path.exists(output_mp3):
                    os.remove(output_mp3)
                if os.path.exists(output_zip):

                    os.remove(output_zip)
