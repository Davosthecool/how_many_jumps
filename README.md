# How Many Jumps

The goal of this application is to aim how many redirection within Wikipedia's pages you need to go from the first one to the second one

## Requirements

Python 3.12 OR docker

### .env
These fields are mandatory:
```
WIKIPEDIA_START_URL= # The Wikipedia page where to start the crawling

MAILER_EMAIL= # The mailer email
MAILER_MAILING_LIST= # all the mail who will receives the mails, ( comma separated list with no spaces)
```

These are optionnal:
```
DB_PATH= # The Sqlite database path and name, default 'data/wikipedia_crawl.db'

WIKIPEDIA_MAX_DEPTH= # The maximum depth from the starting page to go in, default 0

MAILER_SMTP_SERVER= # The smtp server who will handle the mails requests, default 'smtp.gmail.com'

MAILER_PORT = # The port of the smtp server, default 465
```

## How to use

### Python

1. Clone the repository
```
git clone https://github.com/Davosthecool/how_many_jumps.git
cd how_many_jumps
```

2. Create the .env file
```
touch .env # Linux
nano .env # edit the .env file
```

3. Install Dependancies
```
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

4. Execute application
```
python main.py
```

4. (bis) The first time you will launch the app, you will be asked to connect to your google account, just follow the instructions.  

### Docker

1. Clone the repository
```
git clone https://github.com/Davosthecool/how_many_jumps.git
cd how_many_jumps
```

### TODO : rajouter les etapes du setup du token google 
2. Create the .env file
```
touch .env # Linux
nano .env # edit the .env file
```

3. Build the Docker image
```
docker build -t how-many-jumps .
```

4. Execute application
```
./run.sh
```