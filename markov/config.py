import sys, os
from configparser import SafeConfigParser
import ast


class ConfigManager(object):

    def __init__(self):
        # http://stackoverflow.com/a/4060259
        __location__ = os.path.split(os.getcwd())[0]
        print __location__
        sys.path.append(os.path.abspath(__location__))
        self._config_parser = SafeConfigParser()
        self._config_parser.readfp(open("markov.conf"))

        self._db_host = self._config_parser.get('DB', 'host')
        self._db = self._config_parser.get('DB', 'db')

        self._server_address = self._config_parser.get('IRC', 'host')
        self._server_port = self._config_parser.get('IRC', 'port')
        self._channel = self._config_parser.get('IRC', 'channel')
        self._bot_nick = self._config_parser.get('IRC', 'nickname')

        self._chattiness = self._config_parser.get('markov', 'chattiness')
        self._seed = self._config_parser.get('markov', 'seed')
        self._chain_length = self._config_parser.get('markov', 'chain_length')
        self._authed_users = self._config_parser.get('markov', 'authed_users')
        self._ignored_users = self._config_parser.get('markov', 'ignored_users')

    @property
    def server_address(self):
        return str(self._server_address)

    @server_address.setter
    def server_address(self, value):
        self._server_address = value

    @property
    def server_port(self):
        return int(self._server_port)

    @server_port.setter
    def server_port(self, value):
        self._server_port = value

    @property
    def channel(self):
        return str(self._channel)

    @channel.setter
    def channel(self, value):
        self._channel = value
        self._update_data_path()

    @property
    def bot_nick(self):
        return str(self._bot_nick)

    @bot_nick.setter
    def bot_nick(self, value):
        self._bot_nick = value

    @property
    def data_path(self):
        return self._data_path

    @property
    def db_host(self):
        return str(self._db_host)

    @property
    def db(self):
        return int(self._db)

    @property
    def chattiness(self):
        return float(self._chattiness)

    @chattiness.setter
    def chattiness(self, value):
        self._chattiness = value

    @property
    def seed(self):
        return ast.literal_eval(self._seed)

    @seed.setter
    def seed(self, value):
        self._seed = value

    @property
    def chain_length(self):
        return int(self._chain_length)

    @property
    def authed_users(self):
        return self._authed_users

    @property
    def ignored_users(self):
        return self._ignored_users
