import re
import os
import requests

class objOneWebPage:
    def __init__(self, cache, url, language='English', verbose=False):
        self.cache_folder = cache
        self.input_url = url
        self.article_language = language
        self.cache_available = False  # Will set to true if we have a cached version of this URL
        self.cache_uuid = self.url_uuid(from_str=self.input_url, to_style='uuid', verbose=verbose)

        # Is there a cache file available?
        self.cache_full_file_name = f"{self.cache_folder}{self.cache_uuid}.html"
        self.cache_available = self.cache_check_local(verbose=verbose)

        self.column_values = []  # This is dangerous as we can't specify the column names, just get the order right

        print(f"objOneWebPage initialized:\n\tCache folder: {self.cache_folder}\n\tURL: {self.input_url}\n\tuuid: {self.cache_uuid}") if verbose else None
        print(f"\tLocal cache available: {self.cache_available}")

        # now get the content itself - from the source, or from the cache if it exists
        self.html = self.get_content(force_reread=False, verbose=verbose)
        print(f"HTML has been read:")
        self.article_tag_title = self.get_tag(tag='title')
        self.article_description = self.get_tag(tag='description')
        self.article_contents = self.get_tag(tag='contents')
        self.article_keywords = self.get_tag(tag='keywords')

        self.article_author = self.get_tag(tag='author')
        self.article_date_creation = self.get_tag(tag='creation_date')

        print(f"Title: {self.article_tag_title}") if verbose else None
        print(f"Description: {self.article_description}") if verbose else None
        print(f"Keywords: {self.article_keywords}") if verbose else None
        print(f"Author: {self.article_author}") if verbose else None
        print(f"Date - creation: {self.article_date_creation}") if verbose else None
        print(f"Description: {self.article_description}") if verbose else None
        print(f"Contents (character count): {len(self.article_contents)}") if verbose else None
        print(f"Contents (400): {self.article_contents}...") if verbose else None

        # Put this in a list of lists in the correct order of the columns after the Url
        # This is dangerous as we can't specify the column names, just get the order right

        self.column_values = [[self.article_tag_title,
                               self.article_description,
                               self.article_language,
                               self.article_keywords,
                               self.article_author,
                               self.article_date_creation,
                               len(self.article_contents),
                               self.article_contents
                               ]]
    def get_content(self, force_reread=False, verbose=False):
        if (force_reread or (self.cache_available == False)):
            print("\tRead the URL")
            page = requests.get(self.input_url)
            # Write this to the cache
            with open(self.cache_full_file_name, 'w') as file:
                # Write the contents of the variable to the file
                file.write(page.text)
                print(f"Wrote the contents of the web page to:\n\t{self.cache_full_file_name}")

            return page.text
        else:
            with open(self.cache_full_file_name, 'r') as file:
                # Read the contents of the file into a variable
                print("\tRead the URL from local cache file")
                html_ret = file.read()
            return html_ret

    def get_tag(self, tag, verbose=False):
        if tag == 'title':
            # Start easy, just regex on:
            # "articleTitle":"After fixing El Salvador’s gang problem, Nayib Bukele sets his sights on the economy","articleLength":994
            pattern = r'articleTitle":"([^"]+)","articleLength'
        elif tag == 'description':
            pattern = r'description":"(.*?)","articleBody'
        elif tag == 'contents':
            pattern = r'articleBody":"(.*?)","keywords'
        elif tag == 'keywords':
            pattern = r'keywords":\[(.*?)\],'
        elif tag == 'author':
            pattern = r'author":\[(.*?)\],'
        elif tag == 'creation_date':
            pattern = r'creationDate":"([^"]*?)"'

        matches = re.findall(pattern, self.html)
        return matches[0]

    def cache_check_local(self, verbose=False):
        # See if a local file exists

        print(f"Does local file exist? (cache_check_local)\n\t{self.cache_full_file_name}")
        if os.path.exists(self.cache_full_file_name):
            return True
        else:
            return False

    def url_uuid(self, from_str, to_style, verbose=False):
        # Maybe this only needs to be from URL to uuid
        return_uuid = from_str.lower()
        return_uuid = re.sub(r'[^a-z0-9]', '', return_uuid)
        if len(return_uuid) > 250:
            print("ERROR 4412 (function url_uuid): return_uuid is too long a file name")
        else:
            print(f"PASS 4412 (function url_uuid): return_uuid of length {len(return_uuid)}") if verbose else None
        return return_uuid

    def __repr__(self):
        return f"\nWeb page scraped:\n\tTitle: {self.article_tag_title}\n\tDesc: {self.article_description}\n\tContent characters: {len(self.article_contents)}"

    def valuesToInsertList(self):
        return self.column_values
    def scrapeSuccess(self):
        # Make sure we have data in all the key columns
        success = True
        error_string = "Errors:\n"
        if len(self.article_tag_title) < 3:
            success = False
            error_string += "Title is a problem"
        if len(self.article_description) < 3:
            success = False
            error_string += "Description is a problem"
        if len(self.article_keywords) < 3:
            success = False
            error_string += "Keywords are a problem"
        if len(self.article_author) < 3:
            success = False
            error_string += "Author is a problem"
        if len(self.article_date_creation) < 3:
            success = False
            error_string += "Creation date is a problem"

        if not success:
            print(error_string)

        return success



