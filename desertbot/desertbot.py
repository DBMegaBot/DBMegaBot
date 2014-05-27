from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from message import IRCMessage
from user import IRCUser
from channel import IRCChannel
import yaml


class DesertBot(irc.IRCClient):
    def __init__(self, factory):
        """
        @type factory: DesertBotFactory
        """
        self.nickname = factory.config["nickname"]
        self.username = factory.config["username"]
        self.realname = factory.config["realname"]
        self.commandChar = factory.config["commandChar"]
        for channelName in factory.config["channels"]:
            self.channels[channelName] = IRCChannel(channelName)
        self.admins = factory.config["admins"]
        #assuming, for now, that channels and admins would be in the config as lists

    def signedOn(self):
        for channel in self.channels.keys():
            self.join(channel)

    def nickChanged(self, nick):
        self.nickname = nick

    def modeChanged(self, user, channel, set, modes, args):
        pass

    def irc_TOPIC(self, prefix, params):
        pass

    def irc_RPL_TOPIC(self, prefix, params):
        pass

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = self.getChannel(params[2])
        channelUsers = params[3].strip().split(" ")
        for channelUser in channelUsers:
            rank = ""
            # TODO Parse rank information

            user = self.getUser(channelUser, params[2])
            if not user:
                user = IRCUser("{}!{}@{}".format(channelUser, None, None))

            channel.users[user.nickname] = user
            channel.ranks[user.nickname] = rank

    def privmsg(self, user, channel, msg):
        message = IRCMessage('PRIVMSG', self.getUser(user, channel), self.getChannel(channel), msg)
        pass

    def action(self, user, channel, msg):
        message = IRCMessage('ACTION', self.getUser(user, channel), self.getChannel(channel), msg)
        pass

    def noticed(self, user, channel, msg):
        message = IRCMessage('NOTICE', self.getUser(user, channel), self.getChannel(channel), msg.upper())
        pass

    def irc_JOIN(self, prefix, params):
        message = IRCMessage('JOIN', self.getUser(prefix, params[0]), self.getChannel(params[0]), '')
        pass

    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: ' + u' '.join(params[1:])
        message = IRCMessage('PART', self.getUser(prefix, params[0]), self.getChannel(params[0]), partMessage)
        pass

    def irc_KICK(self, prefix, params):
        kickMessage = u''
        if len(params) > 2:
            kickMessage = u', message: ' + u' '.join(params[2:])
        message = IRCMessage('KICK', self.getUser(prefix, params[0]), self.getChannel(params[0]), kickMessage)
        kickee = params[1]
        pass

    def irc_QUIT(self, prefix, params):
        quitMessage = u''
        if len(params) > 0:
            quitMessage = u', message: ' + u' '.join(params[0])
        for key in self.channels:
            channel = self.channels[key]
            message = IRCMessage('QUIT', self.getUser(prefix, channel), channel, quitMessage)
            pass

    def getChannel(self, channel):
        """
        @type channel: str
        @rtype: IRCChannel
        """
        if channel in self.channels:
            return self.channels[channel]
        return None

    def getUser(self, user, channel):
        """
        @type user: str
        @type channel: str
        @rtype: IRCUser
        """
        if user in self.channels[channel]:
            return self.channels[channel].users[user]
        return None


class DesertBotFactory(protocol.ReconnectingClientFactory):
    protocol = DesertBot

    def __init__(self, server):
        """
        @type server: str
        """
        config = yaml.load("configs/{}.yaml". format(server))
        self.bot = DesertBot(self)
        reactor.connectTCP(config["server"], config["port"], self)

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.bot

    def clientConnectionLost(self, connector, unused_reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass
