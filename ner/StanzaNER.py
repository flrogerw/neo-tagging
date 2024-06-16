import json  # Import the json module for working with JSON data
import torch  # Import torch for working with neural networks
import stanza  # Import stanza for natural language processing
from stanza.pipeline.multilingual import Pipeline  # Import Pipeline class from stanza for multilingual NLP
from stanza.pipeline.core import DownloadMethod  # Import DownloadMethod from stanza for downloading resources

# Download multilingual models from stanza
stanza.download(lang="multilingual")
# Open the bad word list JSON file
words = open('ner/bad_word_list.json')
# Load the bad words list from JSON
bad_words_list = json.load(words)


# Class for named entity recognition using stanza
class StanzaNER(Pipeline):
    def __init__(self, languages, use_gpu=False, *args, **kwargs):
        """
        Initialize the StanzaNER class.
        :param languages: List of languages for which NER is performed
        """
        # Initialize text processors for each language
        self.text_processors = {}
        for language in languages:
            # Initialize a stanza pipeline for each language
            self.text_processors[language] = Pipeline(download_method=DownloadMethod.REUSE_RESOURCES, lang=language,
                                                      processors='tokenize,ner', use_gpu=use_gpu)

        # Initialize the Stanza pipeline for language identification
        super().__init__(download_method=DownloadMethod.REUSE_RESOURCES,
                         lang="en",  use_gpu=use_gpu, langid_clean_text=True)

    @staticmethod
    def get_language(nlp):
        """
        Get the language of the input text processed by stanza.
        :param nlp: Stanza NLP object
        :return: Language of the input text
        """
        try:
            return nlp.lang
        except Exception:
            raise

    @staticmethod
    def remove_stopwords(sents):
        """
        Remove stopwords from sentences.
        :param sents: Sentences
        :return: Sentences with stopwords removed
        """
        try:
            sentences = []
            for sent in sents:
                for word in sent.words:
                    # Filter out stopwords based on Universal POS tags
                    if word.upos not in ['PUNCT', 'PRON', 'ADP', 'CCONJ', 'DET', 'PART', 'SYM']:
                        sentences.append(word)
            return sentences
        except Exception:
            raise

    def get_ner(self, language, text_str):
        """
        Get named entities in the input text.
        :param language: Language of the text
        :param text_str: Input text
        :return: Named entities in the text
        """
        ner = self.text_processors[language](text_str)
        return ner

    @staticmethod
    def get_words(nlp):
        """
        Get words from processed text.
        :param nlp: Stanza NLP object
        :return: Words from the processed text
        """
        sentences = []
        for sent in nlp.sentences:
            for word in sent.words:
                if word.upos not in ['PUNCT', 'PART', 'SYM']:
                    sentences.append(word)
        return sentences

    def get_lemma(self, text_str, language):
        """
        Get lemmatized text.
        :param text_str: Input text
        :param language: Language of the text
        :return: Lemmatized text
        """
        try:
            nlp = self.text_processors[language](text_str)
            no_stopwords = self.remove_stopwords(nlp.sentences)
            return ' '.join([word.lemma.lower() for word in no_stopwords])
        except Exception:
            raise

    @staticmethod
    def get_vector(text, model):
        """
        Get vector representation of text using a pre-trained model.
        :param text: Input text
        :param model: Pre-trained model
        :return: Vector representation of the text
        """
        try:
            with torch.no_grad():
                vector = model.encode(text)
            return vector
        except Exception:
            raise

    @staticmethod
    def profanity_check(text, fields_to_check, profanity):
        """
        Check for profanity in the input text.
        :param text: Input text
        :param fields_to_check: Fields to check for profanity
        :param profanity: Profanity checker object
        :return: True if profanity is detected, False otherwise
        """
        bad_words = bad_words_list[text['language']]
        profanity_check_str = ' '.join(list(map(lambda a, r=text: r[a], fields_to_check)))
        profanity.load_censor_words(bad_words)
        return profanity.contains_profanity(profanity_check_str)
