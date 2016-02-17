from model import *
import random
import sys
import string
import re
import database
import ConfigParser
from configobj import ConfigObj
from twisted.internet import defer, endpoints, protocol, reactor, task
from twisted.python import log
from twisted.words.protocols import irc
import threading
import time

import thread
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

class MarkovBot(irc.IRCClient):

    def __init__(self):
        # Error/Info log. not to be confused with message logger
        self.log = logging.getLogger(__name__)

        self.log.info("Initializing...")

        self.r = database.db_connection()
        self.parse_config()
        self.deferred = defer.Deferred()
        self.logger = database.MessageLogger()

        self.log.info("Getting Commands...")
        self.commands = {"!chattiness": self.set_chattiness}

        self.log.info("Generating model...")
        self.get_model()

        self.log.info("...Initialized.")


    def parse_config(self):
        """Defines variables from config file"""

        self.log.info("Parsing Config...")
        config = ConfigObj('settings.ini')

        self.host = config['IRC']["host"]
        self.port = config['IRC']["port"]
        self.nickname = config['IRC']['nickname']
        self.channel = config['IRC']['channel']

        self.chattiness = float(config['markov']['chattiness'])
        self.chain_length = int(config['markov']['chain_length'])
        self.authed_users = config['permissions']['authed_users']


    def get_prefix(self, nick):
        """Returns a string (host-channel-nick) used
          for prefixing key in the model db

          nick: user's nickname
        """

        prefix = ['irc', self.host, self.channel, nick]
        return '-'.join([p for p in prefix if p is not None])

    def seed(self, msg):
        msg = self.logger._prepare_message(msg)
        words = msg.split()
        seedlist = []
        for i in range(len(words) - self.chain_length):
                seedlist.append(words[i:i + self.chain_length])

        seed = random.choice(seedlist)

        return tuple(seed)

    def get_model(self, prefix=None):
        # pulls values from s-keys and generates MarkovEase model
        self.log.debug("Getting model text...")
        text = self.logger.get_text()

        self.log.debug("Generating model...")
        self.model = MarkovEase("\n".join(text), state_size=2)
        self.log.debug("Generated model successfully.")
        self.log.debug("[MODEL ID]" + str(id(self.model)))
        self.log.debug("Spawning model timer...")
        thread = threading.Timer(120, self.get_model)
        thread.daemon = True
        thread.start()
        self.log.debug("...Thread spawned.")

    def generate_message(self, message):
        print "-generate_message-"
        # Takes a seed message (if one) and generates message
        n = 0
        best_len = 0
        best_msg = ''
        seed = self.seed(message)
        while n < 20:
            try:
                print seed
                gen_message = self.model.make_short_sentence(140, init_state=seed)

                gen_msg = gen_message

                if len(gen_msg) > best_msg:
                    best_len = len(gen_msg)
                    best_msg = gen_msg

                n = n + 1

            except KeyError:
                n = n + 1
                continue

        if best_len > 0:
            return best_msg
        else:
            return self.model.make_short_sentence(140)

# The end of the redis/markov text generation orgy.
    # All IRC methods below

    def connection_lost(self, reason):
        self.deferred.errback(reason)

    def signedOn(self):
        # This is called once the server has acknowledged that we sent
        # both NICK and USER.
        for channel in self.factory.channels:
            self.join(channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        words = msg.split()

        # seed = []

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "I hope you die."
            self.msg(user, msg)

        if len(words) > self.chain_length:
            prefix = self.get_prefix(nick=user)
            self.logger.log(prefix, msg)

        if [msg.startswith(command) for command in self.commands]:
            self.check_command(user, msg)

            if re.search('^markov\S*\W*', msg) or (
                random.random() < self.chattiness
                    ):

                message = self.generate_message(msg)

                if message:
                    self.msg(channel, message)
                else:
                    self.msg(channel, 'nope')

    def check_command(self, user, msg):

        if user in self.authed_users:
            for key, command in self.commands.iteritems():
                if msg.startswith(key):
                    command(msg)
                else:
                    pass

    def set_chattiness(self, msg):
        command, value = msg.split()
        oldvalue = self.chattiness

        config['markov']['chattiness'] = value
        self.chattiness = float(value)

        response = 'Chattiness changed from {ov} to {nv} '.format(ov=oldvalue, nv=value)
        self.msg(self.channel, response)

    def _sendMessage(self, msg, target, nick=None):
        if nick:
            msg = '%s, %s' % (nick, msg)
        self.msg(channel, msg)

    def _showError(self, failure):
        return failure.getErrorMessage()

    def command_ping(self, rest):
        return 'Pong.'


class IRCFactory (protocol.ReconnectingClientFactory):
    config = ConfigObj('settings.ini')
    channel = config["IRC"]["channel"]
    protocol = MarkovBot
    channels = [channel]


def main(reactor, description):
    endpoint = endpoints.clientFromString(reactor, description)
    factory = IRCFactory()
    d = endpoint.connect(factory)
    d.addCallback(lambda protocol: protocol.deferred)
    return d

if __name__ == '__main__':

    config = ConfigObj('settings.ini')

    irchost = config["IRC"]["host"]
    ircport = config["IRC"]["port"]

    log.startLogging(sys.stderr)
    hoststring = ''.join(['tcp:', irchost, ':', ircport])
    task.react(main, [hoststring])
