from model import Model
import database
from commands import Commands
import random
import sys
import re
import os
import ConfigParser
from twisted.internet import defer, endpoints, protocol, reactor, task
from twisted.python import log
from twisted.words.protocols import irc

import logging

logging.basicConfig(level=logging.DEBUG)


class MarkovBot(irc.IRCClient, Commands):

    def __init__(self):
        # Inherit commands
        Commands.__init__(self)

        # Error/Info log. not to be confused with message logger
        self.log = logging.getLogger(__name__)
        self.log.info("Initializing...")
        self.parse_config()

        self.r = database.db_connection()
        self.deferred = defer.Deferred()
        self.logger = database.MessageLogger()

        self.log.info("Getting Commands...")

        self.commands = {
                        "!chattiness": self.set_chattiness,
                        "!seed": self.setSeed
                        }

        self.log.info("Generating model...")
        self.modeller = Model(config)

        self.log.info("...Initialized.")

    def parse_config(self):
        """Defines variables from config file"""

        self.log.info("Parsing Config...")
        self.config = get_config(os.getcwd() + "/settings.ini")
        self.__dict__.update([i for s in config.sections() for i in config.items(s)])

    def get_prefix(self, nick):
        """Returns a string (host-channel-nick) used
          for prefixing key in the model db
          nick: user's nickname
        """
        prefix = ['irc', self.host, self.channel, nick]
        return '-'.join([p for p in prefix if p is not None])

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

                message = self.modeller.generate_message(msg)

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

    def _sendMessage(self, msg, target, nick=None):
        if nick:
            msg = '%s, %s' % (nick, msg)
        self.msg(channel, msg)

    def _showError(self, failure):
        return failure.getErrorMessage()

    def command_ping(self, rest):
        return 'Pong.'


def get_config(path):
    """
    Returns the config object
    """

    config = ConfigParser.ConfigParser()
    config.read(path)
    return config


class IRCFactory (protocol.ReconnectingClientFactory):
    config = get_config(os.getcwd() + "/settings.ini")
    channel = config.get("IRC", "channel")
    protocol = MarkovBot
    channels = [channel]


def main(reactor, description):
    endpoint = endpoints.clientFromString(reactor, description)
    factory = IRCFactory()
    d = endpoint.connect(factory)
    d.addCallback(lambda protocol: protocol.deferred)
    return d


if __name__ == '__main__':

    config = get_config(os.getcwd() + "/settings.ini")

    irchost = config.get("IRC", "host")
    ircport = config.get("IRC", "port")

    log.startLogging(sys.stderr)
    hoststring = ''.join(['tcp:', irchost, ':', ircport])
    task.react(main, [hoststring])
