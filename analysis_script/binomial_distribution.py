import pandas as pd
from scipy.stats import binom


#1 Read the two main data sets
main_df = pd.read_excel("g6_research_data_cleaned.xlsx")

flipped_df = pd.read_excel("Flipped_Schools.xlsx")

in_state_players = main_df[main_df["Committed In-state"] == 1]

in_state_flips = flipped_df[flipped_df["Committed In-state"] == 1]

three_star_flips = flipped_df[flipped_df["Stars"] == 3]
four_star_flips = flipped_df[flipped_df["Stars"] == 4]
five_star_flips = flipped_df[flipped_df["Stars"] == 5]

p4_flips = flipped_df[flipped_df["P4_Flips"] == 1]

p4_zero_star_flips = p4_flips[p4_flips["Stars"] == 2]
p4_three_star_flips = p4_flips[p4_flips["Stars"] == 3]
p4_four_star_flips =  p4_flips[p4_flips["Stars"] == 4]
p4_five_star_flips  =   p4_flips[p4_flips["Stars"] == 5]


#Gets the total number of flips, players, etc

total_players = len(main_df)

total_flips = len(flipped_df)

total_p4_flips = len(p4_flips)


#Gets probabilities P = prob G = givin

PA = total_flips/total_players

PBGA = total_p4_flips / total_flips

PB = PA * PBGA

PC = len(p4_zero_star_flips)/total_flips

print(PC)

