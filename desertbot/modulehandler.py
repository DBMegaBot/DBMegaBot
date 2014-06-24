# -*- coding: utf-8 -*-
from twisted.plugin import getPlugins
from desertbot.moduleinterface import IModule, ModuleType, ModulePriority, AccessLevel
from desertbot.desertbot import DesertBot
from desertbot.response import IRCResponse, ReponseType
from desertbot.message import IRCMessage
import desertbot.modules
import re, operator

class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: DesertBot
        """
        self.bot = bot
        self.loadedModules = {}
    
    def sendResponse(self, response):
        """
        @type response: IRCResponse
        """
        responses = []
        
        if hasattr(response, "__iter__"):
            for r in response:
                if r is None or r.response is None or r.response == "":
                    continue
                responses.append(r)
        elif response is not None and response.response is not None and response.response != "":
            responses.append(response)
            
        for response in responses:
            try:
                if response.responseType == ResponseType.PRIVMSG:
                    self.bot.msg(response.target, response.response) #response should be unicode here
                elif response.responseType == ResponseType.ACTION:
                    self.bot.describe(response.target, response.response)
                elif response.responseType == ResponseType.NOTICE:
                    self.bot.notice(response.target, response.response)
                elif response.responseType == ResponseType.RAW:
                    self.bot.sendLine(response.response)
            except Exception:
                pass #TODO Exception handling
                    

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        for module in sorted(self.loadedModules.values(), key=operator.attrgetter("modulePriority")):
            try:
                if self._shouldExecute(module, message):
                    #TODO Threading for the modules?
                    response = module.execute(message)
                    self.sendResponse(response)
            except Exception:
                pass #TODO Exception logging

    def _shouldExecute(self, module, message):
        """
        @type message: IRCMessage
        """
        if message.messageType in module.messageTypes:
            if module.moduleType == ModuleType.PASSIVE:
                return True
            elif message.user.nickname == self.bot.nickname:
                return False
            elif module.moduleType == ModuleType.ACTIVE:
                for trigger in module.triggers:
                    match = re.search(".*{}.*".format(trigger), message.messageText, re.IGNORECASE)
                    if match:
                        return True
                return False
            elif module.moduleType == ModuleType.COMMAND:
                for trigger in module.triggers:
                    match = re.search("^{}({})($| .*)".format(self.bot.commandChar, trigger), message.messageText, re.IGNORECASE)
                    if match:
                        return True
                return False
            elif module.moduleType == ModuleType.POSTPROCESS:
                return True
            elif module.moduleType == ModuleType.UTILITY:
                return True

    def _checkCommandAuthorization(self, module, message):
        """
        @type message: IRCMessage
        """
        if module.accessLevel == AccessLevel.ANYONE:
            return True

        if module.accessLevel == AccessLevel.ADMINS:
            for adminRegex in self.bot.admins:
                if re.match(adminRegex, message.user.getUserString()):
                    return True
            return False

    def loadModule(self, name):
        """
        @type name: unicode
        """
        if name.lower() not in self.loadedModules:
            moduleReload = False
            # not a reload, log something for this? A boolean for later return perhaps?
        else:
            moduleReload = True
            # totes a reload. Log/boolean?
        for module in getPlugins(IModule, desertbot.modules):
            if module.name == name.lower():
                self.loadedModules[module.name] = module
                self.loadedModules[module.name].onModuleLoaded()
                if moduleReload:
                    return (True, "{} reloaded!".format(module.name))
                else:
                    return (True, "{} loaded!".format(module.name))
                #TODO Return stuff and also log
        return (False, "No module named '{}' could be found!".format(name))
        #if we get here, there is no such module. Throw exception?

    def unloadModule(self, name):
        """
        @type name: unicode
        """
        if name.lower() in self.loadedModules:
            self.loadedModules[name.lower()].onModuleUnloaded()
            del self.loadedModules[name.lower()]
            return (True, "{} unloaded!".format(name))
            #TODO Return stuff and log
        return (False, "No module named '{}' is loaded!".format(name))
    
    def loadAllModules(self):
        for module in getPlugins(IModule, desertbot.modules):
            self.loadedModules[module.name.lower()] = module
            self.loadedModules[module.name.lower()].onModuleLoaded()
            #TODO Return stuff and log
        return (True, "All modules successfully loaded!")
