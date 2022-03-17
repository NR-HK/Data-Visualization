# -*- coding: UTF-8 -*-

import requests
from pprint import pprint
from datetime import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches

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

# nested pie chart for dose ratio
outer = doseDataFrame.groupby(['ifDose1']).sum()
middle = doseDataFrame.groupby(['ifDose1', 'ifDose2']).sum()
inner = doseDataFrame.groupby(['ifDose1', 'ifDose2', 'ifDose3']).sum()
outerLabels = outer.index.get_level_values(0)
middleLabels = middle.index.get_level_values(1)
innerLabels = inner.index.get_level_values(2) # 3 levels
fig, ax = plt.subplots(figsize=(20,12)) #24, 12
size = 0.1
sizeInner = 0.3
sizeMiddle = 0.6
colorOuter = ['#3F7C85', '#FF5F5D']
colorMiddle = ['#72F2EB', '#00CCBF', '#FF5F5D']
colorInner = ['#A1C7E0', '#0099DD', '#00CCBF', '#FF5F5D']

ax.pie(outer.values.flatten(), radius=1,
       labels = outerLabels,
       labeldistance = 1.1, #1.2
       colors = colorOuter,
       autopct = '%1.1f%%',
       pctdistance = 0.95, #1.1
       startangle = 90,
       textprops={'fontsize': 12},
       wedgeprops = dict(width = size, edgecolor = 'w'))

ax.pie(middle.values.flatten(), radius=sizeMiddle,
       labels = middleLabels,
       labeldistance = 1.1,
       colors = colorMiddle,
       autopct = '%1.1f%%',
       pctdistance = 0.93,
       startangle = 90,
       textprops={'fontsize': 12},
       wedgeprops = dict(width = size, edgecolor = 'w'))

ax.pie(inner.values.flatten(), radius=sizeInner,
       labels = innerLabels,
       labeldistance = 0.98,
       colors = colorInner,
       autopct = '%1.1f%%',
       pctdistance = 0.8,
       startangle = 90,
       textprops={'fontsize': 12},
       wedgeprops = dict(width = size, edgecolor = 'w'))

# legend
redPatch = mpatches.Patch(color = '#FF5F5D', label = u'未接種')
greenPatch0 = mpatches.Patch(color = '#3F7C85', label = u'已接種第一針')
greenPatch1 = mpatches.Patch(color = '#72F2EB', label = u'已接種第一、第二針')
greenPatch2 = mpatches.Patch(color = '#00CCBF', label = u'已接種第一針，未接種第二針')
greyPatch = mpatches.Patch(color = '#A1C7E0', label = u'已接種全部三針')
bluePatch = mpatches.Patch(color = '#0099DD', label = u'已接種兩針，未接種第三針')
ax.legend(handles = [redPatch, greenPatch0, greenPatch2, greenPatch1, bluePatch, greyPatch],
          title = u'接種率說明',
          bbox_to_anchor = (1, 1),
          bbox_transform = fig.transFigure,
          loc = 'upper right')

#ax.set(aspect="equal", title=u'疫苗接種比例圖')
ax.set_title(u'疫苗接種比例圖', fontsize = 18)
ax.set(aspect = "equal")
plt.savefig('./res/dose-pie-chart' + str(int(timeStamp)) + '.jpg')

#children age from 3 to 11
childrenFirstDosePct = float(rDoseDict['age3to11FirstDosePercent'].strip('%')) # received 1 dose
childrenSecondDosePct = float(rDoseDict['age3to11SecondDosePercent'].strip('%')) # received 2 doses
children1DosePct = childrenFirstDosePct - childrenSecondDosePct # only received 1 dose
childrenUndosePct = 100 - childrenFirstDosePct - childrenSecondDosePct
print(childrenFirstDosePct, childrenSecondDosePct, children1DosePct, childrenUndosePct)

labelsChildren = [u'徑接種第一針兒童', u'接種二針兒童', u'未接種兒童']
colorChildren =  ['#B7FF63', '#32E89C', '#FF515F']

fracsChildren = [children1DosePct, childrenSecondDosePct, childrenUndosePct]
childrenExplode = (0, 0, 0.2)

fig1, ax1 = plt.subplots()
ax1.pie(fracsChildren,
              labels = labelsChildren,
              colors = colorChildren,
              autopct = '%1.1f%%',
              shadow = True,
              startangle = 90)

ax1.set(aspect="equal", title=u'兒童疫苗接種比例圖')
plt.savefig('./res/children-dose-pie-chart' + str(int(timeStamp)) + '.jpg')
