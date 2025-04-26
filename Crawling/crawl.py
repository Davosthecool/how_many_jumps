import asyncio

from Config.Config import Config
from Services.Crawler.WikipediaCrawler import WikipediaCrawler
from Services.Crawler.WikipediaDatabase import WikipediaDatabase
from Services.Mailer.Mailer import Mailer

async def explore_wikipedia(config: Config):
    db = WikipediaDatabase(config.db_path, config.log_path)
    print("Connecting to database...")
    await db.connect()
    print("Loading pages...")
    pages = await db.load_all_pages()
    print("Crawling...")
    result = await WikipediaCrawler(config.log_path).deep_crawl(config.wikipedia_start_url, pages, db, config.wikipedia_max_depth)
    print("Closing Connection...")
    await db.close()
    return result

if __name__ == "__main__":
    
    config = Config()
    print("Config completed.")
    print("Connecting to mailer...")
    mailer = Mailer(config)
    mailer.get_service()
    print("Mailer connected.")

    try:
        print("Starting Wikipedia exploration...")
        result = asyncio.run(explore_wikipedia(config))
        print("Sending email...")
        mailer.send_result_mail(result)
        print("Crawling completed and email sent.")
    except Exception as e:
        print(f"An error occurred: {e}")
        mailer.send_eror_mail(e)
        raise e
    
