import resend

from __init__ import from_email
from enums import Level

level_vn = {
    Level.BEGINNER: "Cơ bản",
    Level.INTERMEDIATE: "Trung cấp",
    Level.ADVANCED: "Nâng cao",
}


def sendEmail(to, subject, html_content):
    params = {
        "from": from_email,
        "to": to,
        "subject": subject,
        "html": html_content,
    }
    return resend.Emails.send(params)
