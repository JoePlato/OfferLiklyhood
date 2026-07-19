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
    "Iowa State", "Kansas", "Kansas State", "Oklahoma State", "Oregon State","TCU", 
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
    "South Alabama", "Southern Miss", "Texas State", "Troy", "UConn", "UMass", "USF"
}

SCHOOL_LOCATIONS = {
    # Power 4 Schools
    "Alabama": ["Alabama", "Tuscaloosa"],
    "Arizona": ["Arizona", "Tucson"],
    "Arizona State": ["Arizona", "Tempe"],
    "Arkansas": ["Arkansas", "Fayetteville"],
    "Auburn": ["Alabama", "Auburn"],
    "Baylor": ["Texas", "Waco"],
    "Boston College": ["Massachusetts", "Chestnut Hill"],
    "BYU": ["Utah", "Provo"],
    "California": ["California", "Berkeley"],
    "Cincinnati": ["Ohio", "Cincinnati"],
    "Clemson": ["South Carolina", "Clemson"],
    "Colorado": ["Colorado", "Boulder"],
    "Duke": ["North Carolina", "Durham"],
    "Florida": ["Florida", "Gainesville"],
    "Florida State": ["Florida", "Tallahassee"],
    "Georgia": ["Georgia", "Athens"],
    "Georgia Tech": ["Georgia", "Atlanta"],
    "Houston": ["Texas", "Houston"],
    "Illinois": ["Illinois", "Champaign"],
    "Indiana": ["Indiana", "Bloomington"],
    "Iowa": ["Iowa", "Iowa City"],
    "Iowa State": ["Iowa", "Ames"],
    "Kansas": ["Kansas", "Lawrence"],
    "Kansas State": ["Kansas", "Manhattan"],
    "Kentucky": ["Kentucky", "Lexington"],
    "LSU": ["Louisiana", "Baton Rouge"],
    "Louisville": ["Kentucky","Louisville"],
    "Maryland": ["Maryland", "College Park"],
    "Miami": ["Florida", "Coral Gables"],
    "Michigan": ["Michigan", "Ann Arbor"],
    "Michigan State": ["Michigan", "East Lansing"],
    "Minnesota": ["Minnesota", "Minneapolis"],
    "Mississippi State": ["Mississippi", "Starkville"],
    "Missouri": ["Missouri", "Columbia"],
    "NC State": ["North Carolina", "Raleigh"],
    "Nebraska": ["Nebraska", "Lincoln"],
    "North Carolina": ["North Carolina", "Chapel Hill"],
    "Northwestern": ["Illinois", "Evanston"],
    "Notre Dame": ["Indiana", "Notre Dame"],
    "Ohio State": ["Ohio", "Columbus"],
    "Oklahoma": ["Oklahoma", "Norman"],
    "Oklahoma State": ["Oklahoma", "Stillwater"],
    "Ole Miss": ["Mississippi", "Oxford"],
    "Oregon": ["Oregon", "Eugene"],
    "Penn State": ["Pennsylvania", "University Park"],
    "Pittsburgh": ["Pennsylvania", "Pittsburgh"],
    "Purdue": ["Indiana", "West Lafayette"],
    "Rutgers": ["New Jersey", "New Brunswick"],
    "SMU": ["Texas", "Dallas"],
    "South Carolina": ["South Carolina", "Columbia"],
    "Stanford": ["California", "Stanford"],
    "Syracuse": ["New York", "Syracuse"],
    "TCU": ["Texas", "Fort Worth"],
    "Tennessee": ["Tennessee", "Knoxville"],
    "Texas": ["Texas", "Austin"],
    "Texas A&M": ["Texas", "College Station"],
    "Texas Tech": ["Texas", "Lubbock"],
    "UCF": ["Florida", "Orlando"],
    "UCLA": ["California", "Los Angeles"],
    "USC": ["California", "Los Angeles"],
    "Utah": ["Utah", "Salt Lake City"],
    "Vanderbilt": ["Tennessee", "Nashville"],
    "Virginia": ["Virginia", "Charlottesville"],
    "Virginia Tech": ["Virginia", "Blacksburg"],
    "Wake Forest": ["North Carolina", "Winston-Salem"],
    "Washington": ["Washington", "Seattle"],
    "West Virginia": ["West Virginia", "Morgantown"],
    "Wisconsin": ["Wisconsin", "Madison"],

    # Group of 5 Schools
    "Air Force": ["Colorado", "Colorado Springs"],
    "Akron": ["Ohio", "Akron"],
    "Appalachian State": ["North Carolina", "Boone"],
    "Arkansas State": ["Arkansas", "Jonesboro"],
    "Army": ["New York", "West Point"],
    "Ball State": ["Indiana", "Muncie"],
    "Boise State": ["Idaho", "Boise"],
    "Bowling Green": ["Ohio", "Bowling Green"],
    "Buffalo": ["New York", "Buffalo"],
    "Central Michigan": ["Michigan", "Mount Pleasant"],
    "Charlotte": ["North Carolina", "Charlotte"],
    "Coastal Carolina": ["South Carolina", "Conway"],
    "Colorado State": ["Colorado", "Fort Collins"],
    "East Carolina": ["North Carolina", "Greenville"],
    "Eastern Michigan": ["Michigan", "Ypsilanti"],
    "FIU": ["Florida", "Miami"],
    "Florida Atlantic": ["Florida", "Boca Raton"],
    "Fresno State": ["California", "Fresno"],
    "Georgia Southern": ["Georgia", "Statesboro"],
    "Georgia State": ["Georgia", "Atlanta"],
    "Hawaii": ["Hawaii", "Honolulu"],
    "Jacksonville State": ["Alabama", "Jacksonville"],
    "James Madison": ["Virginia", "Harrisonburg"],
    "Kennesaw State": ["Georgia", "Kennesaw"],
    "Kent State": ["Ohio", "Kent"],
    "Liberty": ["Virginia", "Lynchburg"],
    "Louisiana": ["Louisiana", "Lafayette"],
    "Louisiana Tech": ["Louisiana", "Ruston"],
    "Louisiana-Monroe": ["Louisiana", "Monroe"],
    "Marshall": ["West Virginia", "Huntington"],
    "Memphis": ["Tennessee", "Memphis"],
    "Miami (OH)": ["Ohio", "Oxford"],
    "Middle Tennessee": ["Tennessee", "Murfreesboro"],
    "Navy": ["Maryland", "Annapolis"],
    "Nevada": ["Nevada", "Reno"],
    "New Mexico": ["New Mexico", "Albuquerque"],
    "New Mexico State": ["New Mexico", "Las Cruces"],
    "North Texas": ["Texas", "Denton"],
    "Northern Illinois": ["Illinois", "DeKalb"],
    "Oregon State": ["Oregon", "Benton County"],
    "Ohio": ["Ohio", "Athens"],
    "Old Dominion": ["Virginia", "Norfolk"],
    "Rice": ["Texas", "Houston"],
    "Sam Houston": ["Texas", "Huntsville"],
    "San Diego State": ["California", "San Diego"],
    "San Jose State": ["California", "San Jose"],
    "South Alabama": ["Alabama", "Mobile"],
    "South Florida": ["Florida", "Tampa"],
    "Southern Miss": ["Mississippi", "Hattiesburg"],
    "Temple": ["Pennsylvania", "Philadelphia"],
    "Texas State": ["Texas", "San Marcos"],
    "Toledo": ["Ohio", "Toledo"],
    "Troy": ["Alabama", "Troy"],
    "Tulane": ["Louisiana", "New Orleans"],
    "Tulsa": ["Oklahoma", "Tulsa"],
    "UAB": ["Alabama", "Birmingham"],
    "UConn": ["Connecticut", "Storrs"],
    "UMass": ["Massachusetts", "Amherst"],
    "UNLV": ["Nevada", "Las Vegas"],
    "Utah State": ["Utah", "Logan"],
    "UTEP": ["Texas", "El Paso"],
    "UTSA": ["Texas", "San Antonio"],
    "Western Kentucky": ["Kentucky", "Bowling Green"],
    "Western Michigan": ["Michigan", "Kalamazoo"],
    "Wichita State": ["Kansas", "Wichita"],
    "Wyoming": ["Wyoming", "Laramie"],
    "Washington State": ["Pullman","Washington"],
    "USF": ["Tampa", "Florida"]
}



