import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from CustomWorker import CustomWorker
from redis import Redis
from rq import Queue

if __name__ == "__main__":
    redis_conn = Redis(
        host='redis-18330.crce202.eu-west-3-1.ec2.redns.redis-cloud.com',
        port=18330,
        decode_responses=True,
        username="default",
        password="T8KkjFCsm5brnNFnDAwJSVElemhjtecG",
    )
    q = Queue(connection=redis_conn)
    worker = CustomWorker([q], connection=redis_conn)
    worker.work()
