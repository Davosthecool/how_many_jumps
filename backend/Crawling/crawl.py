import asyncio
import time

from Config.Config import Config
from Services.Crawler.WikipediaCrawler import WikipediaCrawler
from Services.Crawler.WikipediaDatabase import WikipediaDatabase
from Services.Mailer.Mailer import Mailer

async def explore_wikipedia(start_url: str, max_depth: int, config: Config, db: WikipediaDatabase, id_history: int) -> list:
    print("Connecting to mailer...")
    mailer = Mailer(config)
    mailer.get_service()
    print("Connecting to database...")
    await db.connect()
    await db.update_history(id_history, 'started')
    try:
        print("Loading pages...")
        pages = await db.load_all_pages()
        print("Crawling...")
        await db.update_history(id_history, 'in_progress')
        result = await WikipediaCrawler(config.log_path).deep_crawl(start_url, memo=pages, database_handler=db, max_depth=max_depth)
        await db.update_history(id_history, 'completed', f"Visited {len(result)} pages", time.time())
        print("Closing database connection...")
        await db.close()
        print("Sending email...")
        mailer.send_result_mail(result)
        print("Crawling completed and email sent.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await db.update_history(id_history, 'failed', str(e),  time.time())
        await db.close()
        mailer.send_eror_mail(e)
        raise e

def crawl_task(start_url: str, max_depth: int, id_history: int):
    config = Config()
    db = WikipediaDatabase(config.db_path, config.log_path)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(db.connect())
    loop.run_until_complete(db.update_history(id_history, 'started'))
    loop.run_until_complete(db.close())

    result = loop.run_until_complete(explore_wikipedia(start_url, max_depth, config, db, id_history))
    return result
