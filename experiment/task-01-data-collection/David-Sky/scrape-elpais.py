from objOneWebPage import *
from objWorkSheet import *

# Update for your local file system
cache_folder = '/Users/davidsky/PycharmProjectselsalvador-local/cache/elpais/'
google_sheet_id='1Uutt8Yv_8Dt3tHDM2RgJ5jQvbkLD5hNP-a3ZIs7x1PI'
page_name='scraped data'

show_debug = True  # Set to False to hide debug information

# Pick a URL that hasn't been scraped
work_sheet = objWorkSheet(gs_id=google_sheet_id, gs_page=page_name, verbose=False)
if work_sheet.hasNoURLtoProcess():
    print("There are no URLs in the worksheet to process")
    exit(-123)

# We have the URL to work with, so scrape
webpage = objOneWebPage(url=work_sheet.get_next_url_value(), cache=cache_folder, verbose=False)
if webpage.scrapeSuccess():
    # Good news, we could scrap the URL
    print(f"Scrape was a success:{webpage}")

    # Now write the details back to the Google Sheet
    work_sheet.addNewRowData(new_values=webpage.valuesToInsertList())
