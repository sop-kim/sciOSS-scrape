import threading
from time import ctime
from typing import List
import stscraper as scraper
from github import Github
import pandas as pd
import calendar
import time
import re
import base64

#read from files of false positive keywords, separated by newlines
path_descrip= 'C:\\Users\\sciOSS-scrape\\fp_descrip_words.txt' #modify with path to text file
path_readme = 'C:\\Users\\sciOSS-scrape\\fp_readme_words.txt' #modify with path to text file

with open(path_descrip) as wordfile:
    fp_descrip_words = wordfile.read().splitlines()
wordfile.close()
with open(path_readme) as wordfile:
    fp_readme_words = wordfile.read().splitlines()
wordfile.close()


def saveData(saveFilePath,dataList):   
    Mychart = pd.DataFrame(dataList)
    writer = pd.ExcelWriter(saveFilePath, engine='xlsxwriter')
    Mychart.to_excel(writer)
    writer.save()
    print("spreadsheet saved at :"+saveFilePath)

def scraping(token,searchKeyword,advancedQuery,outputFolder,saveFileIndex=''):
    """ token (str): github token for API requests
        searchKeyword (str): keywords used for github search as well as the output speadsheet name
        advancedQuery (str): additional filtering conditions for github search, 
                            since the returned result for github search is max 1000 repositories per request,
                              it is better to set a time window for each request
        outputFolder (str): the folder path for the output spreadsheets
        saveFileIndex (str): used for indexing the speadsheet
    """
    indexOverall = 0
    g = Github(token,per_page=560,retry=8)
    SearchList ={"SearchKeyword":[],"IsOrgRepo":[],"OwnerName":[],"RepoName":[],"RepoSlug":[],
                "Language":[],"StarsCount":[],"ForksCount":[], "Description":[], "Readme":[],
                "CreatedAt":[],"PushedAt":[],"IsFork":[]}
    #read the docs at https://docs.github.com/en/rest/reference/search 
    #for proper formating of the searchKeyword and advancedQuery
    repositories = g.search_repositories(query=searchKeyword+advancedQuery)

    for rItems in repositories:
        start_time=time.time()
        search_rate_limit = g.get_rate_limit().search
        remaining_limit = search_rate_limit.remaining
        print("remaining limit is :"+str(remaining_limit))
        print(search_rate_limit)
        if remaining_limit>2: 
            try:
                encoded_readme = rItems.get_readme()
            except:
                print("no readme found")
                continue
        
            base64_message = encoded_readme.content
            base64_bytes = base64_message.encode()
            message_bytes = base64.b64decode(base64_bytes)
            readme = message_bytes.decode()

            if criteria(rItems, readme) == False: 
                continue
            SearchList["SearchKeyword"].append(searchKeyword)
            SearchList["IsOrgRepo"].append(rItems.owner.type)
            SearchList["OwnerName"].append(rItems.owner.login)
            SearchList["RepoName"].append(rItems.name)
            SearchList["RepoSlug"].append(rItems.full_name)
            SearchList["Language"].append(rItems.language)
            SearchList["StarsCount"].append(rItems.stargazers_count)
            SearchList["ForksCount"].append(rItems.forks_count)
            SearchList["Description"].append(rItems.description)
            SearchList["Readme"].append(readme)
            SearchList["CreatedAt"].append(rItems.created_at)
            SearchList["PushedAt"].append(rItems.pushed_at)
            SearchList["IsFork"].append(rItems.fork)
            indexOverall+=1
        else:
            reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
            sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5  #  wait 5 more seconds 
            time.sleep(sleep_time)
        end_time=time.time()
        times=round(end_time-start_time,2)
        print('total scraping time is{}s'.format(times))
        print(indexOverall)

    saveData(outputFolder+searchKeyword+saveFileIndex+'.xlsx',SearchList)
    print("scraping completed for "+searchKeyword+saveFileIndex)

#==============================================================================
def criteria(repo, readme):
    #check repo ownership, number of contributors
    if (repo.owner.type != 'Organization') or (repo.get_contributors().totalCount < 3):
        return False
    else:
        return expressionCheck(readme, repo.description) #call expressionCheck on readme and description

    
def expressionCheck(readme, descrip):
    if descrip==None:
        print("no description found")
        return False
    #filter out repos with false positive key words
    fp_descrip = re.compile(r'(?i)\b(%s)\b' % '|'.join(fp_descrip_words))
    fp_readme = re.compile(r'(?i)\b(%s)\b' % '|'.join(fp_readme_words))
    
    if fp_descrip.search(descrip, re.IGNORECASE) or fp_readme.search(readme, re.IGNORECASE):
        return False

    return True 



if __name__ == '__main__':

    threads = []
    qualifiers='in:title in:readme in:description pushed:>=2020-01-01 -fork:only'
    token1, token2 = '' #modify with your github tokens
    saveToPath = 'C:\\Users\\' #modify to path of your choice

    t1 = threading.Thread(target=scraping,args=(token1, 
                                                'molecular',
                                                qualifiers,
                                                saveToPath,
                                                '_01'))
    
    t2 = threading.Thread(target=scraping,args=(token2, 
                                                'research framework',
                                                qualifiers,
                                                saveToPath,
                                                '_01'))
    threads.append(t1)
    threads.append(t2)
    
    for t in threads:
        t.setDaemon(True)
        t.start()
    
    for t in threads:
         t.join() 
    print ("all threads completed %s" %ctime())