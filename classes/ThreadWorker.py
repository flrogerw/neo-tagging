import re
from pathlib import Path
from classes.TagGraph import TagGraph
from classes.WordBag import WordBag
import threading
import queue
import traceback


class ThreadWorker(threading.Thread):

    def __init__(self, jobs_q, user, password, text_processor, thread_lock, host_name="localhost", port=7687, database="neo4j", scheme="neo4j", *args, **kwargs):
        self.job_queue = jobs_q
        self.uri = f"{scheme}://{host_name}:{port}"
        self.user = user
        self.password = password
        self.database = database
        self.text_processor = text_processor
        self.thread_lock = thread_lock
        self.graph = TagGraph(self.uri, self.user, self.password, self.database)
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            try:
                filename = self.job_queue.get(timeout=30)
                self.process(filename)

            except queue.Empty:
                self.graph.close()
                return

    def process(self, filename, air_play_date=1716413530):
        try:
            txt = Path(f'corpus_files/Raw_data/{filename}').read_text()
            txt = re.sub(r'[\S]+\.(net|com|org|info|edu|gov|uk|de|ca|jp|fr|au|us|ru|ch|it|nel|se|no|es|mil)[\S]*\s?',
                         '', txt)
            doc = self.text_processor.get_ner('en', txt)
            keywords = self.filter_ner_sentences(doc.sentences)
            weighted_keywords = WordBag.get_weight(keywords)
            self.graph.create_content(weighted_keywords, filename, air_play_date)
        except Exception as err:
            print(filename, err)

    def normalize_token(self, t):
        if len(t) > 1:
            t[0]['text'] = t[1]['text']
            return t[0]
        else:
            return t[0]

    def filter_ner_sentences(self, sentences):
        try:
            final = []
            xpos_types = ['NNP', 'NNPS', 'DT']
            # ner_types = ['LOC', 'PERSON', 'PERCENT', 'ORG', 'WORK_OF_ART', 'GPE', 'EVENT', 'FAC', 'PRODUCT', 'NORP']
            ner_types = ['PERSON', 'ORG', 'GPE', 'EVENT', 'FAC', 'PRODUCT', 'NORP']
            temp_ner = ''
            for sent in sentences:
                for t in sent.tokens:
                    t = t.to_dict()
                    t = self.normalize_token(t)
                    if t["ner"] != "O" and t["ner"] != "S-PERSON":
                        position, ner = t["ner"].split("-")
                        if ner in ner_types:
                            if position == "S":
                                final.append(t["text"])
                            else:
                                if position == 'B':
                                    temp_ner = ''
                                    if ner != 'EVENT' and 'xpos' in t and t['xpos'] in xpos_types and t['text'].istitle():
                                        temp_ner = t['text']
                                    elif type(t['id']) is tuple and t['text'].istitle():
                                        nt = self.text_processor.get_ner('en', t['text'])
                                        nt = nt.to_dict()[0][0]
                                        if nt["ner"] != "O" and nt['xpos'] in xpos_types:
                                            temp_ner = nt['text']
                                else:
                                    temp_ner += f" {t['text']}"
                            if position == 'E':
                                final.append(temp_ner.strip())
            return final
        except Exception as err:
            print(err)

