import concurrent.futures
import hashlib
import re
from pathlib import Path
from ner.StanzaNER import StanzaNER
from classes.TagGraph import TagGraph
from classes.WordBag import WordBag
from classes.TagS3 import TagS3
import string
import random
import os

"""
#txt = Path('corpus_files/transcript.txt').read_text()
    
        latest_entries = s3.get_latests()
        for entry in latest_entries:
            content = s3.get_content(entry)
            result = hashlib.md5(content.encode())
            new_hash = result.hexdigest()
            if hasattr(final, new_hash):
                next
            final[new_hash] = content
            count += 1
            print(count)
        for k in final.keys():
            print(final[k], "\n\n")
            #lang = StanzaNER.get_language(text_processor(content))
            #if lang != 'en':
                #print(lang)
      
DATE - absolute or relative dates or periods
PERSON - People, including fictional
GPE - Countries, cities, states
LOC - Non-GPE locations, mountain ranges, bodies of water
MONEY - Monetary values, including unit
TIME - Times smaller than a day
PRODUCT - Objects, vehicles, foods, etc. (not services)
CARDINAL - Numerals that do not fall under another type
ORDINAL - "first", "second", etc.
QUANTITY - Measurements, as of weight or distance
EVENT - Named hurricanes, battles, wars, sports events, etc.
FAC - Buildings, airports, highways, bridges, etc.
LANGUAGE - Any named language
LAW - Named documents made into laws.
NORP - Nationalities or religious or political groups
PERCENT - Percentage, including "%"
WORK_OF_ART - Titles of books, songs, etc.
"""


class Neo:

    def __init__(self, user, password, text_processor, port=7687, database="neo4j", scheme="neo4j",host_name="localhost"):
        self.uri = f"{scheme}://{host_name}:{port}"
        self.user = user
        self.password = password
        self.database = database
        # s3 = TagS3('transcription-engine-data-nonprod-stg')
        self.text_processor = text_processor

    def process(self, filename, air_play_date=1716413530):
        try:
            graph = TagGraph(self.uri, self.user, self.password, self.database)
            txt = Path(f'corpus_files/Raw_data/{filename}').read_text()
            txt = re.sub(r'[\S]+\.(net|com|org|info|edu|gov|uk|de|ca|jp|fr|au|us|ru|ch|it|nel|se|no|es|mil)[\S]*\s?',
                         '', txt)
            doc = self.text_processor.get_ner('en', txt)
            keywords = self.filter_ner_sentences(doc.sentences)
            weighted_keywords = WordBag.get_weight(keywords)
            content_name = f"a_{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"
            graph.create_content(weighted_keywords, content_name, air_play_date)
            graph.close()
        except Exception as err:
            print(filename, err)
        finally:
            self.graph.close()

    def normalize_token(self, t):
        if len(t) > 1:
            t[0]['text'] = t[1]['text']
            return t[0]
        else:
            return t[0]

    def filter_ner_sentences(self, sentences):
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
                                    nt = text_processor.get_ner('en', t['text'])
                                    nt = nt.to_dict()[0][0]
                                    if nt["ner"] != "O" and nt['xpos'] in xpos_types:
                                        temp_ner = nt['text']
                            else:
                                temp_ner += f" {t['text']}"
                        if position == 'E':
                            final.append(temp_ner.strip())

        # return list(set(final))
        return final


if __name__ == "__main__":
    # s3 = TagS3('transcription-engine-data-nonprod-stg')
    count = 0
    text_processor = StanzaNER(['en', 'es', 'ru'])
    neo = Neo("neo4j", "bad_password", text_processor)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_result = {
                executor.submit(neo.process, filename, 1716413530): filename for filename in os.listdir('corpus_files/Raw_data')}
            for future in concurrent.futures.as_completed(future_result):
                try:
                    count += 1
                    print(count)
                    # print(future.result())
                except Exception:
                        raise
    except Exception as err:
        print(err)
