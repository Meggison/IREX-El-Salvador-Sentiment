from objOneWebPage import *
from objWorkSheet import *

class objWebPage_CNN(objOneWebPage):
    # Should only need the following specific function for this data source:


    def get_tag(self, tag, verbose=False):
        # Two cases - some pages have <div class="news__excerpt"> and <h1 class="news__title">
        # If so, will rename the tag with "-excerpt" and specify different patterns to search for
        if '<div class="news__excerpt">' in self.html:
            print("\n\nFound news__excerpt\n\n")
            if tag in ['contents', 'author', 'keywords', 'creation_date']:
                tag = f"{tag}-excerpt"

        if tag == 'title':
            pattern = r'<title>(.*?)</title>'

        elif tag == 'description':
            pattern = r'<meta name="description" content="(.*?)"\s?/>'

        elif tag == 'contents-excerpt':
            pattern = r'<div class=.news__excerpt.>(.*?)<.div>'
        elif tag == 'contents':
            pattern = r'<p><strong>(?:.*?)<.strong>(.*?)<div class=.tag'

        elif tag == 'keywords-excerpt':
            pattern = r'<div class=.news__tags.>(.*?)<.div>'
        elif tag == 'keywords':
            pattern = r'"keywords":\[(.*?)\],'

        elif tag == 'author-excerpt':
            pattern = r'<span itemprop=.name.>(.*?)<.span>'
        elif tag == 'author':
            pattern = r'<meta name="author" content="(.*?)" />'

        elif tag == 'creation_date-excerpt':
            pattern = r'itemprop="datePublished" datetime="([0-9\-]*?)"'
        elif tag == 'creation_date':
            pattern = r'<meta property="article:published_time" content="(.*?)" />'

        try:
            matches = re.findall(pattern, self.html, re.DOTALL)
            return matches[0]
        except:
            return f"Not found: {tag}"

# Update for your local file system
cache_folder = '/Users/davidsky/PycharmProjectselsalvador-local/cache/cnn/'
google_sheet_id = '1DreXINNN40B-GA3CzC7qfeqOLg7OiD1VYHK6i0ndaU4'
page_name = 'scraped data'

show_debug = True  # Set to False to hide debug information

# Pick a URL that hasn't been scraped
work_sheet = objWorkSheet(gs_id=google_sheet_id, gs_page=page_name, verbose=show_debug)
if work_sheet.hasNoURLtoProcess():
    print("There are no URLs in the worksheet to process")
    exit(-123)

# We have the URL to work with, so scrape
print(f"Ready to scrape.")
webpage = objWebPage_CNN(url=work_sheet.get_next_url_value(), cache=cache_folder, language='Spanish', verbose=show_debug)
if webpage.scrapeSuccess():
    print(f"Scrape was a success:{webpage}")
    # Now write the details back to the Google Sheet
    work_sheet.addNewRowData(new_values=webpage.valuesToInsertList())
