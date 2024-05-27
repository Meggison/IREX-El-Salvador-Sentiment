import os

from apify_client import ApifyClient
import pandas as pd
from datetime import datetime
import xlsxwriter
import getpass

# Given a single tweet URL like
#    https://twitter.com/MaxKevinC/status/1781174881050128396
#
# Retrieve all the responses
#
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
        if key in items_to_collect:
            # print(key, ":", value)
            df.loc[new_row, key] = value
    # df._append(new_row, ignore_index=True)
    return df


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
        "text"
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


    # Get the URL of the tweet to analyze - todo - define multiple strings and loop through them
    one_tweet_url = input("Enter the full URL of the tweet to analyze: ")
    one_tweet_id = str(one_tweet_url.split('/')[-1])
    one_tweet_user = one_tweet_url.split('/')[-3]
    one_tweet_string = f"{one_tweet_user}_X_replies_{one_tweet_id}"
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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Final step, create the Excel file with multiple tabs
    local_excel = f"{local_excel_path}/{one_tweet_string}.xlsx"

    # Create a readme df
    rm_data = {'Readme': ['Initial URL', 'Conversation ID', 'response count', 'generated_on_utc', 'generated_by', 'python_code', 'dagshub_link', 'Apify_actor_id'],
               'Notes': [one_tweet_url, one_tweet_id, len(df_conv), datetime.utcnow(), generated_by, python_code_name, python_code_dagshub, apify_actor_id]
               }
    rm_df = pd.DataFrame(rm_data)

    # Write each of these dataframes to one Excel spreadsheet
    with pd.ExcelWriter(local_excel, engine='xlsxwriter') as writer:
        # Write each DataFrame to a different sheet
        df_conv_tweets.to_excel(writer, sheet_name='responses', index=False)
        df_initial_tweet.to_excel(writer, sheet_name='initial_tweet', index=False)
        rm_df.to_excel(writer, sheet_name='Readme', index=False)

    print(f"\nCreated Excel file:\n\t{local_excel}")
    # End of main()

if __name__ == "__main__":
    main()