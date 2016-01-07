import markovify
import re
import nltk.data, nltk.tag
from nltk.tag.perceptron import PerceptronTagger

tagger = PerceptronTagger()
MAX_OVERLAP_RATIO = 0.5
MAX_OVERLAP_TOTAL = 10
DEFAULT_TRIES = 500

class MarkovEase(markovify.Text):
    """
    Overrides markovify.Text. accepts all the same args.
    input_text: A string.
    state_size: An integer, indicating the number of words in the model's state.
    chain: A trained markovify.Chain instance for this text, if pre-processed.

    """

    def test_sentence_input(self, sentence):
        # Add sentence tests, or not
        return True

    def _prepare_text(self, text):
        # parses text. Remove/replace special characters
        text = text.strip()
        if not text.endswith((".", "?", "!")):
            text += "."

        return text

    def sentence_split(self, text):
        # split everything up by newlines, prepare them, and join back together
        return re.split(r"\s*\n\s*", text)

    def word_split(self, sentence):
        global tagger
        words = re.split(self.word_split_pattern, sentence)
        words = ["::".join(tag) for tag in tagger.tag(words)]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence
