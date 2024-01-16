import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version


def send_email(email , verification_code):
    print(email, verification_code)
    server = 'smtp.yandex.ru'
    user = 'about.uz@yandex.ru'
    password = 'pfjekzkkkiyqwbik'

    recipients = [f"{email}"]
    sender = 'about.uz@yandex.ru'
    subject = 'Parol tiklash.'
    text = f'<b>Parolingiz tiklash uchun tasdiqlash kodi </b><h1>{verification_code}</h1>'
    html = '<html><head></head><body><p>' + text + '</p></body></html>'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Chikim app <' + sender + '>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())

    part_text = MIMEText(text, 'plain')
    part_html = MIMEText(html, 'html')

    msg.attach(part_text)
    msg.attach(part_html)

    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()