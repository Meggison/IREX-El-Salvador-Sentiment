import pandas as pd
import pygsheets

class objWorkSheet:
    def __init__(self, gs_id, gs_page, verbose=False):
        self.google_sheet_id = gs_id
        self.google_sheet_tab = gs_page
        self.has_url_to_process = False


        print(f"Open the Google Sheet from:\n\tID: {self.google_sheet_id}\n\tTab:{self.google_sheet_tab}")
        try:
            gc = pygsheets.authorize()
            sh = gc.open_by_key(self.google_sheet_id)
            self.wks = sh.worksheet_by_title(self.google_sheet_tab)
            df = self.wks.get_as_df()
            print(f"Read meta-data worksheet size: {df.shape}")
        except:
            print(f"Error 8711: Unable to access Google Sheet - is the file here and up to date:\n\tsheets.googleapis.com-python.json")
            exit(-112)

        # Pick the 1st value in the URL column where the other columns are empty
        df_incomplete = df[df.drop('URL', axis=1).eq('').all(axis=1)]
        if len(df_incomplete) > 0:
            self.next_url_value = df_incomplete['URL'].iloc[0]
            print(f"Will process the URL {self.next_url_value}") if verbose else None
            self.has_url_to_process = True
        else:
            print("All rows in the spreadsheet are complete, no new URLs to process")  if verbose else None
            self.has_url_to_process = False

    def get_next_url_value(self):
        return self.next_url_value

    def hasNoURLtoProcess(self):
        return not self.has_url_to_process

    def addNewRowData(self, new_values, verbose=True):
        # Write the data back to the Google spreadsheet for the URL we've read
        data = self.wks.get_all_records()
        row_index = None
        for i, row in enumerate(data):
            if row['URL'] == self.next_url_value:
                row_index = i + 2  # Add 2 because row indexing starts from 1 and get_all_records() returns data with header row
                print(f"Row index is: {row_index}") if verbose else None
                break
        if row_index is not None:
            # Specify the data you want to write to the row
            new_data = {
                'Title': 'New title',
                'Description': 'New description',
                # Add more columns and values as needed
            }
            new_data = [['new value 1', 'new value 2']]

            # Update the values in the corresponding row
            self.wks.update_row(row_index, new_values, 1)
            print("Data updated successfully.")
        else:
            print("URL not found in the spreadsheet.")


