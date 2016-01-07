import redis
import string
from walrus import *
import walrus
import itertools
import string

def db_connection():
    db = walrus.Walrus(host='192.168.1.4', db=8)
    return db


# class MessageLogger:
#     """
#     An independent logger class (because separation of application
#     and protocol logic is a good thing).
#     """
#     def __init__(self, List):
#         self.db = db_connection()
#         self.List = List
#
#     def log(self, key, message):
#         """Write a message to Redis."""
#         # removes special characters from message and logs it to the db
#         # where the message is the value of key.
#         message = message.translate(None, string.punctuation)
#
#         self.List.append(message)


class MessageLogger:
    db = db_connection()

    def get_key(self, key):
        # Returns the object (list) at 'key'
        dblist = self.db.Set(key)
        return dblist

    def get_keys(self):
        # returns all keys
        keys = self.db.keys()
        return keys

    def get_text(self, key=None):
        if not key:
            # keylist = [k for k in self.db.keys()]
            txtlist = []
            keys = [self.get_key(k) for k in self.db.keys()]
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