# 1. Access the excel data
df = pd.read_excel("g6_research_data_cleaned.xlsx")

#Filter out unknown or uncommitted players
# df = df[df["Last_Commit"] != "Unknown"]
# df = df[df["Last_Commit"] != "Uncommitted"]

df2 = df.copy()

# df2.insert(loc=17, column='Committed In-state', value=0)

# school_states = df2["Last_Commit"].map(lambda school: SCHOOL_LOCATIONS[school][0]) #type: ignore

# # # 2. Compare the new Series of school states to the student's state column
# df2.loc[school_states == df["State"], "Committed In-state"] = 1



# #2. Seperating the states and hometown in the main
# # split_data = df["Hometown"].str.split(", ", expand=True)

# # df["Hometown"] = split_data[0]

# # df.insert(loc=3, column='State', value=split_data[1])

# #3. Filtering out schools that had 0 flips
df2 = df2[df2["Flip_Count"] > 0]

df2.insert(loc=17, column='P4_Flips', value=0)

# #4. Getting the school the flipped from the most recently
first_school_flipped = df2["Flipped_From"].str.split(",").str[0].str.strip()

is_first_p4 = first_school_flipped.isin(P4_SCHOOLS)
is_last_g6 = df2["Last_Commit"].isin(G5_SCHOOLS)

df2.loc[is_first_p4 & is_last_g6, "P4_Flips"] = 1


# # print(filtered_df.shape)
df2.to_excel("Flipped_Schools.xlsx", index = False)
#4. Getting the number of times people switched from a p4 school to a G6 School

#5.Saving the excel file 
# df.to_excel("g6_research_data_cleaned.xlsx")