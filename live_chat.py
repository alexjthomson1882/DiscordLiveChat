#########################################################################################################################################
# LIVE CHAT - DISCORD.PY BOT API                                                                                                        #
# A discord.py bot with a RESTful API that allows applications to integrate live discord chat.                                          #
#########################################################################################################################################

# Discord Live Chat Bot
# Author:  Alex James Thomson (QuackyBoi)
# Website: https://alexthomson.dev
# GitHub:  https://github.com/alexjthomson1882/DiscordLiveChat

# A RESTful API that allows applications to integrate live two way chat with Discord.

# This application and any Discord guilds it integrates with are configured via JSON files in a configuration directory.

#########################################################################################################################################
# TODO                                                                                                                                  #
#########################################################################################################################################

# - Complete LiveChatBot implementation.
# - Create code that initialises the application by looking for configuration files and using them to create bots and server
#   configurations.
# - Create Flask API that integrates with LiveChatBot instances.
# - Create a Stormworks mission script that integrates with the LiveChatBot to test it works.
# - Publish LiveChatBot on GitHub as a public project.
# - Publish LiveChatBot-Stormworks on GitHub as a public project.

#########################################################################################################################################

import os
from os import access, R_OK
from os.path import isfile
import sys

import logging
import logging.handlers

import json

import discord

#########################################################################################################################################
# LOGGING                                                                                                                               #
#########################################################################################################################################

LOG_LEVEL = logging.INFO                        # logging level
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"           # date-time format used in all log files
LOG_FILE_NAME = "server_manager.log"            # server management script log file name
LOG_FILE_ENCODING = "utf-8"                     # encoding used for log files
LOG_FILE_MAX_BYTES = 32 * 1024 * 1024           # maximum number of bytes a single log file can take up
LOG_FILE_BACKUP_COUNT = 5                       # number of log file backups to maintain

logging.basicConfig() # set the root logger to write to stdout

log_formatter = logging.Formatter("[{asctime}] [{levelname}] {name}: {message}", LOG_DATE_FORMAT, style='{')

log_stream_handler = logging.StreamHandler()
log_stream_handler.setLevel(LOG_LEVEL)
log_stream_handler.setFormatter(log_formatter)

log_file_handler = logging.handlers.RotatingFileHandler(
    filename=LOG_FILE_NAME,
    encoding=LOG_FILE_ENCODING,
    maxBytes=LOG_FILE_MAX_BYTES,
    backupCount=LOG_FILE_BACKUP_COUNT
)
log_file_handler.setFormatter(log_formatter)

def configure_logger(logger_name):
    global log_stream_handler
    global log_file_handler
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(log_stream_handler)
    logger.addHandler(log_file_handler)
    return logger

LOGGER = configure_logger("root")
configure_logger("discord")
configure_logger("discord.client")
configure_logger("discord.gateway")
configure_logger("discord.http")

#########################################################################################################################################
# DISCORD BOT                                                                                                                           #
#########################################################################################################################################

