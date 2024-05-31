import os

from apify_client import ApifyClient
import pandas as pd
from datetime import datetime
import xlsxwriter
import getpass
import time

# Retrieve all responses from a given a single tweet URL like:
#    https://twitter.com/MaxKevinC/status/1781174881050128396
#
# Or process all the URLs, one per line, in a text file specified, like:
#     /Users/davidsky/PycharmProjectselsalvador-local/tweet_list_to_process.txt

script_v = "V3.2"
# V3.2 - multiple additions
#          - add author id and author name of the political actor that posting the post
#          - add version number to filename
# V3.1 - add location and when the user started using twitter
# V3.0 - support a text file with a list of tweets to process
# V2.1 - bit more code cleanup - still expects a single Tweet to process, no list support yet
# V2.0 - rework the code to use more functions, clean up the code and add a main()
# V1.1 - read the API key from a system variable if it is set, otherwise ask
# v1.0 - some repeated code that should really be cleaned up
#   getpass is used to calculate the generated_by string for the Readme and can be replaced by a simple string if there
#        is a problem - hasn't been tested on Windows, only the Mac

def call_apify_client(reason_text, apify_client, tweet_url, actor_id, actor_input, df):
    """Call the Apify API with the variables required, then process it to return all the rows as specified in df"""
    # Run the Actor and wait for it to finish
    start_time = datetime.now()
    print(f"Calling the actor now for {reason_text}:\n\tURL >{tweet_url}<\n\tStart at", start_time.strftime("%H:%M:%S"))
    run = apify_client.actor(actor_id).call(run_input=actor_input)
    run_id = run["id"]
    end_time = datetime.now()
    print("...done at : ", end_time.strftime("%H:%M:%S"))

    # Fetch and print Actor results from the run's dataset (if there are any)
    run_status = apify_client.run(run_id).get()
    status = run_status["status"]
    print(f"Run status: {status}")
    i = 1
    for one_tweet_dict in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        print(format(i, '3'), end='...')
        df = tweet_to_df(df, one_tweet_dict)
        i += 1
        if i % 30 == 1:
            print("")
    print(" rows processed.\n")
    return df

def tweet_to_df(df, tweet_dict):
    """Given one dictionary of details on a single tweet, add a row to df based on the column names in the df"""
    items_to_collect = df.columns.tolist()
    new_row = len(df)
    # new_row = df.iloc[0:1].copy()
    for key, value in tweet_dict.items():
        # Need two cases - want
        #       author__location - maybe have: author__location - then save
        #       author__createdAt
        # print(f"Consider >{key}<")
        if key == 'author':
            # Hard coded values - sorry!
            # See if there is a author__location
            sub_value = value['location']
            df.loc[new_row, 'author__location'] = sub_value
            # And author_createdAt
            sub_value2 = value['createdAt']
            parsed_date = datetime.strptime(sub_value2, '%a %b %d %H:%M:%S %z %Y')
            # Format the datetime object into an ISO formatted date string
            iso_formatted_date = parsed_date.strftime('%Y-%m-%d')
            df.loc[new_row, 'author__createdAt'] = iso_formatted_date

            # Some items JUST for the political actors - V3.2
            sub_valueAI = value['id']
            df.loc[new_row, 'author__id'] = sub_valueAI

            sub_valueAN = value['name']
            df.loc[new_row, 'author__name'] = sub_valueAN

            sub_valueAD = value['description']
            df.loc[new_row, 'author__description'] = sub_valueAD

            sub_valueAF = value['followers']
            df.loc[new_row, 'author__followers'] = sub_valueAF

            sub_valueAV = value['isVerified']
            df.loc[new_row, 'author__verified'] = sub_valueAV



        else:
            # And the rest of the top level values
            if key in items_to_collect:
                # print(key, ":", value)
                df.loc[new_row, key] = value
    # df._append(new_row, ignore_index=True)
    return df

