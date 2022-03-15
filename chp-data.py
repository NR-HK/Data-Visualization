# -*- coding: UTF-8 -*-

import requests
from pprint import pprint
from datetime import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

urlDoseApi = 'https://static.data.gov.hk/covid-vaccine/summary.json?_='
urlCaseApi = 'https://chp-dashboard.geodata.gov.hk/covid-19/data/keynum.json?_='

nowTime = datetime.now()
timeStamp = datetime.timestamp(nowTime)
#print(nowTime, timeStamp)

tmpS = ''
urlDose = tmpS.join([urlDoseApi, str(int(timeStamp))])
urlCase = tmpS.join([urlCaseApi, str(int(timeStamp))])
#print(urlDose, urlCase)

# GET request
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
}
# rDose.json() type:dict
rDose = requests.get(urlDose, headers=headers)
rDoseDict = rDose.json()
#pprint(rDose.json())
rCase = requests.get(urlCase, headers=headers)
rCaseDict = rCase.json()
#pprint(rCase.json())
print("Dose:")
for key in rDoseDict:
    print(key, ':', rDoseDict[key])

print("\nCase:")
for key in rCaseDict:
    print(key, ':', rCaseDict[key])

# data struct
totalNum = int(rDoseDict['firstDoseTotal'] / (float(rDoseDict['firstDosePercent'].strip('%')) / 100))
#print("totalNum:", totalNum)
# 未接种人数
undoseNum = totalNum - rDoseDict['firstDoseTotal']
# 仅接种1针
dose1Num = rDoseDict['firstDoseTotal'] - rDoseDict['secondDoseTotal']
# 仅接种2针
dose2Num = rDoseDict['secondDoseTotal'] - rDoseDict['thirdDoseTotal']
# 全部3针接种
dose3Num = rDoseDict['thirdDoseTotal']
# doseN/undoseN：是否接种第N针
doseDataFrame = pd.DataFrame([[u'未接種第1針', u'未接種第2針', u'未接種第3針', undoseNum],
                        [u'接種第1針', u'未接種第2針', u'未接種第3針', dose1Num],
                        [u'接種第1針', u'接種第2針', u'未接種第3針', dose2Num],
                        [u'接種第1針', u'接種第2針', u'接種第3針', dose3Num]])
#print(doseDataFrame)
doseDataFrame.columns = ['ifDose1', 'ifDose2', 'ifDose3', 'number']

# 各具体数据
#print("\nThe first dose\nReceived Dose1: ", rDoseDict['firstDoseTotal'], " undoseNum: ", undoseNum, " sum(Total): ", rDoseDict['firstDoseTotal'] + undoseNum)
#print("\nThe secode dose\nReceived Dose2: ", rDoseDict['secondDoseTotal'], "Only received 1 dose: ", dose1Num, "sum(firstDoseTotal): ", rDoseDict['secondDoseTotal'] + dose1Num)
#print('totalNum: ', totalNum)

# nested pie chart
outer = doseDataFrame.groupby(['ifDose1']).sum()
middle = doseDataFrame.groupby(['ifDose1', 'ifDose2']).sum()
inner = doseDataFrame.groupby(['ifDose1', 'ifDose2', 'ifDose3']).sum()
outerLabels = outer.index.get_level_values(0)
middleLabels = middle.index.get_level_values(1)
innerLabels = inner.index.get_level_values(2) # 3 levels
fig, ax = plt.subplots(figsize=(24,12))
size = 0.1
sizeInner = 0.3
sizeMiddle = 0.6
colorOuter = ['#3F7C85', '#FF5F5D']
colorMiddle = ['#72F2EB', '#00CCBF', '#FF5F5D']
colorInner = ['#A1C7E0', '#0099DD', '#00CCBF', '#FF5F5D']

ax.pie(outer.values.flatten(), radius=1,
       labels = outerLabels,
       labeldistance = 1.2,
       colors = colorOuter,
       autopct = '%1.1f%%',
       pctdistance = 1.1,
       wedgeprops = dict(width = size, edgecolor = 'w'))

ax.pie(middle.values.flatten(), radius=sizeMiddle,
       labels = middleLabels,
       labeldistance = 1.1,
       colors = colorMiddle,
       autopct = '%1.1f%%',
       pctdistance = 0.93,
       wedgeprops = dict(width = size, edgecolor = 'w'))

ax.pie(inner.values.flatten(), radius=sizeInner,
       labels = innerLabels,
       labeldistance = 0.95,
       colors = colorInner,
       autopct = '%1.1f%%',
       pctdistance = 0.4,
       wedgeprops = dict(width = size, edgecolor = 'w'))

ax.set(aspect="equal", title=u'疫苗接種比例圖')
plt.savefig('./res/dose-pie-chart' + str(int(timeStamp)) + '.jpg')
