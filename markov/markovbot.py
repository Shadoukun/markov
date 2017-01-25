from model import Model
import logger
from commands import Commands
import random
import re
from config import ConfigManager
from twisted.internet import defer, protocol, reactor
from twisted.words.protocols import irc

import logging

logging.basicConfig(level=logging.DEBUG)


class MarkovBot(irc.IRCClient, Commands):

    def __init__(self, factory, model):
        # Inherit commands
        Commands.__init__(self)
        self.factory = factory
        self.config = self.factory.config
        self.nickname = self.config.bot_nick
        self.model = model

        # Error/Info log. not to be confused with message logger
        self.log = logging.getLogger(__name__)
        self.deferred = defer.Deferred()
        self.logger = logger.Logger(self.config.db_host, self.config.db)

    def get_key(self, nick):
        """Returns a string (host-channel-nick) used
          for prefixing key in the model db
          nick: user's nickname
        """
        key = ['irc', self.config.server_address, self.config.channel, nick]
        return '-'.join([k for k in key if k is not None])

    def connection_lost(self, reason):
        self.deferred.errback(reason)

    def signedOn(self):
        # This is called once the server has acknowledged that we sent
        # both NICK and USER.
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        words = msg.split()

        # Check to see if they're sending me a private message
        if channel is self.config.bot_nick:
            msg = "I hope you die."
            self.msg(user, msg)

        if len(words) > self.config.chain_length:
            key = self.get_key(nick=user)
            self.logger.log(key, msg)

        if [msg.startswith(command) for command in self.commands]:
            self.check_command(user, msg)

            regex = '^{n}\S*\W*'.format(n=self.config.bot_nick)
            if re.match(regex, msg) or (
                random.random() < self.config.chattiness
                    ):

                message = self.model.generate_message(msg)

                if message:
                    self.msg(channel, message)
                else:
                    self.msg(channel, 'nope')

    def check_command(self, user, msg):

        if user in self.config.authed_users:
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


class IRCFactory (protocol.ReconnectingClientFactory):

    def __init__(self):
        self.config = ConfigManager()
        self.channel = self.config.channel
        self.nickname = self.config.bot_nick

    def buildProtocol(self, addr):
        model = Model(self.config)
        return MarkovBot(self, model)

    def connect(self):

        host = self.config.server_address
        port = self.config.server_port

        print "Connecting to %s:%s" % (host,  port)
        reactor.connectTCP(host, port, self)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect:", reason
        reactor.stop()

    def run(self):
        reactor.run()


def main():
    factory = IRCFactory()
    factory.connect()
    factory.run()
