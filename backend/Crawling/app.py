import asyncio
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from redis import Redis
from rq import Queue

from Config.Config import Config
from Services.Crawler.WikipediaDatabase import WikipediaDatabase
from Services.Worker.CustomWorker import CustomWorker
from crawl import crawl_task
from Services.Worker.worker_hooks import on_success, on_failure, on_start

app = Flask(__name__)
CORS(app)

config = Config()
db = WikipediaDatabase(config.db_path, config.log_path)

redis_conn = Redis(
    host='redis-18330.crce202.eu-west-3-1.ec2.redns.redis-cloud.com',
    port=18330,
    decode_responses=True,
    username="default",
    password="T8KkjFCsm5brnNFnDAwJSVElemhjtecG",
)
q = Queue(connection=redis_conn)

def start_worker():
    worker = CustomWorker([q], connection=redis_conn)
    worker.work(with_scheduler=False)
threading.Thread(target=start_worker, daemon=True).start()


@app.before_request
def before_request():
    asyncio.run(db.connect())

@app.teardown_request
def teardown_request(exception):
    asyncio.run(db.close())

@app.route('/api/crawl', methods=['POST'])
def crawl():
    data = request.get_json()
    start_url = data.get('start_url')
    max_depth = data.get('max_depth')

    if not start_url or not max_depth:
        return jsonify({"error": "start_url and max_depth are required"}), 400

    try:
        id_history = db.insert_history_sync(url=start_url, depth=max_depth, status='queued')

        job = q.enqueue(
            crawl_task,
            start_url,
            max_depth,
            id_history,
            on_start=on_start,
            on_success=on_success,
            on_failure=on_failure
        )
        job.meta['id_history'] = id_history
        job.meta['config'] = {
            'db_path': config.db_path,
            'log_path': config.log_path
        }
        job.save()

        return jsonify({
            "message": "Crawling task enqueued",
            "job_id": job.get_id(),
            "start_url": start_url,
            "max_depth": max_depth
        }), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)