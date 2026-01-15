#!/usr/bin/env python

import argparse
import tabulate
import yaml

NAME = "name"
TEAM = "team"
COST = "cost"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="yaml file containing the LCS fantasy state")
    parser.add_argument("-k", "--key", default=0, type=int, help="column index to sort role tables")
    parser.add_argument("-r", "--reverse", action="store_true", default=False, help="sort column in reverse order")
    args = parser.parse_args()

    if args.key < 0 or args.key > 5:
        print(f"Error: invalid key '{args.key}'")
        exit(1)

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
        print(tabulate.tabulate(opponent_table, headers=[TEAM, "opponents"]))
        print()

        for role in ["top", "jungle", "mid", "bottom", "support", "coach"]:
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

            max_value = max(row[4] for row in role_table)
            for row in role_table:
                row.append(max_value - row[4])

            role_table.sort(key=lambda row: row[args.key], reverse=args.reverse)
            print(tabulate.tabulate(role_table, headers=[NAME, TEAM, COST, "computation", "value", "delta"]))
            print()

if __name__ == "__main__":
    main()
