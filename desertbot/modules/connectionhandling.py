# -*- coding: utf-8 -*-
import datetime

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType
from desertbot.config import Config


class ConnectionHandling(Module):
    implements(IPlugin, IModule)

    name = u"connectionhandling"
    triggers = [u"connect", u"quit", u"quitfrom", u"restart", u"shutdown"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS

    def getHelp(self, message):
        helpDict = {
            self.name: u"connect <configfilename> / quit / quitfrom <configfilename> / restart / "
                       u"shutdown - handle bot connections.",
            u"connect": u"connect <configfilename> - connect to the server in the given "
                        u"config file.",
            u"quit": u"quit - quits the bot instance connected to this server.",
            u"quitfrom": u"quitfrom <configfilename> - quits the bot instance connected to the "
                         u"server in the given config file.",
            u"restart": u"restart - restarts every instance of the bot, with any code changes "
                        u"that may have happened since the bot started.",
            u"shutdown": u"shutdown - quit every instance of the bot on every server and end the "
                         u"process.",
        }

        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"connect":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG, u"Connect where?", message.user,
                                   message.replyTo)
            for configFileName in message.parameterList:
                try:
                    if not configFileName.endswith(".yaml"):
                        config = Config("{}.yaml".format(configFileName))
                    else:
                        config = Config(configFileName)
                    if config.loadConfig():
                        message.bot.bothandler.configs[config.configFileName] = config
                        message.bot.bothandler.startBotFactory(config)
                        return IRCResponse(ResponseType.PRIVMSG,
                                           u"Using \"{}\" for new connection...".format(
                                               config.configFileName),
                                           message.user, message.replyTo)
                    else:
                        return IRCResponse(ResponseType.PRIVMSG,
                                           u"\"{}\" was not correct. Aborting.".format(
                                               config.configFileName),
                                           message.user, message.replyTo)
                except Exception as e:
                    log.err("Connecting with \"{}\" failed. ({})".format(configFileName, e))
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"Connecting with \"{}\" failed. ({})".format(
                                           configFileName, e),
                                       message.user, message.replyTo)
        if message.command == u"quit":
            if datetime.datetime.utcnow() > message.bot.startTime + datetime.timedelta(seconds=10):
                message.bot.factory.shouldReconnect = False
                message.bot.bothandler.stopBotFactory(message.bot.config.configFileName, None)
        if message.command == u"quitfrom":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG, u"Quit from where?", message.user,
                                   message.replyTo)
            for configFileName in message.parameterList:
                if not configFileName.endswith(".yaml"):
                    quitFromConfig = "{}.yaml".format(configFileName)
                else:
                    quitFromConfig = configFileName
                if quitFromConfig == message.bot.config.configFileName:
                    return IRCResponse(ResponseType.PRIVMSG, u"Can't quit from here with this!",
                                       message.user, message.replyTo)
                else:
                    quitMessage = u"Killed from \"{}\"".format(message.bot.config["server"])
                    result = message.bot.bothandler.stopBotFactory(quitFromConfig, quitMessage)
                    if result:
                        return IRCResponse(ResponseType.PRIVMSG,
                                           u"Successfully quit from \"{}\".".format(configFileName),
                                           message.user, message.replyTo)
                    else:
                        return IRCResponse(ResponseType.PRIVMSG,
                                           u"I am not on \"{}\"!".format(configFileName),
                                           message.user, message.replyTo)
        if message.command == u"restart":
            if datetime.datetime.utcnow() > message.bot.startTime + datetime.timedelta(seconds=10):
                message.bot.bothandler.restart()
        if message.command == u"shutdown":
            if datetime.datetime.utcnow() > message.bot.startTime + datetime.timedelta(seconds=10):
                message.bot.bothandler.shutdown()


connectionhandling = ConnectionHandling()
