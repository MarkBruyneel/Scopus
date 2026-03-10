# Example program that allows citation downloads based on a combination of title words
# and/or author words and/or a publication year
# The Scopus API has a limit per week of 20.000 records and 1000 requests a day
# Documentation on searches: https://dev.elsevier.com/sc_search_tips.html
#
# Author: Mark Bruyneel
#
# Date: 2026-03-07
# Version: 1.0
# Created using Python version 3.11

import sys
import os
import glob
import pandas as pd
from scopusconfig import KEY
import requests
import json
from loguru import logger #version 0.7.2
import time

logger.add(r'U:\Werk\financiele bestanden\Scopus\Scopus.log', backtrace=True, diagnose=True, rotation="10 MB", retention="12 months")
@logger.catch()

# Function to exit program when needed
def exit_program():
    print("Exiting the program...")
    sys.exit(0)

def main():
    params = {'httpaccept': 'application/json',
              'apiKey': str(KEY)}
    URL = 'https://api.elsevier.com/content/search/scopus?query='

    choice_search = ''
    while choice_search not in (1, 2):
        choice_search = int(input('Do you wish to search by title words (1) or Title words and author last name (2)?'))
        if choice_search == 1:
            key_word = input('Input words to search for:\n')
            chars = set(' ,:;')
            if any((c in chars) for c in key_word):
                new_search = key_word.replace(' ', '+AND+')
                new_search_edited = '%28'+new_search+'%29'
            else:
                new_search_edited = '%28'+key_word+'%29'
                url_search = URL + 'TITLE' + new_search_edited
        elif choice_search == 2:
            key_word = input('Input words to search for:\n')
            author_Sirname = input('Input the last name of the author:\n')
            chars = set(' ,:;')
            if any((c in chars) for c in key_word):
                new_search = key_word.replace(' ', '+AND+')
                new_search_edited = '%28' + new_search + '%29'
            else:
                new_search_edited = '%28' + key_word + '%29'
            author = 'AUTHLASTNAME%28' + author_Sirname + '%29'
            url_search = URL + 'TITLE' + new_search_edited + '+AND+' + author
        else:
            print('Please provide choice 1 or 2')
    print(url_search)
    response = requests.get(url_search, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        nr = int(data['search-results']['opensearch:totalResults'])
        pages = round(nr / 25)

        print(f'Total search result for {key_word}: {nr}\n')
        print(f'Number of pages: {pages}\n')
        # Save data:
        with open(f'U:\Werk\\financiele bestanden\Scopus\data_test_0.json', 'w') as f:
            f.write(json.dumps(data))

        # Test to add the next 3 pages
        # pages = 25
        while pages > 0 and pages < nr:
            logger.debug(f'Getting the next 25 records ...')
            time.sleep(10)
            params2 = {'httpaccept': 'application/json',
                  'apiKey': str(KEY),
                  'start': str(pages)}
            url_search2 = URL + key_word
            response2 = requests.get(url_search2, params=params2)
            if response2.status_code == 200:
                data2 = json.loads(response2.text)
                # Save data:
                with open(f'U:\Werk\\financiele bestanden\Scopus\data_test{pages}.json', 'w') as f:
                    f.write(json.dumps(data2))
                pages = pages + 25
            else:
                logger.debug('No response. Quitting program ...')
                exit_program()
        logger.debug(f'Finished getting records.')
    else:
        logger.debug('No response. Quitting program ...')
        exit_program()

    # Look for the Json files in the download folder
    dir_path = 'U:\Werk\\financiele bestanden\Scopus'
    # Get list of all files only in the given directory
    scopus_list_json = glob.glob(os.path.join(dir_path, '*.json'))
    scopuslistsize = len(scopus_list_json)
    if scopuslistsize == 0:
        logger.debug(f'Number of Json files to process: {scopuslistsize}')
        exit_program()
    else:
        logger.debug(f'Number of Json files to process: {scopuslistsize}')
        # Create DataFrame to add data to
        Scopus_data = pd.DataFrame()
        # Variable lists
        id_list = []
        title_list = []
        type_list = []
        Pub_dates = []
        doi_list = []
        author_list = []
        issn_list = []
        eissn_list = []
        pages_list = []
        isbn_list = []
        vol_list = []
        source_list = []
        cited_count_list = []
        open_access_status = []
        i = 0
        while i != scopuslistsize:
            logger.debug(f'Copying and adding data from file {i+1}')
            f = open(f'{scopus_list_json[i]}', 'r')
            # returns JSON object as a dicionary
            data = json.load(f)
            size = sys.getsizeof(data)
            if size < 100:
                pass
            else:
                # Iterating through the json list to get specific items
                # First put them in item lists and then create a table by combining them
                nr_of_items = len(data['search-results']['entry'])
                entrynr = 0
                while entrynr < nr_of_items:
                    try:
                        id_list.append(data['search-results']['entry'][entrynr]['dc:identifier'])
                    except:
                        id_list.append(None)
                    try:
                        title_list.append(data['search-results']['entry'][entrynr]['dc:title'])
                    except:
                        title_list.append(None)
                    try:
                        type_list.append(data['search-results']['entry'][entrynr]['subtypeDescription'])
                    except:
                        type_list.append(None)
                    try:
                        Pub_dates.append(data['search-results']['entry'][entrynr]['prism:coverDate'])
                    except:
                        Pub_dates.append(None)
                    try:
                        doi_list.append(data['search-results']['entry'][entrynr]['prism:doi'])
                    except:
                        doi_list.append(None)
                    try:
                        author_list.append(data['search-results']['entry'][entrynr]['dc:creator'])
                    except:
                        author_list.append(None)
                    try:
                        issn_list.append(data['search-results']['entry'][entrynr]['prism:issn'])
                    except:
                        issn_list.append(None)
                    try:
                        eissn_list.append(data['search-results']['entry'][entrynr]['prism:eIssn'])
                    except:
                        eissn_list.append(None)
                    try:
                        pages_list.append(data['search-results']['entry'][entrynr]['prism:pageRange'])
                    except:
                        pages_list.append(None)
                    try:
                        isbn_list.append(data['search-results']['entry'][entrynr]['prism:isbn'][0]['$'])
                    except:
                        isbn_list.append(None)
                    try:
                        vol_list.append(data['search-results']['entry'][entrynr]['prism:volume'])
                    except:
                        vol_list.append(None)
                    try:
                        source_list.append(data['search-results']['entry'][entrynr]['prism:publicationName'])
                    except:
                        source_list.append(None)
                    try:
                        cited_count_list.append(data['search-results']['entry'][entrynr]['citedby-count'])
                    except:
                        cited_count_list.append(None)
                    try:
                        open_access_status.append(data['search-results']['entry'][entrynr]['openaccessFlag'])
                    except:
                        open_access_status.append(None)
                    entrynr += 1
            # Closing file
            f.close()
            i = i + 1
        id_list = {'Scopus_identifier': id_list}
        scopus_table = pd.DataFrame(id_list)
        scopus_table['Open_Access_Status'] = open_access_status
        scopus_table['title'] = title_list
        scopus_table['PublicationType'] = type_list
        scopus_table['PublicationDate'] = Pub_dates
        scopus_table['DOI'] = doi_list
        scopus_table['First_author'] = author_list
        scopus_table['Issn'] = issn_list
        scopus_table['eIssn'] = eissn_list
        scopus_table['ISBN'] = isbn_list
        scopus_table['Pages'] = pages_list
        scopus_table['Volume'] = vol_list
        scopus_table['Source'] = source_list
        scopus_table['CitedCount'] = cited_count_list
        Scopus_data = pd.concat([Scopus_data, scopus_table], ignore_index=True)
        # Drop empty rows from empty json files
        Scopus_data.dropna(subset=['Scopus_identifier'], inplace=True)

        # Dataframe is empty skip the next part
        nr_of_rows = len(Scopus_data)
        if  nr_of_rows == 0:
            logger.debug(f'No resulting data from Scopus!')
        else:
            # Remove some characters from fields
            Scopus_data['Scopus_identifier'] = Scopus_data['Scopus_identifier'].str.replace('SCOPUS_ID:', '')
            Scopus_data['ISBN'] = Scopus_data['ISBN'].str.replace('[', '')
            Scopus_data['ISBN'] = Scopus_data['ISBN'].str.replace(']', '')
            # Export result as a CSV file with the date of the Python run
            Scopus_data.to_csv(f'{dir_path}\Scopus_publications.csv', encoding='utf-8')
            # Delete the json files that were processed
            files_json = glob.glob(f'{dir_path}/*.json')
            for j in files_json:
                os.remove(j)
            logger.debug(f'Finished processing records. Exiting program.')
if __name__ == "__main__":
    main()
