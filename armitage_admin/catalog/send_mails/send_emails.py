import smtplib


def send_notifications(project_id, project_name):
    gmail_user = 'johnborn9517@gmail.com'
    gmail_password = 'gihan12345'

    sent_from = gmail_user
    to = 'gihangamage.15@cse.mrt.ac.lk'
    subject = 'Client has queued new project'
    body = 'Client has added a new project \n' \
           'Project_ID : %s\n' \
           'Name : %s\n'%(project_id,project_name)

    email_text = """\
   Subject: %s\n

   %s
   """ % ( subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()

        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
    except SyntaxError as e:
        print('Something went wrong...')

# send_notifications('123','name')