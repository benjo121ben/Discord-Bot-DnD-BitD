from Character import *
from os import linesep as endl


class Game:

    def __init__(self, game_name, player_username):
        self.game_name = game_name
        self.player_list: list[str] = []
        self.character_list: list[Character] = []
        self.player_list.append(player_username)

    def is_authorized(self, command_user) -> bool:
        if self.player_list.count(command_user) != 0:
            return True
        else:
            raise Exception(command_user + " is not authorized to edit this Game: " + self.game_name)

    def is_player(self, command_user) -> bool:
        return self.player_list.count(command_user) != 0

    def add_player(self, command_user, player_username) -> str:
        if self.is_authorized(command_user):
            if self.is_player(player_username):
                raise Exception("This player has already joined game: " + self.game_name)
            self.player_list.append(player_username)
            return "Player " + player_username + " added to Game."

    def remove_player(self, command_user, player_username) -> str:
        if self.is_authorized(command_user):
            if not self.is_player(player_username):
                raise Exception("Player" + player_username + " is not part of game: " + self.game_name)
            self.player_list.remove(player_username)
            return "Player " + player_username + " removed from Game."

    def add_character(self, command_user, player_name, char_name) -> str:
        if self.is_authorized(command_user):
            self.character_list.append(Character(player_name, char_name))
            return "Character " + char_name + " added to Game."

    def remove_character(self, command_user, char_name) -> str:
        if self.is_authorized(command_user):
            for char in self.character_list:
                if char.name == char_name:
                    self.character_list.remove(char)
                    return "Character " + char_name + " removed from Game."
            return "Character " + char_name + " does not exist in this game"

    def __str__(self):
        ret_str = ""
        ret_str += "Name: " + self.game_name + endl + endl + \
                   "Players: " + endl
        for player in self.player_list:
            ret_str += str(player) + endl
        ret_str += endl + "Characters: " + endl
        for char in self.character_list:
            ret_str += str(char) + endl
        return ret_str


