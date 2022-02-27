import os
import sys
import ast
import requests
import itertools
import threading
import pandas as pd
import bar_chart_race as bcr
from bs4 import BeautifulSoup
from datetime import datetime as dt
from time import sleep


# Configuration Variables
PAUSE_IN_END = 3                  # In seconds
OUTPUT_FILE_NAME = "output.mp4"   # use .gif extension to make gif
READ_INPUT_FROM_FILE = True       # If False or file doesn't exists, then takes input from user
INPUT_FILE_NAME = "input.txt"     # To store CodeForces user handles in separate lines
VIDEO_TITLE = "Codeforces Ratings Racer"     # Default title of video
USE_HANDLE_INSTEAD_OF_NAME = False           # If True, then it will show actual name of user in video


# Gobal Variables
CONTESTS = {}      # Contains a dictionary of contest_date_obj: contest_name
USERS_RATING = {}  # Nested dictionary to store ratings of all users
DATES = []         # List of all contest dates objects
REAL_NAME = {}     # Distionary of handle: name
DONE = False


def take_handle_input():
    """
    Takes input from a file input.txt and returns a list of handles
    If file doesn't exists then takes input from user
    """

    global READ_INPUT_FROM_FILE

    if not os.path.exists("input.txt") or not READ_INPUT_FROM_FILE:
        # File doesn't exists' so taking input from user
        handles = []
        while 1:
            handle = input("Enter CodeForces handle (or press Enter if done): ")
            if handle == "":
                break
            handles.append(handle)
        return handles

    with open(INPUT_FILE_NAME, "r") as f:
        handles = f.readlines()
    return [h.strip() for h in handles]


def parse_string_date(date_time_str):
    """
    Takes a string of the form "Feb/23/2022" and returns a date object
    """
    return dt.strptime(date_time_str.split()[0], "%b/%d/%Y").date()


def ratings_scraper(handle):
    """
    Takes a user handle and returns a list of their CF ratings and date of contest
    Returns empty list if user has not given any contest
    Returns None if user doesn't exists or HTTP error occurs
    """
    
    global CONTESTS
    global REAL_NAME

    url = "https://codeforces.com/profile/{}".format(handle)
    resp = requests.get(url)

    if resp:
        soup = BeautifulSoup(resp.content, "html.parser")
        
        try:
            script_tag = soup.findAll('script')[51]

            script_str = str(script_tag).replace("\r", " ").replace("\n", " ").replace("Rated for ", "")
            while "  " in script_str:
                script_str = script_str.replace("  ", " ")

            
            data_list_str = script_str.split("; data.push")[1][1:-1]
            data_list = ast.literal_eval(data_list_str)
            
        except IndexError:
            return None           # User doesn't exists
        
        try:
            # Fetching name
            main_info = soup.find_all("div", class_="main-info")
            name = handle  # Default name
            for d in main_info[0].find_all("div"):
                if "font-size: 0.8em; color: #777;" in str(d.div):
                    name_line = d.div.text
                    name = name_line.split(",")[0]
                    break
            name = name.title()   # To capitalize first letter of each word
            REAL_NAME[handle] = name

        except:
            REAL_NAME[handle] = handle

        ratings_data = {}
        for row in data_list:
            contest_date_time = BeautifulSoup(row[-2].replace("\\",""), "html.parser").text
            ratings = row[1]
            rank = row[6]
            contest_name = row[3]
            short_contest_name = contest_name.replace("Round ", "").replace("Codeforces", "CF")
            # print(contest_date, ratings, rank, contest_name)
            date_obj = parse_string_date(contest_date_time)
            CONTESTS[date_obj] = short_contest_name
            ratings_data[date_obj] = ratings
        
        return ratings_data
    
    else:
        print("Error: Could not connect to Codeforces")
        print("HTTP error: {}".format(resp.status_code))
        return None


