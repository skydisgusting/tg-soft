import shutil
import requests
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.message import Message
from email.mime.multipart import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from Tools.demo.mcast import sender
from email.header import Header
from email.utils import parseaddr, formataddr

def prepare_mail(account, get_chose, target):
	if get_chose == '1':
		if send_mail(account=account, reason="Child Abuse", target=target) == 1:
			return 1
		else:
			return 0
	elif get_chose == '2':
		if send_mail(account=account, reason="Fake", target=target) == 1:
			return 1
		else:
			return 0
	elif get_chose == '3':
		if send_mail(account=account, reason="Other", target=target) == 1:
			return 1
		else:
			return 0
	elif get_chose == '4':
		if send_mail(account=account, reason="Spam", target=target) == 1:
			return 1
		else:
			return 0
	elif get_chose == '5':
		if send_mail(account=account, reason="Copyright", target=target) == 1:
			return 1
		else:
			return 0
	elif get_chose == '6':
		if send_mail(account=account, reason="Pornography", target=target) == 1:
			return 1
		else:
			return 0
	elif get_chose == '7':
		if send_mail(account=account, reason="Violence", target=target) == 1:
			return 1
		else:
			return 0
	else:
		print("Error")

def send_mail(account, reason, target):
	mail_data = account.split(':')
	msgtext = MIMEText(f'Report for: {reason} \nLink: {target[0]}'.encode('utf-8'), 'plain', 'utf-8')
	msg = MIMEMultipart()
	msg['From'] = mail_data[0]
	msg['To'] = 'abuse@telegram.org'
	msg['Subject'] = f"{reason}"
	msg.attach(msgtext)

	try:
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.starttls()
		login = s.login(mail_data[0], mail_data[1])
		sending = s.sendmail(mail_data[0], 'abuse@telegram.org', msg.as_string())
		s.quit()
		return 1
	except Exception as e:
		print(f"[ - ] Произошла ошибка. Ее содержимое {e}")
		return 0