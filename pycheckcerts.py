################################
#  Max J. Rodriguez Beltran    #
#  maxjrb[at]openitsinaloa.com #
#  https://openitsinaloa.com   #
#  2018                        #
################################
import ssl, socket
import os.path
import smtplib
import argparse

from datetime import datetime
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#########VARS##########
listHosts=[]
my_path = os.path.abspath(os.path.dirname(__file__))
filehosts = os.path.join(my_path,"Hosts")
daysToCheck = 3 #Change it to the days you want to set to send mail to warn you about expire day
#######################

parser = argparse.ArgumentParser()
parser.add_argument("--resume", "-r", help="resume all hosts in 1 mail", action="store_true")
parser.add_argument("--url", "-u", help="pass host to check for expiry date", action="append")
args = parser.parse_args()

def send_mail(content):

    message = MIMEMultipart()
    # Change to the mail that you want to send
    message['Subject'] = "Certs close to expire"
    message['From'] = "certchecker@yourmail.com"
    message['To'] = "yourmail@mail.com, othermail@othermail.com"

    body = MIMEText(content, 'html')
    message.attach(body)

    with smtplib.SMTP_SSL('smtp.powweb.com',465) as server:
        server.login('certchecker@yourmail.com',"YourSecurePassw0rd")
        server.send_message(message)
        server.quit()

def checkCert(hostname):
    days_to_expire = 0
    context = ssl.create_default_context()
    connection = context.wrap_socket(socket.socket(), server_hostname=hostname)

    try:
        connection.connect((hostname, 443))
        cert = connection.getpeercert()
        expdate = cert['notAfter']
        datetime_object = datetime.strptime(expdate, '%b %d %H:%M:%S %Y %Z')
        date_today = datetime.today()
        days_to_expire = datetime_object - date_today
        days_to_expire = days_to_expire.days
    except:
        days_to_expire = 99

    return  days_to_expire

def checkHosts (hostsList, checkDays = False):
    for host in hostsList:
        daysToExpire = checkCert(host.strip())
        message=f"""<!DOCTYPE html>
            <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <title></title>
            <meta name="description" content="">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <div style="position: relative; text-align: center; color: white;">
                <img src="https://i.imgur.com/SxzZBDF.png" alt="xpmessage" style="width:40%;">
                <div style="position: absolute; top: 45%; left:50%; transform: translate(-50%, -50%); font-size: 19px; font-family: Tahoma, Geneva, Verdana, sans-serif; color: rgba(55, 63, 71, 0.822)"><p>{host}</p>En {daysToExpire} días!
                </div>
            </div>
        </body>
        </html>"""
        if checkDays:
            if daysToExpire <= daysToCheck:
                send_mail(message)
        else:
            send_mail(message)

#If --url arg is passed, will check for every host is passed as argument and will send one mail per host
if args.url:
    checkHosts(args.url)
    exit(0)

if not os.path.isfile(filehosts):
    print("File Hosts doesn't exist...")
    exit(2)

with open(filehosts, mode='r') as hostsfile:
    listHosts = [(line.strip()).replace("\n","") for line in hostsfile if '#' not in line]

#If --resume arg is passed, will check for every host in Hosts file and will send them all listed in one mail
if args.resume :
    if listHosts:
        message = f"""<!DOCTYPE html>
        <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title></title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Certificate List and their expiracy date:</h1>
        </br>"""
        for host in listHosts:
            daysToExpire = checkCert(host)
            message+=f"""<p>The host: {host} expires in {daysToExpire} days!</p>
            """
        message+=f"""</body>
        </html>"""
        send_mail(message)
    exit(0)

if listHosts:
    checkHosts(listHosts, True)