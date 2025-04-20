import datetime, base64, os

from email.mime.text import MIMEText
import socket
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from Config.Config import Config
import Crawling.utils as utils



class Mailer:

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, config: Config):
        """
        Initialize the Mailer with SMTP server details and sender's email credentials.
        """
        self.smtp_server_domain_name = config.mailer_smtp_server
        self.port = config.mailer_port
        self.sender_mail = config.mailer_email
        self.mailing_list = config.mailer_mailing_list

        orig_getaddrinfo = socket.getaddrinfo
        def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
            return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

        socket.getaddrinfo = getaddrinfo_ipv4

    def get_service(self):
        token_path = "./Config/.config/mail_token.json"
        creds_path = "./Config/.config/mail_credentials.json"
        creds = None

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
            creds = flow.run_local_server(port=8888, open_browser=False)

            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)
    
    def _create_message(self, sender, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def _send_mail(self, subject, content) :
        service = self.get_service()
        for email in self.mailing_list:
            message = self._create_message(self.sender_mail, email, subject, content)
            try:
                service.users().messages().send(userId='me', body=message).execute()
            except Exception as e:
                print(f"An error occurred for {email}: {e}")

    def send_eror_mail(self, error: Exception):
        """
        Send an error message via email.
        """
        subject = "Error in Wikipedia Crawl"
        content = f"""
        An error occurred during the Wikipedia crawl:
        
        Error: {str(error)}
        
        Please check the logs for more details.
        """
        self._send_mail(subject, content)
        
    def send_result_mail(self, result_dict: dict):
        """
        Send the result of the Wikipedia crawl via email.
        """
        subject = "Wikipedia Crawl Result"
        content = f"""
        Initial Data:
        Start URL: {result_dict['start_url']}
        Domain: {result_dict['domain']}
        Depth: {result_dict['depth']}

        Result:
        Visited: {result_dict['visited']}
        Total: {result_dict['total']}
        
        Details:
        Started_at: {datetime.datetime.fromtimestamp(result_dict['started_at']).strftime('%Y-%m-%d %H:%M:%S')}
        Finished_at: {datetime.datetime.fromtimestamp(result_dict['finished_at']).strftime('%Y-%m-%d %H:%M:%S')}
        Duration: {utils.format_duration(result_dict['duration'])}

        """
        self._send_mail(subject, content)