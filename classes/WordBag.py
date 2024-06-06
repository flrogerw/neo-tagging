import re


class WordBag:
    @staticmethod
    def get_weight(corpus):
        bag_of_words = {}
        org_corpus = corpus
        for i, name in enumerate(corpus):
            corpus[i] = re.sub(r'[^a-zA-Z0-9\s]', '', corpus[i]).strip().lower()
            name = corpus[i]
            corpus[i] = corpus[i].replace(' ', '_').lower()

            if corpus[i] in bag_of_words:
                bag_of_words[corpus[i]]['count'] += 1
            else:
                bag_of_words[corpus[i]] = {}
                bag_of_words[corpus[i]]['count'] = 1
                bag_of_words[corpus[i]]['name'] = name
        words_freq = [(word, bag_of_words[word]['name'], (bag_of_words[word]['count'] / len(org_corpus)) * 10) for word in list(set(bag_of_words.keys()))]
        return words_freq[:None]
