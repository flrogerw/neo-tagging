import os
import queue
import time
import traceback
import threading
from datetime import datetime
from dotenv import load_dotenv
from classes.ThreadWorker import ThreadWorker
from ner.StanzaNER import StanzaNER

# Load System ENV VARS
load_dotenv()
JOB_QUEUE_SIZE = int(os.getenv('JOB_QUEUE_SIZE'))
THREAD_COUNT = int(os.getenv('THREAD_COUNT'))
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

thread_lock = threading.Lock()
good_record_count = 0
total_record_count = 0

# Set up Queues
jobs_q = queue.Queue(JOB_QUEUE_SIZE)
errors_q = queue.Queue()


def flush_queues():
    try:
        with thread_lock:
            errors_list = list(errors_q.queue)
            errors_q.queue.clear()
        if errors_list:
            print(errors_list)
    except Exception:
        raise


def monitor(x, stop):
    try:
        starting_time = datetime.now()
        while True:
            time.sleep(10)
            if stop():
                break
            elapsed_time = datetime.now() - starting_time
            print(f'Elapsed Time: {elapsed_time} Jobs Queue Size: {jobs_q.qsize()}')
    except Exception as e:
        print(traceback.format_exc())
        pass


if __name__ == '__main__':
    try:
        print('Process Started')
        text_processor = StanzaNER(['en', 'es', 'ru'])
        stop_monitor = False
        threads = []
        for i in range(THREAD_COUNT):
            w = ThreadWorker(jobs_q, NEO4J_USER, NEO4J_PASSWORD, text_processor, thread_lock)
            threads.append(w)

        start_time = datetime.now()
        for filename in os.listdir('corpus_files/Raw_data'):
            total_record_count += 1
            jobs_q.put(filename)
        print(f'Jobs Queue Populated with {total_record_count} in {datetime.now() - start_time}', flush=True)

        # Start Monitor Thread
        print('Starting Monitor Thread')
        threading.Thread(target=monitor, args=('place_holder', lambda: stop_monitor)).start()

        print('Starting Worker Threads')
        for thread in threads:
            thread.start()

        jobs_q.join()
        for thread in threads:
            thread.join()

        print('All Threads have Finished')
        stop_monitor = True
    except Exception as err:
        print(traceback.format_exc())
