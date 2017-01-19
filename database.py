import string
import walrus
import itertools
import re


def db_connection():
    db = walrus.Walrus(host='192.168.1.4', db=8)
    return db


class MessageLogger:

    def __init__(self):
        self.db = db_connection()

    def get_keys(self, key=None):
        # Returns the object (list) at 'key'
        if key:
            dblist = self.db.Set(key)
        else:
            dblist = self.db.keys()
        return dblist

    def get_text(self, key=None):

        txtlist = []
        keys = [self.get_keys(k) for k in self.db.keys()]

        for s in itertools.chain.from_iterable(keys):
                txtlist.append(s.strip())

        return txtlist

    def _prepare_message(self, message):
        rep = [
            re.compile('http.*\W'),
            re.compile('^markov\S*\W*')
            # need to add more
            ]

        for regex in rep:
            cleaned = re.sub(regex, '', message)

        return cleaned

    def log(self, key, message):
        textk = self.db.Set(key)
        m = string.translate(message.strip(), None, string.punctuation)
        textk.add(self._prepare_message(m))
