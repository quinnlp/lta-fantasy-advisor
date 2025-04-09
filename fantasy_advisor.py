#!/usr/bin/env python3

import argparse
import tabulate
import yaml

NAME = "name"
TEAM = "team"
COST = "cost"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="yaml file containing the LTA fantasy state")
    parser.add_argument("-s", "--sort", default=2, type=int, help="column index to sort role tables (decreasing)")
    args = parser.parse_args()

    with open(args.filepath) as file:
        yamlfile = yaml.safe_load(file)

        opponent_dict = dict()  # tracks the opponents of each team
        for match in yamlfile["matches"]:
            if len(match) != 2:
                print(f"Error: match '{match}' does not have exactly two teams")
                exit(1)

            blue_team = match[0]
            red_team = match[1]
            opponent_dict.setdefault(blue_team, []).append(red_team)
            opponent_dict.setdefault(red_team, []).append(blue_team)

        opponent_table = []
        for team, opponent_list in opponent_dict.items():
            opponent_table.append([team, opponent_list])
        opponent_table.sort()  # sort alphabetically
        print(tabulate.tabulate(opponent_table, headers=["Teams", "Matches"]))
        print()

        for role in ["top", "jungle", "mid", "bottom", "support"]:
            role_dict = dict()  # tracks the cost of each team's player for this role
            for player_dict in yamlfile[role]:
                if player_dict[TEAM] in role_dict.keys():
                    print(f"Error: duplicate team '{player_dict[TEAM]}' in role '{role}'")
                    exit(1)

                role_dict[player_dict[TEAM]] = player_dict[COST]

            role_table = []
            for player_dict in yamlfile[role]:
                cost_against = 0.0
                cost_against_str = str(player_dict[COST])
                for opponent in opponent_dict[player_dict[TEAM]]:
                    cost_against += role_dict[opponent] 
                    cost_against_str += f" - {role_dict[opponent]}"
                cost_against_str += " ="

                role_table.append([player_dict[NAME], player_dict[TEAM], player_dict[COST], cost_against_str, player_dict[COST] - cost_against])
                role_table.sort(key=lambda x: x[args.sort], reverse=True)  # sort decreasing cost

            print(tabulate.tabulate(role_table, headers=[NAME, TEAM, COST, "computation", "value"]))
            print()

if __name__ == "__main__":
    main()
