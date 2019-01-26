import os
import sys
import logic
from logic import chk_is_whitespace

###
# METHOD DECLARATION
###


def clear_console():
    """Clear console using system-specific command"""
    clear_command_string = 'clear' if 'linux' in sys.platform else 'cls'
    os.system(clear_command_string)


def display_players_info(clear_console_prior: bool = True):
    """Display players"""
    if clear_console_prior:
        clear_console()

    print('Players:')
    print(*(f'{player.id}: {player.name}' for player in controller.players), sep="\n")


def display_games_info(clear_console_prior: bool = True):
    """Display games"""
    if clear_console_prior:
        clear_console()

    print('Games:')
    print(*(f'{game.id}: {game.name}' for game in controller.games), sep="\n", end="\n")


def display_matches_list(clear_console_prior: bool = True):
    """Display matches"""
    if clear_console_prior:
        clear_console()

    print("Matches:")
    print(*controller.matches, sep="\n")


def display_scoreboard(clear_console_prior: bool = True):
    """Display scoreboard"""
    if clear_console_prior:
        clear_console()

    print("Scoreboard:")
    player_scores = controller.get_player_scores()
    scoreboard = sorted(
        [entry for entry in zip(player_scores.keys(), player_scores.values())], key=lambda x: x[1], reverse=True)

    for entry in scoreboard:
        print(f'{entry[0]}: {entry[1]}')


def display_menu_options(clear_console_prior: bool = True):
    """Display menu options - actions that can be invoked in application"""
    if clear_console_prior:
        clear_console()

    options = ['Finalize match', 'Display scoreboard', 'Display matches']

    for (index, option) in enumerate(options):
        print(f'{index+1}: {option}')


###
# START OF SCRIPT LIFECYCLE
###

# Read player names and game names and amount of round to be played by each player
# Added exception handling logic
player_names = input("Player names (comma separated): ")

if chk_is_whitespace(player_names):
    raise ValueError('One or more of player names is blank. Please focus next time głuptasie')

player_names = player_names.replace(' ', '').split(',')

game_names = input("Game names (comma separated): ")

if chk_is_whitespace(game_names):
    raise ValueError('One or more of game names is blank. Please focus next time głuptasie')

game_names = game_names.replace(' ', '').split(',')

round_count = int(input("Round count (default: 1): ") or 1)

# Initialise controller
controller = logic.TournamentController(player_names, game_names)

# Gather data about all matches (who plays what game with whom etc.)
for rounds in range(round_count):
    for player in controller.players:
        display_games_info()
        print('')
        display_players_info(False)
        print(f'\nMatch details for Player: {player.name} ')

        game_id = input('Game ID (ENTER for random): ')
        if game_id == '':
            game = controller.randomize_game()
            game_id = game.id
            print(f'Randomized game: {game}')
        else:
            game_id = int(game_id)
            game = controller.get_game_by_id(game_id)
            print(f'Selected game: {game}')

        excluded_opponent_ids = [player.id]
        all_player_ids = [p.id for p in controller.players]
        opponent_ids = []

        while len(opponent_ids) < 2:
            opponent_id = input(f'Opponent #{len(opponent_ids)+1} ID (ENTER for random{", - for none" if len(opponent_ids) > 0 else ""}): ')
            if opponent_id == '-':
                if len(opponent_ids) > 0:
                    break
            else:
                try:
                    opponent_id = int(opponent_id)
                    if (opponent_id in all_player_ids) and (opponent_id not in excluded_opponent_ids):
                        opponent_ids.append(opponent_id)
                        excluded_opponent_ids.append(opponent_id)
                    else:
                        print('Player already takes part in this match or provided value is not a correct Player ID')
                except ValueError:
                    randomized_opponent = controller.randomize_player(excluded_ids=excluded_opponent_ids)
                    opponent_ids.append(randomized_opponent.id)
                    excluded_opponent_ids.append(randomized_opponent.id)

        controller.add_match(player.id, opponent_ids, game_id)

# User action loop
while True:
    display_menu_options()
    selected_option = int(input('Option: ') or 0)

    if selected_option == 1:  # 'Finalize match'
        display_matches_list()
        try:
            match_id = int(input('Match ID: '))
            match = controller.get_match_by_id(match_id)
            main_player_won = (input(f'{match.player.name} won? [Y/n]: ') or 'y').lower() == 'y'
            controller.finalize_match(match_id, main_player_won)
        except ValueError:
            print('No match selected')

    elif selected_option == 2:  # 'Display scoreboard'
        display_scoreboard()

    elif selected_option == 3:  # 'Display matches'
        display_players_info()
        try:
            player_id = int(input('Player ID (ENTER for all): '))
            player = controller.get_player_by_id(player_id)
            main_player_only = (input(f'{player.name} only as main player? [y/N]: ') or 'n').lower() == 'y'
            print('Matches: ', *controller.get_matches_by_player_id(player_id, main_player_only), sep='\n')
        except ValueError:
            display_matches_list()
    else:
        print('Incorrect option selected')

    input('Press any key to continue...')
