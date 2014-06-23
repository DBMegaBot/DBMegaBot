# -*- coding: utf-8 -*-
from desertbot import DesertBot
from response import IRCResponse
from message import IRCMessage


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
        pass

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        pass
  
    def _loadModule(self, name):
        """
        @type name: unicode
        """
        pass
    
    def _unloadModule(self, name):
        """
        @type name: unicode
        """
        pass
    
    def _loadAllModules(self):
        pass
