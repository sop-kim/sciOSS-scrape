import os,time
import pandas as pd

def mergeAndDropDuplicates(dirToMerge,outputFilePath):
    """ dirToMerge (str): the path of the folder that containes all the spreadsheets that need to be merged 
        outputFilePath (str): the path and file name of the output merged result
    """
    start_time=time.time()

    DFs = []
    for root, dirs,files in os.walk(dirToMerge): 
        for file in files:
            file_path=os.path.join(root,file)  
            df = pd.read_excel(file_path) 
            DFs.append(df)

    mergedDfs = pd.concat(DFs)  #sort='False'
    end_time=time.time()
    times=round(end_time-start_time,2)

    print(' merged complete, used {} secs '.format(times))
    print(' now dropping duplicated items by "RepoSlug"')

    filteredList = mergedDfs.drop_duplicates(['RepoSlug'])
    DataChart = pd.DataFrame(filteredList)
    writer = pd.ExcelWriter(outputFilePath,engine='xlsxwriter')
    DataChart.to_excel(writer)
    writer.save()
    print(" new speadsheet saved at : "+outputFilePath)

if __name__ == '__main__':
    #setting the path of the folder that containes all the spreadsheets that need to be merged 

    dirToMerge = r'C:\\Users\\' 
    outputFilePath='C:\\Users\\Merged_06.xlsx'
    mergeAndDropDuplicates(dirToMerge,outputFilePath)
