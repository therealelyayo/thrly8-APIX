import json
import subprocess
import os
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
 
# ANSI escape codes for formatting
BOLD = "\033[1m"
BLUE = "\033[34m"
RESET = "\033[0m"

# Function to read the license from a URL
def read_license_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching license: {e}")
        return None

# Function to validate the license
def is_license_valid(license_key):
    # Example validation: check if the license key matches a specific string
    return license_key == "VALID_LICENSE_KEY-44erdu75tugj"  # Replace with actual validation logic

# Function to read SMTP credentials from a file
def read_smtp_credentials(filename='smtp_credentials.txt'):
    try:
        with open(filename, 'r') as f:
            line = f.readline().strip()
            host_port, username, password = line.split('|')
            host, port = host_port.split(':')
            return host, int(port), username, password
    except Exception as e:
        print(f"Error reading SMTP credentials: {e}")
        return None, None, None, None

# Function to send email via SMTP
def send_email_smtp(host, port, username, password, from_name, to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"{from_name} <{username}>"
    msg['To'] = to_email
    msg.set_content(body, subtype='html')

    try:
        with smtplib.SMTP(host, port) as server:
            server.set_debuglevel(1)  # Enable debug output
            server.ehlo()
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()
            server.login(username, password)
            server.send_message(msg)
        print(f"Email sent successfully to {to_email} via SMTP.")
    except Exception as e:
        print(f"Failed to send email to {to_email} via SMTP: {e}")

# Print the app name in bold and blue, simulating a larger size
app_name = f"{BOLD}{BLUE}=================Welcome to Thrly Api Sender V2=================={RESET}"
print(f"{app_name}\n\n{app_name}\n\n")  # Print six times for larger appearance

# Highlighting key functionalities
print("This project allows you to:")
print("- Send personalized emails with customizable HTML content.")
print("- Validate licenses to ensure authorized usage.")
print("- Easily manage email subjects and recipients.")
print("- Utilize a secure API for sending messages.")

# Read the license from a URL
license_url = 'https://iowagroups.center/Licensed.txt'  # Replace with the actual URL
license_key = read_license_from_url(license_url)
if not license_key or not is_license_valid(license_key):
    print("Invalid or missing license. Exiting the program.")
    exit(1)

# Set default values
default_html_file = 'gm.html'
default_subjects_file = 'gmsj.txt'
default_from_name = 'Email Support'

# Prompt the user for the HTML file name with default
html_file_name = input(f"Please enter the HTML file name to use as the email body (including .html) [default: {default_html_file}]: ") or default_html_file

# Check if the specified HTML file exists
if not os.path.isfile(html_file_name):
    print(f"Error: The file '{html_file_name}' does not exist.")
    exit(1)

# Prompt the user for the subjects text file name with default
subjects_file_name = input(f"Please enter the subjects text file name (including .txt) [default: {default_subjects_file}]: ") or default_subjects_file

# Check if the specified subjects file exists
if not os.path.isfile(subjects_file_name):
    print(f"Error: The file '{subjects_file_name}' does not exist.")
    exit(1)

# Read subjects from the specified text file
with open(subjects_file_name, 'r') as file:
    subjects = [subject.strip() for subject in file.readlines()]

# Read email addresses from the text file
with open('recipients.txt', 'r') as file:
    emails = file.readlines()

# Read the email body from the specified HTML file
with open(html_file_name, 'r') as file:
    email_body_template = file.read()

import subprocess
import sys

def send_test_email(test_email, from_name):
    test_subject = "Test Email from Thrly Api Sender V2"
    test_body = "<html><body><h1>This is a test email.</h1></body></html>"
    try:
        with smtplib.SMTP('localhost', 25) as server:
            server.sendmail(from_name, test_email, test_body)
        print(f"Test email sent successfully to {test_email} via localhost SMTP.")
        return True
    except Exception as e:
        print(f"Failed to send test email to {test_email} via localhost SMTP: {e}")
        return False

def install_mail_tools():
    print("Installing mail tools silently...")
    try:
        # Detect package manager and install postfix or sendmail silently
        if subprocess.run(["which", "apt-get"], stdout=subprocess.PIPE).returncode == 0:
            subprocess.run(["sudo", "apt-get", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["sudo", "apt-get", "install", "-y", "postfix"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif subprocess.run(["which", "yum"], stdout=subprocess.PIPE).returncode == 0:
            subprocess.run(["sudo", "yum", "install", "-y", "postfix"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            print("Unsupported package manager. Please install mail tools manually.")
            return False
        print("Mail tools installed.")
        return True
    except Exception as e:
        print(f"Failed to install mail tools: {e}")
        return False

# Prompt user to choose sending method
send_method = input("Choose sending method (SMTP/API) [default: API]: ").strip().upper() or "API"

smtp_mode = None
smtp_credentials = None

if send_method == "SMTP":
    while True:
        smtp_mode = input("Choose SMTP mode (localhost/smtp) [default: localhost]: ").strip().lower() or "localhost"
        if smtp_mode == "smtp":
            creds_input = input("Enter SMTP credentials (host:port|username|password): ").strip()
            try:
                host_port, username, password = creds_input.split('|')
                host, port = host_port.split(':')
                smtp_credentials = (host, int(port), username, password)
                # Save to smtp_credentials.txt
                with open('smtp_credentials.txt', 'w') as f:
                    f.write(creds_input + '\n')
                print("SMTP credentials saved to smtp_credentials.txt")
                break
            except Exception as e:
                print(f"Invalid format for SMTP credentials: {e}")
                continue
        elif smtp_mode == "localhost":
            # Interactive test email for localhost mode
            while True:
                test_email = input("Enter an email address to send a test email: ").strip()
                if send_test_email(test_email, default_from_name):
                    proceed = input("Test email sent successfully. Proceed with sending all emails? (yes/i to install mail tools/no): ").strip().lower()
                    if proceed == "yes":
                        break
                    elif proceed == "i":
                        if install_mail_tools():
                            print("Retrying test email...")
                            continue
                        else:
                            print("Installation failed. Please configure mail tools manually.")
                            sys.exit(1)
                    else:
                        print("Aborting email sending.")
                        sys.exit(0)
                else:
                    retry = input("Test email failed. Retry? (yes/no): ").strip().lower()
                    if retry != "yes":
                        print("Aborting email sending.")
                        sys.exit(0)
            break
        else:
            print("Invalid SMTP mode. Please enter 'localhost' or 'smtp'.")


import time

# Ask user for sending speed (emails per second)
try:
    send_speed = float(input("Enter sending speed (emails per second, e.g., 10): ").strip())
    if send_speed <= 0:
        print("Invalid sending speed. Using default 1 email per second.")
        send_speed = 1.0
except Exception:
    print("Invalid input. Using default 1 email per second.")
    send_speed = 1.0

delay = 1.0 / send_speed

# Send emails
for index, email in enumerate(emails):
    email = email.strip()  # Remove any extra whitespace or newline characters
    
    # Split the email into name and domain
    emailname, domain = email.split('@')
    
    # Get the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Cycle through subjects
    subject = subjects[index % len(subjects)]  # Use a new subject for each email
    subject_with_placeholders = subject.replace('{{domain}}', domain).replace('{{emailname}}', emailname).replace('{{time}}', current_time)  # Replace placeholders in subject

    # Replace placeholders in the email body
    email_body = email_body_template.replace('{{recipient_email}}', email)  # Replace placeholder with actual email
    email_body = email_body.replace('{{domain}}', domain)  # Replace domain placeholder
    email_body = email_body.replace('{{emailname}}', emailname)  # Replace email name placeholder
    email_body = email_body.replace('{{time}}', current_time)  # Replace time placeholder
    email_body = email_body.replace('{{subject}}', subject_with_placeholders)  # Replace subject placeholder with domain
    email_body = email_body.replace('{{from_name}}', default_from_name)  # Replace from name placeholder

    if send_method == "SMTP":
        if smtp_mode == "localhost":
            # Use localhost and port 25 for SMTP without authentication
            try:
                with smtplib.SMTP('localhost', 25) as server:
                    server.sendmail(default_from_name, email, email_body)
                print(f"Email sent successfully to {email} via localhost SMTP.")
            except Exception as e:
                print(f"Failed to send email to {email} via localhost SMTP: {e}")
        elif smtp_mode == "smtp":
            # Use saved SMTP credentials for authenticated sending
            try:
                host, port, username, password = smtp_credentials
                msg = EmailMessage()
                msg['Subject'] = subject_with_placeholders
                msg['From'] = f"{default_from_name} <{username}>"
                msg['To'] = email
                msg.set_content(email_body, subtype='html')

                with smtplib.SMTP(host, port) as server:
                    server.ehlo()
                    if server.has_extn('STARTTLS'):
                        server.starttls()
                        server.ehlo()
                    server.login(username, password)
                    server.send_message(msg)
                print(f"Email sent successfully to {email} via SMTP server {host}:{port}.")
            except Exception as e:
                print(f"Failed to send email to {email} via SMTP server {host}:{port}: {e}")
    else:
        # Escape double quotes and newlines for JSON in API call
        email_body_api = email_body.replace('"', '\\"').replace('\n', '\\n')

        # Define the cURL command template
        curl_command = f"""
        curl --request POST \\
          --url https://api.us.nylas.com/v3/grants/d0f5bd96-d2cd-4ebe-a5a2-5c4546fc9006/messages/send \\
          --header 'Authorization: Bearer nyk_v0_IDxmJtl9h5BGx1ZCpKBxssPwrLTTmrDheQoZhBFNzeYiFSyQFeDOsq61FAIvPGOf' \\
          --header 'Content-Type: application/json' \\
          --data '{{ 
            "subject": "{subject_with_placeholders}",
            "body": "{email_body_api}",
            "from": [
                {{
                  "name": "{default_from_name}"
                }}
            ],
            "to": [
                {{
                    "email": "{email}",
                    "replyto": "idan@sent.com"
                }}
            ],
            "tracking_options": {{
                "opens": true,
                "links": true,
                "thread_replies": false,
                "label": "Gmail"
            }}
        }}'
        """

        # Execute the cURL command
        process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # Print the output
        if stderr:
            print(f"Thrly8 Api Send successfully for {email}: {stderr.decode()}")

    time.sleep(delay)
