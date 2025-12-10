import resend

from __init__ import from_email


def sendEmail(to, subject, html_content):
    params = {
        "from": from_email,
        "to": to,
        "subject": subject,
        "html": html_content,
    }
    return resend.Emails.send(params)
