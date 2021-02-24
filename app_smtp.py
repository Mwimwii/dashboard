import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os.path


def send_email(email_recipients,
               email_subject,
               email_message,
               attachment_location = ''):

    email_sender = 'sysdev@grz.gov.zm'

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipients
    msg['Subject'] = email_subject


    # msg.attach(MIMEText(html, 'html'))
    msg.attach(MIMEText(email_message, 'html'))
    

    # This example assumes the image is in the current directory
    fp = open('h1.gif', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)
    # if attachment_location != '':
    #     filename = os.path.basename(attachment_location)
    #     attachment = open(attachment_location, "rb")
    #     part = MIMEBase('application', 'octet-stream')
    #     part.set_payload(attachment.read())
    #     encoders.encode_base64(part)
    #     part.add_header('Content-Disposition',
    #                     "attachment; filename= %s" % filename)
    #     msg.attach(part)

    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        print('Attempting to reach server')
        server.ehlo()
        print('Echo recieved')
        print('Attempting to TTLS')
        server.starttls()
        print('TTLS Succesful')
        user_cred = ('user','pass')

        print(f'Attempting to Login {user_cred}')
        server.login(*user_cred)
        print('Login Succesful')
        text = msg.as_string()
        print('Attempting to ')
        for email_recipient in email_recipients:
            server.sendmail(email_sender, email_recipients, text)
        print('email sent')
        

        server.quit()
    except Exception as err:
        print(err)
        print("SMTP server connection error")
    return True



def template_engine_replace(html, start_stop):
    return True
