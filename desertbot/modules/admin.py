# -*- coding: utf-8 -*-
import json
import os
import re
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Admin(Module):
    implements(IPlugin, IModule)

    name = u"admin"
    triggers = [u"admin", u"unadmin", u"admins"]
    moduleType = ModuleType.PASSIVE
    accessLevel = AccessLevel.ADMINS
    modulePriority = -50  # Very high priority, should be higher than ignore but lower than passive logging.

    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"admin": u"admin <user> - adds the specified userstring to the admins list.",
            u"unadmin": u"unadmin <user> - removes the specified userstring from the admins list.",
            u"admins": u"admins - gives you a list of current admins.",
        }
        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"admin":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"Admin who?",
                                   message.user, message.replyTo)
            else:
                if message.parameterList[0] not in self.admins:
                    self.admins.append(message.parameterList[0])
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"Added \"{}\" to the admin list!".format(
                                           message.parameterList[0]),
                                       message.user, message.replyTo)
                else:
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"That user is already an admin!",
                                       message.user, message.replyTo)
        elif message.command == u"unadmin":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"Un-admin who?",
                                   message.user, message.replyTo)
            else:
                if message.parameterList[0] in self.admins:
                    self.admins.remove(message.parameterList[0])
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"Removed \"{}\" from the admin list.".format(
                                           message.parameterList[0]),
                                       message.user, message.replyTo)
                else:
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"That user is not on the admin list!",
                                       message.user, message.replyTo)
        elif message.command == u"admins":
            return IRCResponse(ResponseType.PRIVMSG,
                               u"Current admins: {}".format(u", ".join(self.admins)),
                               message.user, message.replyTo)
        else:
            if not self._allowedToUse(message):
                response = IRCResponse(ResponseType.PRIVMSG, u"Only my admins can use \"{}\"!".format(message.command), message.user, message.replyTo)
                message.clear()
                return response

    def onModuleLoaded(self):
        configFileName = self.bot.factory.config.configFileName[:-5]
        if os.path.exists(os.path.join("data", configFileName, "admins.json")):
            with open(os.path.join("data", configFileName, "admins.json")) as jsonFile:
                admins = json.load(jsonFile)
            if len(admins) != 0:
                self.admins = admins
                log.msg("Loaded {} admins from admins file for config \"{}\".".format(len(admins),
                                                                                      configFileName))
            else:
                log.msg("Admins file for config \"{}\" is empty.".format(configFileName))
                self.admins = []
        else:
            log.err("Admins file not found for config \"{}\"!".format(configFileName))
            self.admins = []

    def onModuleUnloaded(self):
        configFileName = self.bot.factory.config.configFileName[:-5]
        if not os.path.exists(os.path.join("data", configFileName, "admins.json")):
            os.makedirs(os.path.join("data", configFileName))
        with open(os.path.join("data", configFileName, "admins.json"), "w") as jsonFile:
            json.dump(self.admins, jsonFile)

    def _allowedToUse(self, message):
        if len(self.admins) == 0:
            return True
        for moduleName, module in self.bot.moduleHandler.loadedModules.iteritems():
            if message.command in module.triggers and module.accessLevel is AccessLevel.ADMINS:
                for adminRegex in self.admins:
                    if re.match(adminRegex, message.user.getUserString()):
                        return True
                return False

admin = Admin()
