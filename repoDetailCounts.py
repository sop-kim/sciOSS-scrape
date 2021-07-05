import stscraper as scraper
import threading
import pandas as pd
import time

class repoMethod(scraper.GitHubAPI):
    
    @scraper.api_filter(lambda issue: 'pull_request' not in issue)
    @scraper.api('repos/%s/issues', paginate=True, state='closed')
    def repo_closed_issues(self, repo_slug):
        """Get repository issues (not including pull requests)"""
        # https://developer.github.com/v3/issues/#list-issues-for-a-repository
        return repo_slug
    def repo_pulls_count(self, repo_slug,pull_state):
        """return the result of pull requests"""
        #https://developer.github.com/v3/pulls/#list-pull-requests
        url ='repos/'+repo_slug+'/pulls'
        repopulls= self.request(url, paginate=True,state=pull_state)
        return repopulls

    def repo_contributor_count(self, repo_slug):
        """return the result of pull requests"""
        #https://developer.github.com/v3/pulls/#list-pull-requests
        url ='repos/'+repo_slug+'/contributors'
        repocontr= self.request(url, paginate=True)
        return repocontr

    def repo_commits_count(self, repo_slug):
        """return the result of pull requests"""
        #https://developer.github.com/v3/pulls/#list-pull-requests
        url ='repos/'+repo_slug+'/commits'
        repocontr= self.request(url, paginate=True)
        return repocontr
    

def saveData(saveFilePath,dataList):   
    Mychart = pd.DataFrame(dataList)
    writer = pd.ExcelWriter(saveFilePath, engine='xlsxwriter')
    Mychart.to_excel(writer)
    writer.save()
    print("spreadsheet saved at :"+saveFilePath)


def scrapingForDetailCounts(threadName,tokens,inputSpreadsheet,outputSpeadsheet):
    gh_api =repoMethod(tokens)
    detailList ={"SearchKeyword":[],"IsOrgRepo":[],"OwnerName":[],"RepoName":[],"RepoSlug":[],"Language":[],"StarsCount":[],"ForksCount":[],
                "Description":[],"CreatedAt":[],"PushedAt":[],"IsFork":[],
                'Topics':[],'MergedPullRequestsCount':[],'ContributorsCount':[]}

    df = pd.read_excel(inputSpreadsheet,sheet_name=0)
    rawList = df.to_dict(orient='records')
    indexOverall=0

    for element in rawList:
        start_time=time.time()
        print(str(threadName)+" : "+str(indexOverall))
        searchKeyword = str(element['SearchKeyword'])
        IsOrgRepo = str(element['IsOrgRepo'])
        OwnerName=str(element['OwnerName'])
        RepoName= str(element['RepoName'])
        RepoSlug=str(element['RepoSlug'])
        Language= str(element['Language'])
        StarsCount= str(element['StarsCount'])
        ForksCount= str(element['ForksCount'])
        Description= str(element['Description'])
        CreatedAt= str(element['CreatedAt'])
        PushedAt= str(element['PushedAt'])
        IsFork= str(element['IsFork'])

        detailList['SearchKeyword'].append(searchKeyword)
        detailList['IsOrgRepo'].append(IsOrgRepo)
        detailList['OwnerName'].append(OwnerName)
        detailList['RepoName'].append(RepoName)
        detailList['RepoSlug'].append(RepoSlug)
        detailList['Language'].append(Language)
        detailList['StarsCount'].append(StarsCount)
        detailList['ForksCount'].append(ForksCount)
        detailList['Description'].append(Description)
        detailList['CreatedAt'].append(CreatedAt)
        detailList['PushedAt'].append(PushedAt)
        detailList['IsFork'].append(IsFork)

        try:
            myctb=gh_api.repo_contributor_count(RepoSlug)
            ctbcount=pd.DataFrame(myctb).shape[0]
            mergedpulls = gh_api.repo_pulls_count(RepoSlug,pull_state="merged")
            mergedcount =pd.DataFrame(mergedpulls).shape[0]
            
            detailList['Topics'].append(gh_api.repo_topics(RepoSlug))
            detailList['MergedPullRequestsCount'].append(mergedcount)
            detailList['ContributorsCount'].append(ctbcount)
        except:
            print("not found")
            detailList['Topics'].append("REPO NOT FOUND")
            detailList['MergedPullRequestsCount'].append("REPO NOT FOUND")
            detailList['ContributorsCount'].append("REPO NOT FOUND")

        end_time=time.time()
        times=round(end_time-start_time,2)
        print('total scraping time is{}s'.format(times))
        indexOverall+=1

    saveData(outputSpeadsheet,detailList)

if __name__ == '__main__':
    #myGithubTokens="my github tokens, separeted by ','"
    myGithubTokens= ''
    path = r'C:\\Users\\' #modify to path to csv\xlsx file of repos to scrape from

    threads = []
    t1 = threading.Thread(target=scrapingForDetailCounts,
                          args=("thread1",myGithubTokens, 
                          path + 'inputsheet.xlsx',
                          path + 'outputsheet.xlsx'))
    '''
    t2 = threading.Thread(target=scrapingForDetailCounts,
                          args=("thread2",myGithubTokens, 
                          r'C:\\Users\\skim4\\Downloads\\FORCOLAB\\github_scrape\\inputsheet_02.xlsx',
                          r'C:\\Users\\skim4\\Downloads\\FORCOLAB\\github_scrape\\OutputSpreadsheet_02.xlsx'))
    '''
    threads.append(t1)
    #threads.append(t2)

    for t in threads:
        t.setDaemon(True)
        t.start()
    
    for t in threads:
         t.join() 

    print ("all threads completed %s" %time.ctime())