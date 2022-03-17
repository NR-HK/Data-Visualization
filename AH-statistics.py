import requests
import sys
import getopt
from termcolor import colored
from pprint import pprint

startDate = None #default => endDate
endDate = None
lang = 'EN' #SC TC EN, default EN

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
}

# cli
def cli():
    global startDate, endDate, lang
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hl:s:e:")
    except:
        print(colored("Invalid param, please use -h for help.\nExit.", 'red'))
        exit()

    for opt, arg in opts:
        if opt in ['-h']:
            print("Get statistics from HA. Data format: JSON.")
            print("param:")
            print(" -h\thelp.")
            print(" -l [TC|SC|EN]\tlanguage. TC: traditional Chinese. SC: simplified Chinese. EN: English. Default: EN.")
            print(" -s [YYYYMMDD]\tstart date.")
            print(" -e [YYYYMMDD]\tend date.")
            exit()
        elif opt in ['-l']:
            lang = arg
            if lang == "EN" or lang == "TC" or lang == "SC":
                pass
            else:
                print(colored("There must be EN, TC or SC after -l\nExit.", 'red'))
                exit()
        elif opt in ['-s']:
            startDate = arg
        elif opt in ['-e']:
            endDate = arg

cli() #cli

if endDate == None:
    print(colored("End date is required, please use -h for help.\nExit.", 'red'))
    exit()

if startDate == None:
    startDate = endDate

print("lang:", lang)
print("startDate:", startDate)
print("endDate:", endDate)

# get timestamp
JSFile = "https://www.ha.org.hk/opendata/pas_report/Daily_Services_Statistics/Daily_Services_Statistics_LANG.json".replace("LANG", lang)
#print("JSFile:", JSFile)
timestampPayload = {'url': JSFile, 'start': startDate, 'end': endDate}
timestampURL = "https://api.data.gov.hk/v1/historical-archive/list-file-versions"
rTimestamp = requests.get(timestampURL, params = timestampPayload, headers = headers)
rTimestampDict = rTimestamp.json()
#pprint(rTimestampDict)

# get statistics
print(type(rTimestampDict['timestamps']))
dataURL = "https://api.data.gov.hk/v1/historical-archive/get-file"
for eachTimeStamp in enumerate(rTimestampDict['timestamps']):
    print("Downloading json file of timestamp ", eachTimeStamp[1])
    dataPayload = {'url': JSFile, 'time': eachTimeStamp[1]}
    r = requests.get(dataURL, params = dataPayload, headers = headers)
    path = './raw-data/' + lang + '_' + str(eachTimeStamp[1]) + '.json'
    with open(path, 'w') as f:
        f.write(r.text)
