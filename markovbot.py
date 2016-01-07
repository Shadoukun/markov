import random
import sys
import string
import re
from model import *
import database

from twisted.internet import defer, endpoints, protocol, reactor, task
from twisted.python import log
from twisted.words.protocols import irc


class MarkovBot(irc.IRCClient):

    host = '--host--'
    channel = '#lobby'
    port = '6667'
    nickname = 'markov'
    chattiness = 0.1
    chain_length = 2

    def __init__(self):
        self.r = database.db_connection()
        self.deferred = defer.Deferred()
        self.logger = database.MessageLogger()

    def get_prefix(self, nick):
        # Returns string made up of IRC host-channel-nick, for sorting logs
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

        text = self.logger.get_text()
        model = MarkovEase("\n".join(text), state_size=2)
        return model

    def generate_message(self, message):
        # Takes a seed message (if one) and generates message
        model = self.get_model(prefix='*')
        seed = self.seed(message)

        try:
            gen_message = model.make_sentence(init_state=seed)
        except KeyError:
            gen_message = model.make_sentence()

        return gen_message

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

            if re.search('^markov\S*\W*', msg) or (
                random.random() < self.chattiness
                    ):

                    message = self.generate_message(msg)

                    if message:
                        self.msg(channel, message)
                    else:
                        self.msg(channel, 'nope')

    def _sendMessage(self, msg, target, nick=None):
        if nick:
            msg = '%s, %s' % (nick, msg)
        self.msg(channel, msg)

    def _showError(self, failure):
        return failure.getErrorMessage()

    def command_ping(self, rest):
        return 'Pong.'


class IRCFactory (protocol.ReconnectingClientFactory):
    protocol = MarkovBot
    channels = ['#lobby']


def main(reactor, description):
    endpoint = endpoints.clientFromString(reactor, description)
    factory = IRCFactory()
    d = endpoint.connect(factory)
    d.addCallback(lambda protocol: protocol.deferred)
    return d

if __name__ == '__main__':
    host = MarkovBot.host
    port = MarkovBot.port
    log.startLogging(sys.stderr)
    hoststring = ''.join(['tcp:', MarkovBot.host, ':', MarkovBot.port])
    task.react(main, [hoststring])