# LiveChatBot
# This class manages a discord.Client implementation that handles live chat integrations.
class LiveChatBot(discord.Client):

    # DEFAULT_INTENTS
    # Contains the default fallback intents for the a standard live chat bot. If any intents are not defined within the JSON
    # configuration provided to the bot in it's constructor, their value is obtained from this constant table.
    DEFAULT_INTENTS = {                         # Default Discord bot intents:
        "auto_moderation": False,               # Whether auto-moderation related events are enabled.
        "auto_moderation_configuration": False, # Whether auto-moderation configuration related events are enabled.
        "auto_moderation_execution": False,     # Whether auto-moderation execution related events are enabled.
        "bans": False,                          # Whether guild ban related events are enabled.
        "dm_messages": False,                   # Whether dm message related events are enabled.
        "dm_reactions": False,                  # Whether dm reaction related events are enabled.
        "dm_typing": False,                     # Whether dm typing related events are enabled.
#       "emojis": False,                        # Alias of 'emojis_and_stickers'. This was changed in version 2.0 of Discord.py. 
        "emojis_and_stickers": False,           # Whether guild emoji and sticker related events and functions are enabled.
        "guild_messages": True,                 # Whether guild message related events are enabled. This is required for the live chat
                                                # bot to recognize when a message is sent into a channel.
        "guild_reactions": False,               # Whether guild reaction related events are enabled.
        "guild_scheduled_events": False,        # Whether guild scheduled events related events are enabled.
        "guild_typing": False,                  # Whether guild typing related events are enabled.
        "guilds": True,                         # Whether guild related events are enabled. This is required for the bot to recognize if
                                                # the live chat channel has been deleted.
        "integrations": False,                  # Whether guild integration related events are enabled.
        "invites": False,                       # Whether guild invite related events are enabled.
        "members": True,                        # Whether guild member related events and member related functions are enabled. This is
                                                # required to find member nicknames etc.
        "message_content": True,                # Whether message content, attachments, embeds and components will be available in
                                                # messages which do not meet the following criteria:
                                                # * The message was sent by the client.
                                                # * The message was sent in direct messages.
                                                # * The message mentions the client.
#       "messages": True,                       # Whether message related events and message functions are enabled. This is a shortcut
                                                # for both 'guild_messages' and 'dm_messages'.
        "presences": False,                     # Whether guild presence related events and guild member presence functions are enabled.
#       "reactions": True,                      # Shortcut for both 'guild_reactions' and 'dm_reactions'.
#       "typing": True,                         # Shortcut for both 'guild_typing' and 'dm_typing'.
        "voice_states": False,                  # Whether guild voice related states are enabled.
        "webhooks": True                        # Whether guild webhook related events are enabled. This is required for the live chat
                                                # bot to manage webhooks.
    }

    # __init__
    # Constructs a LiveChatBot instance from a JSON configuration object.
    def __init__(self, configuration):
        if configuration == None:
            raise ValueError("configuration is null.")
        # Get bot API auth token:
        auth = configuration.get("auth", "")
        if auth == None or auth == "":
            raise ValueError("No API authentication token was provided in the bot configuration.")
        # Get bot name and display name:
        self.name = configuration.get("name", "live_chat")
        self.display_name = configuration.get("display_name", "Live Chat")
        # Get bot intents and initialise super class:
        intents = self.build_intents(configuration.get("intents", LiveChatBot.DEFAULT_INTENTS))
        super().__init__(intents = intents)
        LOGGER.info(f"[LiveChatBot] ({self.name}) instance created.")

    # build_intents:
    # Builds a discord.Intents object based off of the provided configuration.
    def build_intents(self, configuration):
        if configuration == None:
            raise ValueError("configuration is null.")
        intents = discord.Intents()
        intents.auto_moderation                 = self.get_intent(configuration, "auto_moderation")
        intents.auto_moderation_configuration   = self.get_intent(configuration, "auto_moderation_configuration")
        intents.auto_moderation_execution       = self.get_intent(configuration, "auto_moderation_execution")
        intents.bans                            = self.get_intent(configuration, "bans")
        intents.dm_messages                     = self.get_intent(configuration, "dm_messages")
        intents.dm_reactions                    = self.get_intent(configuration, "dm_reactions")
        intents.dm_typing                       = self.get_intent(configuration, "dm_typing")
        intents.emojis_and_stickers             = self.get_intent(configuration, "emojis_and_stickers")
        intents.guild_messages                  = self.get_intent(configuration, "guild_messages")
        intents.guild_reactions                 = self.get_intent(configuration, "guild_reactions")
        intents.guild_scheduled_events          = self.get_intent(configuration, "guild_scheduled_events")
        intents.guild_typing                    = self.get_intent(configuration, "guild_typing")
        intents.guilds                          = self.get_intent(configuration, "guilds")
        intents.integrations                    = self.get_intent(configuration, "integrations")
        intents.invites                         = self.get_intent(configuration, "invites")
        intents.members                         = self.get_intent(configuration, "members")
        intents.message_content                 = self.get_intent(configuration, "message_content")
        intents.presences                       = self.get_intent(configuration, "presences")
        intents.voice_states                    = self.get_intent(configuration, "voice_states")
        intents.webhooks                        = self.get_intent(configuration, "webhooks")
    
    # get_intent
    # Gets a single intent from a JSON configuration object. If the configuration entry does not exist for the intent, it's value is
    # obtained from the DEFAULT_INTENTS
    def get_intent(self, configuration, intent_name):
        if configuration == None:
            raise ValueError("configuration is null.")
        if intent_name == None:
            raise ValueError("intent_name is null.")
        intent = configuration.get(intent_name, LiveChatBot.DEFAULT_INTENTS[intent_name])
        LOGGER.info(f"[LiveChatBot] ({self.name}) intents.{intent_name} = `{intent}`.")
        return intent

#########################################################################################################################################
# DISCORD SERVER OBJECT                                                                                                                 #
#########################################################################################################################################
# The Discord server object contains configuration information about a Discord server that uses one of the Discord bots defined in this
# program.

# TODO:
# - Create Discord server object which can be initialised from a JSON configuration file based off of the requirements & planning
#   documentation.

#########################################################################################################################################
# DISCORD BOT MANAGER                                                                                                                   #
#########################################################################################################################################

class DiscordBotManager:

    # __init__:
    # Constructs a DiscordBotManager instance from a JSON configuration file. The JSON file is read and each Discord bot defined within
    # the file is created and assigned to this instance to manage as a LiveChatBot instance.
    def __init__(self, configuration_path):
        # Validate configuration_path provided:
        if configuration_path == None:
            raise ValueError("configuration_path is null.")
        if not isfile(configuration_path):
            raise IOError("configuration_path is not a file.")
        if not access(configuration_path, R_OK):
            raise IOError("configuration_path is not readable.")
        # Read JSON file:
        file = open(configuration_path, "r")
        json_data = json.load(file)
        file.close()
        # Read address, port, and bots array:
        self.listen_address = json_data.get("address", "0.0.0.0")
        self.listen_port    = json_data.get("port", 8080)
        # Read bots array:
        bots_data = json_data.get("bots", [ ])
        self.bots = []
        # Iterate bots array:
        if bots_data != None and len(bots_data) > 0:
            for bot in bots_data:
                self.bots.append(LiveChatBot(bot))
        # Report total number of bots:
        LOGGER.info(f"[DiscordBotManager] {len(self.bots)} LiveChatBot instances created.")

# Read arguments passed into program:
arguments = sys.argv[1:]
arguments_count = len(arguments)
# Read configuration directory path (expected 1st argument):
if arguments_count >= 1:
    configuration_directory_path = arguments[0]
else:
    configuration_directory_path = os.path.realpath(".")
configuration_directory_path = os.path.join(configuration_directory_path, "")
# Create DiscordBotManager instance:
DISCORD_CONFIGURATION_PATH = os.path.join(configuration_directory_path, "configuration.json")
DISCORD_BOT_MANAGER = DiscordBotManager(DISCORD_CONFIGURATION_PATH)