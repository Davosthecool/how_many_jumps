import os
from dotenv import load_dotenv

class Config:
    def __init__(self, config_file: str = ".env"):
        """
        Load environment variables from a .env file.
        """        
        load_dotenv(config_file)
        self.db_path = os.getenv('DB_PATH', default='data/wikipedia_crawl.db')
        self.log_path = os.getenv('LOG_PATH', default='logs/crawler.log')

        self.wikipedia_start_url = os.getenv('WIKIPEDIA_START_URL')
        if not self.wikipedia_start_url: raise ValueError("WIKIPEDIA_START_URL is required")
        self.wikipedia_max_depth = int(os.getenv('WIKIPEDIA_MAX_DEPTH', default=0))


        self.mailer_smtp_server = os.getenv('MAILER_SMTP_SERVER', default='smtp.gmail.com')
        self.mailer_port = int(os.getenv('MAILER_PORT', default=465))
        self.mailer_email = os.getenv('MAILER_EMAIL')
        if not self.mailer_email: raise ValueError("MAILER_EMAIL is required")
        self.mailer_mailing_list = os.getenv('MAILER_MAILING_LIST')
        if not self.mailer_mailing_list: raise ValueError("MAILER_MAILING_LIST is required")
        else: self.mailer_mailing_list = self.mailer_mailing_list.split(',')
