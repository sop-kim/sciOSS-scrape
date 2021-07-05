# sciOSS-scrape
clone of RendalPhoenix/miscellaneous_data_scraping with extended features.

## Usage
Install the dependencies, then run the scripts you want using github access tokens.

### githubSearch.py
Search for scientific OSS repos based on search keywords and advanced criteria as well as regex matching.
Modify the appropriate filepaths where indicated, including the path to text files containing false positive keywords. 

### mergeAndDropDuplicates.py
Merge spreadsheets (results from githubSearch.py) into single spreadsheet with duplicate repos removed.
Modify the appropriate filepaths where indicated.

### repoDetailCounts.py
Scrape further details of repos in input spreadsheet. 
Modify the appropriate filepaths where indicated. 