def get_tweet_list(filename):
    """Given a filename, load the file if possible, and create a list with the value of each line"""
    lines_list = []
    try:
        # Open the file and read the lines
        with open(filename, 'r') as file:
            for line in file:
                stripped_line = line.strip()  # Strip any leading/trailing whitespace (including newline characters)
                if stripped_line:  # Skip empty lines
                    lines_list.append(stripped_line)  # Add the stripped line to the list
    except:
        print(f"ERROR 704: Unable to open and process the file:\n\t>{filename}<")
        exit(-704)
    return lines_list

# Main script
def main():
    # Who is running the script? Will add this detail to the Readme tab -> generated_by row
    try:
        generated_by = getpass.getuser()
    except:
        generated_by = 'unknown_user'

    try:  # V1.1 - save having to ask for the APIfy token each time the script is run
        your_api_token = os.environ.get('APIFY_TOKEN')
    except:
        your_api_token = None
        print("Local system variable APIFY_TOKEN not set, will prompt for token.")

    # Variables we will need
    local_excel_path = "/Users/davidsky/PycharmProjectselsalvador-local"  # Change this to work on your system
    apify_actor_id = "61RPP7dywgiy0JPD0"  # Tweet Scraper V2 (Pay Per Result) - X / Twitter Scraper - https://apify.com/apidojo/tweet-scraper
    python_code_name = 'one_tweet_response.py'
    python_code_dagshub = 'https://dagshub.com/Omdena/IREX-El-Salvador-Sentiment/src/main/experiment/task-01-data-collection/David-Sky/one_tweet_responses.py'
    column_list = [  # The set of columns we will use to create the df from the APIfy call
        "url",
        "createdAt",
        "id",
        "isReply",
        "inReplyToId",
        "isRetweet",
        "isQuote",
        "viewCount",
        "retweetCount",
        "likeCount",
        "replyCount",
        "lang",
        "author__createdAt",
        "author__location",
        # Added for V3.2 for JUST the political actor collections
        "author__name",
        "author__id",
        "author__description",
        "author__followers",
        "author__verified",
        "text"
    ]
    remove_for_comments_column = [  # New for V3.2
        "author__name",
        "author__id",
        "author__description",
        "author__followers",
        "author__verified",
    ]


    log_columns = [  # V3.2 - write a log file for each time the script is run
        "initial_url",
        "response_count",
        "script_duration_secs",
        "generated_date_utc",
        "generated_by",
        "script_name",
        "script_version",
    ]

    # Get the Apify token and connect
    if your_api_token is not None:
        print(f"Using Apify token from system variable APIFY_TOKEN: '{your_api_token[:4]}...{your_api_token[-4:]}'")
    else:
        your_api_token = input("Enter your personal Apify token - or enter to quit: ")
        if len(your_api_token) < 2:
            print("Quiting\n")
        elif len(your_api_token) < 40:
            print(f"Quiting now - token seems too short - only {len(your_api_token)} characters")
        else:
            print("Token seems long enough, attempting to initialize with the token")

    # Otherwise - Initialize the ApifyClient with your Apify API token
    try:
        client = ApifyClient(your_api_token)
    except:
        print("Error 141: Unable to connect to APIfy using the token")
        exit(-141)

    print("\n\nSuccess: Connected to APIfy with token\n\n")

    start_time = time.perf_counter()
    # Get the URL of the tweet to analyze - todo - define multiple strings and loop through them
    print("Two options:\n(1) string that starts with http will be processed as a single tweet, or\n(2) otherwise will be considered a txt file with one line per URL")
    to_process_inp = input("Enter input for tweet(s) to analyze: ")

    # Is it a single tweet or a txt file with a list? Either way, create a list
    if to_process_inp.startswith('http'):
        # Just a single tweet
        to_process_list = [to_process_inp]
    else:
        # Expect a filename with the list of tweets, one per line - input txt like:
        # /Users/davidsky/PycharmProjectselsalvador-local/tweet_list_to_process.txt

        # create to_process_list from the file
        to_process_list = get_tweet_list(filename=to_process_inp)
        print("Will process each of the following URLs:")
        for one_test in to_process_list:
            print(f"\t- {one_test}")

    # V3.2
    log_df = pd.DataFrame(columns=log_columns)
    # Now run through all the values in to_process_list
    for one_tweet_url in to_process_list:
        print(f"Process the single URL {one_tweet_url}")
        one_tweet_id = str(one_tweet_url.split('/')[-1])
        one_tweet_user = one_tweet_url.split('/')[-3]
        one_tweet_string = f"{one_tweet_user}_X_{script_v}_replies_{one_tweet_id}"  # V3.2 added script_v to filename
        print(f"Will process the tweet: {one_tweet_string}")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Step 1: get the original Tweet
        run_input = {
            "startUrls": [one_tweet_url],
            "maxItems": 300,
        }
        # Define the columns we want from this APIfy call
        df_orig = pd.DataFrame(columns=column_list)
        df_initial_tweet = call_apify_client(reason_text="original tweet", apify_client=client, tweet_url=one_tweet_url, actor_id=apify_actor_id, actor_input=run_input, df=df_orig)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Step 2, get the responses
        run_input_conv = {
            "conversationIds": [one_tweet_id],  # The conversation ID is the long numeric string at the end of one_tweet_id
            "maxItems": 300,
        }
        df_conv = pd.DataFrame(columns=column_list)
        df_conv_tweets = call_apify_client(reason_text="response tweets", apify_client=client, tweet_url=one_tweet_id, actor_id=apify_actor_id, actor_input=run_input_conv, df=df_conv)

        # V3.2 - drop some of the column names we DON'T want to collect for the people commenting
        try:
            df_conv_tweets.drop(columns=remove_for_comments_column, inplace=True)
        except:
            print(f"Could not find: {remove_for_comments_column}")
            print(df_conv_tweets.columns)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final step, create the Excel file with multiple tabs
        local_excel = f"{local_excel_path}/{one_tweet_string}.xlsx"
        elapsed_time = time.perf_counter() - start_time
        # Create a readme df
        rm_data = {'Readme': ['Initial URL', 'Conversation ID', 'response count', 'script_length_sec', 'generated_on_utc', 'generated_by', 'python_code', 'script_version', 'dagshub_link', 'Apify_actor_id'],
                   'Notes': [one_tweet_url, one_tweet_id, len(df_conv), elapsed_time, datetime.utcnow(), generated_by, python_code_name, script_v, python_code_dagshub, apify_actor_id]
                   }
        rm_df = pd.DataFrame(rm_data)

        # Write each of these dataframes to one Excel spreadsheet
        with pd.ExcelWriter(local_excel, engine='xlsxwriter') as writer:
            # Write each DataFrame to a different sheet
            df_conv_tweets.to_excel(writer, sheet_name='responses', index=False)
            df_initial_tweet.to_excel(writer, sheet_name='initial_tweet', index=False)
            rm_df.to_excel(writer, sheet_name='Readme', index=False)

        print(f"\nCreated Excel file:\n\t{local_excel}")
        # End of processing one row in the list
        # V3.2 - add the details for this specific tweet to the log_df.
        new_log_row = {
            "initial_url": one_tweet_url,
            "response_count": len(df_conv),
            "script_duration_secs": elapsed_time,
            "generated_date_utc": datetime.utcnow(),
            "generated_by": generated_by,
            "script_name": python_code_name,
            "script_version": script_v,
            "output_file_name": f"{one_tweet_string}.xlsx"
        }
        new_row_df = pd.DataFrame([new_log_row])
        log_df = pd.concat([log_df, new_row_df], ignore_index=True)

    # Done processing one or more items, now write the log file
    log_file_name = datetime.utcnow().strftime('%Y-%m-%d_at_%H_%M_%S')
    log_file_full = f"{local_excel_path}/{log_file_name}.csv"
    print(f"Done! Writing log to {log_file_name}")
    log_df.to_csv(log_file_full, index=False)
    # End of main()

if __name__ == "__main__":

    main()