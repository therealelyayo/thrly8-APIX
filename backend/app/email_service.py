import smtplib
from email.message import EmailMessage
import time
from datetime import datetime
import subprocess

def send_email_smtp(host, port, username, password, from_name, to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"{from_name} <{username}>"
    msg['To'] = to_email
    msg.set_content(body, subtype='html')

    try:
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()
            server.login(username, password)
            server.send_message(msg)
        return True, f"Email sent successfully to {to_email} via SMTP."
    except Exception as e:
        return False, f"Failed to send email to {to_email} via SMTP: {e}"

def send_email_localhost(from_name, to_email, subject, body):
    try:
        with smtplib.SMTP('localhost', 25) as server:
            server.sendmail(from_name, to_email, body)
        return True, f"Email sent successfully to {to_email} via localhost SMTP."
    except Exception as e:
        return False, f"Failed to send email to {to_email} via localhost SMTP: {e}"

def send_email_api(subject, body, from_name, to_email):
    # Escape double quotes and newlines for JSON in API call
    email_body_api = body.replace('"', '\\"').replace('\n', '\\n')

    curl_command = f"""
    curl --request POST \\
      --url https://api.us.nylas.com/v3/grants/d0f5bd96-d2cd-4ebe-a5a2-5c4546fc9006/messages/send \\
      --header 'Authorization: Bearer nyk_v0_IDxmJtl9h5BGx1ZCpKBxssPwrLTTmrDheQoZhBFNzeYiFSyQFeDOsq61FAIvPGOf' \\
      --header 'Content-Type: application/json' \\
      --data '{{ 
        "subject": "{subject}",
        "body": "{email_body_api}",
        "from": [
            {{
              "name": "{from_name}"
            }}
        ],
        "to": [
            {{
                "email": "{to_email}",
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

    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        return False, stderr.decode()
    return True, stdout.decode()

def send_bulk_emails(emails, subjects, email_body_template, send_method, smtp_mode=None, smtp_credentials=None, from_name="Email Support", send_speed=1.0):
    delay = 1.0 / send_speed
    results = []
    for index, email in enumerate(emails):
        email = email.strip()
        emailname, domain = email.split('@')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = subjects[index % len(subjects)]
        subject_with_placeholders = subject.replace('{{domain}}', domain).replace('{{emailname}}', emailname).replace('{{time}}', current_time)

        email_body = email_body_template.replace('{{recipient_email}}', email)
        email_body = email_body.replace('{{domain}}', domain)
        email_body = email_body.replace('{{emailname}}', emailname)
        email_body = email_body.replace('{{time}}', current_time)
        email_body = email_body.replace('{{subject}}', subject_with_placeholders)
        email_body = email_body.replace('{{from_name}}', from_name)

        if send_method == "SMTP":
            if smtp_mode == "localhost":
                success, message = send_email_localhost(from_name, email, subject_with_placeholders, email_body)
            elif smtp_mode == "smtp":
                host, port, username, password = smtp_credentials
                success, message = send_email_smtp(host, port, username, password, from_name, email, subject_with_placeholders, email_body)
            else:
                success, message = False, "Invalid SMTP mode"
        else:
            success, message = send_email_api(subject_with_placeholders, email_body, from_name, email)

        results.append({"email": email, "success": success, "message": message})
        time.sleep(delay)
    return results