def loading():
    sleep(1)      # Initial pause; Could be removed
    for c in itertools.cycle(['|', '/', '-', '\\']):
        global DONE
        if DONE:
            break
        sys.stdout.write('\rIt may take few minutes... ' + c)
        sys.stdout.flush()
        sleep(0.1)
    sys.stdout.write('\rDone!                              ')


def main():
    global USERS_RATING
    global CONTESTS
    global DATES
    global REAL_NAME
    global DONE
    global INPUT_FILE_NAME
    global OUTPUT_FILE_NAME
    global VIDEO_TITLE
    global USE_HANDLE_INSTEAD_OF_NAME

    user_handles = take_handle_input()
    # Removing duplicates
    user_handles = list(set(user_handles))

    if len(user_handles) == 0:
        print(f"\nPlease Enter CodeForces user handles list in {INPUT_FILE_NAME} file and try again.\n")
        return

    for user in user_handles:
        print(f"Fetching data for {user}")
        ratings_data = ratings_scraper(user)

        if ratings_data is None:
            print(f"Unable to fetch ratings for {user}\n")
            user_handles.remove(user)
            continue

        elif ratings_data == {}:
            print(f"User {user} has not participated in any contests\n")
            user_handles.remove(user)
            continue

        else:
            USERS_RATING[user] = ratings_data
            print(f"{len(ratings_data)} Contests participated by {user}\n")
    

    DATES = list(CONTESTS.keys())
    DATES.sort()
    DATES += [DATES[-1]]*PAUSE_IN_END*2    # To pause the video in the end; Because one period is 500ms

    # Making a name list to for each bar title
    if USE_HANDLE_INSTEAD_OF_NAME:
        name_list = user_handles
    else:
        name_list = []
        for handle in user_handles:
            real_name = REAL_NAME[handle]
            first_two = real_name.split()[:2]
            name_list.append(" ".join(first_two))


    # Making pandas dataframe and merging all user data of contests
    df = pd.DataFrame(columns=name_list, index=DATES)

    prev_row = [0]*len(user_handles)

    for date in DATES:
        cur_row = []
        for i in range(len(user_handles)):
            handle = user_handles[i]
            if date in USERS_RATING[handle]:
                # User gave the contest
                cur_row.append(USERS_RATING[handle][date])
            else:
                # User didn't gave the contest and his ratings will remain same
                cur_row.append(prev_row[i])
        df.loc[date] = cur_row
        prev_row = cur_row


    # Convert datatypes of columns from object to int64
    df.index = pd.to_datetime(df.index)
    df[name_list] = df[name_list].apply(pd.to_numeric)


    # Output file name
    print(f"\nEnter output filename with extension (default: {OUTPUT_FILE_NAME})")
    print("Supported formats are: .mp4, .gif, .html, .mpeg, .mov")
    temp = input("Enter filename (or press Enter to use default): ")
    if temp != "":
        if not (temp.endswith(".mp4") or temp.endswith(".gif") or temp.endswith(".html") or temp.endswith(".mpeg") or temp.endswith(".mov")):
            print("Invalid file extension. Using default")
        OUTPUT_FILE_NAME = temp


    # Video title
    print(f"\nEnter video title (default: {VIDEO_TITLE})")
    temp = input("Enter title (or press Enter to use default): ")
    if temp!="":
        VIDEO_TITLE = temp


    # Now creating video of the dataframe using bar_chart_racer
    print("\nCreating video of the contest data of all the users\n")
    print("It may take few minutes...", end="")
    threading.Thread(target=loading).start()
    bcr.bar_chart_race(
        df=df,
        end_period_pause=50,
        period_template='%B %d, %Y',
        colors='dark12',
        title=VIDEO_TITLE,
        bar_label_font=6,
        tick_label_font=9,
        fixed_max=True,
        filter_column_colors=True,
        period_length=500,
        filename=OUTPUT_FILE_NAME
    )

    DONE = True
    sleep(.2)
    print("\n\n\nThanks for using CF Racer")
    print("See you soon")



if __name__ == "__main__":
    main()
