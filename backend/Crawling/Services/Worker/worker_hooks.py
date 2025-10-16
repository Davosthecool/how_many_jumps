import asyncio
import time
from Services.Crawler.WikipediaDatabase import WikipediaDatabase
from Config.Config import Config

def get_db(config: Config):
    return WikipediaDatabase(config.db_path, config.log_path)

def on_success(job, connection, result, *args, **kwargs):
    print(f"[RQ] Job succeeded: {job.id}")
    config = job.meta['config']
    db = get_db(config)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(db.connect())
    loop.run_until_complete(db.update_history(
        job.meta['id_history'],
        'completed',
        f"Visited {len(result)} pages",
        time.time()
    ))
    loop.run_until_complete(db.close())

def on_failure(job, connection, exc_type, exc_value, traceback):
    print(f"[RQ] Job failed: {job.id}")
    config = job.meta['config']
    db = get_db(config)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(db.connect())
    loop.run_until_complete(db.update_history(
        job.meta['id_history'],
        'failed',
        str(exc_value),
        time.time()
    ))
    loop.run_until_complete(db.close())

def on_start(job, connection, *args, **kwargs):
    print(f"[RQ] Job started: {job.id}")
    config = job.meta['config']
    db = get_db(config)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(db.connect())
    loop.run_until_complete(db.update_history(
        job.meta['id_history'],
        'started'
    ))
    loop.run_until_complete(db.close())
