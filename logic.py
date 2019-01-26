import random
import math
import re


def chk_is_whitespace(name) -> bool:
    test = re.search(r'\,[ \t]+\,|\,[ \t]+$', name)
    if test is None:
        output = False
    else:
        output = True
    return output


class Player:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.score = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Game:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Match:
    NOT_PLAYED_YET = 0
    MAIN_PLAYER_WON = 1
    OPPONENTS_WON = 2

    def __init__(self, id: int, player: Player, game: Game, opponents: list, prize_score: int):
        self.id = id
        self.player = player
        self.opponents = opponents
        self.prize_score = prize_score
        self.game = game
        self.state = self.NOT_PLAYED_YET

    def __str__(self):
        opponents = str(self.opponents).strip("[]").replace(", ", "+")
        players = f'{self.player} vs {opponents}'

        if self.state == self.NOT_PLAYED_YET:
            winner = 'Not played yet'
        elif self.state == self.MAIN_PLAYER_WON:
            winner = self.player.name
        else:
            winner = opponents

        return f'#{self.id}: [Players: {players}] [Game: {self.game}] [Score: {self.prize_score}] [Winner: {winner}]'


class TournamentController:
    SCORE_PICKED_GAME = 1
    SCORE_RANDOM_GAME = 3
    SCORE_PICKED_OPPONENT = 1
    SCORE_RANDOM_OPPONENT = 3

    def __init__(self, player_names: list, game_names: list):

        self.games = [Game(id + 1, name) for (id, name) in enumerate(game_names)]
        self.players = [Player(id + 1, name) for (id, name) in enumerate(player_names)]
        self.matches = []

    def get_game_by_id(self, game_id: int) -> Game:
        return next((game for game in self.games if game.id == game_id), None)

    def get_player_by_id(self, player_id: int) -> Player:
        return next((player for player in self.players if player.id == player_id), None)

    def get_match_by_id(self, match_id: int) -> Match:
        return next((match for match in self.matches if match.id == match_id), None)

    def get_matches_by_player_id(self, player_id: int, only_main_player: bool = False) -> list:
        player = self.get_player_by_id(player_id)

        if only_main_player:
            return [match for match in self.matches if player == match.player]
        else:
            return [match for match in self.matches if (player == match.player or player in match.opponents)]

    def get_players_by_match_id(self, match_id: int) -> list:
        match = next((match for match in self.matches if match.id == match_id), None)
        return [match.player] + match.opponents

    def randomize_game(self) -> Game:
        return random.choice(self.games)

    def randomize_player(self, excluded_ids: list = None) -> Player:
        if excluded_ids is None:
            excluded_ids = []

        return random.choice([player for player in self.players if player.id not in excluded_ids])

    def add_match(self, player_id: int, opponent_ids: list, game_id: int = None):

        match_id = len(self.matches) + 1
        player = self.get_player_by_id(player_id)
        prize_score = 0
        opponents = []
        excluded_opponent_ids = [player_id]

        for opponent_id in opponent_ids:
            if opponent_id:
                opponent = self.get_player_by_id(opponent_id)
                prize_score += self.SCORE_PICKED_OPPONENT
            else:
                opponent = self.randomize_player(excluded_ids=excluded_opponent_ids)
                prize_score += self.SCORE_RANDOM_OPPONENT

            excluded_opponent_ids.append(opponent.id)
            opponents.append(opponent)

        if game_id:
            game = self.get_game_by_id(game_id)
            prize_score += self.SCORE_PICKED_GAME
        else:
            game = self.randomize_game()
            prize_score += self.SCORE_RANDOM_GAME

        self.matches.append(Match(match_id, player, game, opponents, prize_score))

    def finalize_match(self, match_id: int, main_player_won: bool) -> Match:
        match = self.get_match_by_id(match_id)

        if main_player_won:
            match.state = Match.MAIN_PLAYER_WON
        else:
            match.state = Match.OPPONENTS_WON

        return match

    def get_player_scores(self) -> dict:
        completed_matches = [match for match in self.matches if match.state != Match.NOT_PLAYED_YET]

        player_scores = {player: 0 for player in self.players}
        for match in completed_matches:
            if match.state == Match.MAIN_PLAYER_WON:
                player_scores[match.player] += match.prize_score
            else:
                for opponent in match.opponents:
                    player_scores[opponent] += math.ceil(match.prize_score / len(match.opponents))

        return player_scores
