import string
import walrus
import itertools
import re


def db_connection(host, db):
    db = walrus.Walrus(host=host, db=db)
    return db


class Logger:

    def __init__(self, config):
        self.config = config
        self.db = db_connection(self.config.db_host, self.config.db)

    def get_keys(self, key=None):
        # Returns the object (list) at 'key'
        if key:
            dblist = self.db.Set(key)
        else:
            dblist = self.db.keys()
        return dblist

    def get_key(self, nick):
        """returns key formatted for db
          nick: user's nickname
        """
        key = ['irc', self.config.server_address, self.config.channel, nick]
        return '-'.join([k for k in key if k is not None])

    def get_text(self, key=None):

        txtlist = []
        keys = [self.get_keys(k) for k in self.db.keys()]

        for s in itertools.chain.from_iterable(keys):
                txtlist.append(s.strip())

        return txtlist

    def _messageCheck(self, message):

        rex = [
            re.compile(r"\<.+\>"),
            re.compile(r'http.*\W'),
            re.compile(r"\[\d\d\:\d\d\:\d\d\]"),
            re.compile(r"((/|\\)(?!\s)[^/ ]*)+/?")
        ]

        for r in rex:
            if re.match(r, message):
                return False
            else:
                return True

    def log(self, nick, message):

        key = self.get_key(nick)

        if self._messageCheck(message):
            textk = self.db.Set(key)
            m = string.translate(message.strip(), None, string.punctuation)
            textk.add(m)
