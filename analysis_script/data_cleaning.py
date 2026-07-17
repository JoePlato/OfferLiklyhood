import pandas as pd


P4_SCHOOLS = {
    "Alabama", "Arkansas", "Auburn", "Florida", "Georgia", "Kentucky", "LSU", 
    "Mississippi State", "Missouri", "Oklahoma", "Ole Miss", "South Carolina", 
    "Tennessee", "Texas", "Texas A&M", "Vanderbilt", "Illinois", "Indiana", 
    "Iowa", "Maryland", "Michigan", "Michigan State", "Minnesota", "Nebraska", 
    "Northwestern", "Ohio State", "Oregon", "Penn State", "Purdue", "Rutgers", 
    "UCLA", "USC", "Washington", "Wisconsin", "Boston College", "California", 
    "Clemson", "Duke", "Florida State", "Georgia Tech", "Louisville", "Miami", 
    "North Carolina", "NC State", "Pittsburgh", "SMU", "Stanford", "Syracuse", 
    "Virginia", "Virginia Tech", "Wake Forest", "Notre Dame", "Arizona", 
    "Arizona State", "Baylor", "BYU", "Cincinnati", "Colorado", "Houston", 
    "Iowa State", "Kansas", "Kansas State", "Oklahoma State", "TCU", 
    "Texas Tech", "UCF", "Utah", "West Virginia"
}

G5_SCHOOLS = {
    "Army", "Charlotte", "East Carolina", "Florida Atlantic", "Memphis", "Navy", 
    "North Texas", "Rice", "South Florida", "Temple", "Tulane", "Tulsa", "UAB", 
    "UTSA", "Wichita State", "FIU", "Jacksonville State", "Liberty", 
    "Louisiana Tech", "Middle Tennessee", "New Mexico State", "Sam Houston", 
    "UTEP", "Western Kentucky", "Kennesaw State", "Akron", "Ball State", 
    "Bowling Green", "Buffalo", "Central Michigan", "Eastern Michigan", 
    "Kent State", "Miami (OH)", "Northern Illinois", "Ohio", "Toledo", 
    "Western Michigan", "Air Force", "Boise State", "Colorado State", 
    "Fresno State", "Hawaii", "Nevada", "New Mexico", "San Diego State", 
    "San Jose State", "UNLV", "Utah State", "Wyoming", "Appalachian State", 
    "Arkansas State", "Coastal Carolina", "Georgia Southern", "Georgia State", 
    "James Madison", "Louisiana", "Louisiana-Monroe", "Marshall", "Old Dominion", 
    "South Alabama", "Southern Miss", "Texas State", "Troy", "UConn", "UMass"
}


# 1. Access the excel data
df = pd.read_excel("g6_research_data.xlsx")
df2 = df.copy()

#2. Seperating the states and hometown
split_data = df["Hometown"].str.split(", ", expand=True)

df["Hometown"] = split_data[0]

df.insert(loc=3, column='State', value=split_data[1])

#3. Filtering out schools that had 0 flips
df2 = df2[df2["Flip_Count"] > 0]

df2.insert(loc=17, column='P4_Flips', value=0)

#4. Getting the school the flipped from the most recently
first_school_flipped = df2["Flipped_From"].str.split(",").str[0].str.strip()

is_first_p4 = first_school_flipped.isin(P4_SCHOOLS)
is_last_g6 = df["Last_Commit"].isin(G5_SCHOOLS)

filtered_df = df[is_first_p4 & is_last_g6]
print(filtered_df.shape)
filtered_df.to_excel("Flipped_to_p4_Schools.xlsx")
#4. Getting the number of times people switched from a p4 school to a G6 School

#5.Saving the excel file 
#df.to_excel("g6_research_data_cleaned.xlsx")