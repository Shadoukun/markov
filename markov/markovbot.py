import re
import logging
import random
import sys

from twisted.internet import defer, protocol, reactor
from twisted.words.protocols import irc

from model import Model
from logger import Logger
from commands import Commands
from config import ConfigManager


logging.basicConfig(level=logging.INFO)


class MarkovBot(irc.IRCClient, Commands):

    def __init__(self, config, model, logger):
        # Inherit commands
        Commands.__init__(self)

        self.config = config
        self.nickname = self.config.bot_nick
        self.model = model

        # Error/Info log. not to be confused with message logger
        self.log = logging.getLogger(__name__)
        self.deferred = defer.Deferred()
        self.logger = logger

    def signedOn(self):
        # This is called once the server has acknowledged that we sent
        # both NICK and USER.
        self.join(self.config.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        # Check to see if they're sending me a private message
        if channel is self.nickname:
            msg = "I hope you die."
            self.msg(user, msg)
            return

        if len(msg.split()) > self.config.chain_length:
            self.logger.log(user, msg)

        if [msg.startswith(command) for command in self.commands]:
            self.check_command(user, msg)

        regex = '^{n}\S*\W*'.format(n=self.nickname)

        if re.match(regex, msg) or (
            random.random() < self.config.chattiness
                    ):
                    msg = re.sub(regex, '', msg)
                    seed = self.config.seed
                    message = self.model.generate_message(msg, seed)

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

    def _showError(self, failure):
        return failure.getErrorMessage()

    def command_ping(self, rest):
        return 'Pong.'


class IRCFactory (protocol.ReconnectingClientFactory):

    def __init__(self):
        self.config = ConfigManager()
        self.channel = self.config.channel
        self.nickname = self.config.bot_nick
        self.logger = Logger(self.config)

    def buildProtocol(self, addr):
        model = Model(self.logger)
        return MarkovBot(self.config, model, self.logger)

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

    try:
        factory.connect()
        factory.run()

    except KeyboardInterrupt:
        factory.reactor.stop()
        sys.exit()
