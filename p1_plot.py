import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import statsmodels.api as sm

dfq3 = pd.read_csv('Problem1.csv')

# plt.scatter(dfq3['meanMedian'], dfq3['TOTAL_EXPENDITURE'])
g = sns.jointplot(data=dfq3, x='meanMedian',y='TOTAL_EXPENDITURE', kind="reg")

model = sm.OLS(dfq3.TOTAL_EXPENDITURE, dfq3.meanMedian)
dfq3['resid'] = model.fit().resid

head = dfq3.sort_values(by=['resid'], ascending=[False]).head(5)

def ann(row):
    r = row[1]
    x = -145 * (0.98-(r["meanMedian"]/1e4 - 5) / 8)
    y = r["TOTAL_EXPENDITURE"]
    plt.text(x, y, r['STATE'], horizontalalignment='left', size='medium', color='red', weight='semibold')

for row in head.iterrows():
    ann(row)
    
plt.savefig('Problem1.jpeg')

dfq5 = pd.read_csv('Problem2_01.csv')
# plt.scatter(dfq5['meanCleanExpenditure'], dfq5['meanMedian'])
g = sns.jointplot(data=dfq5, x='meanCleanExpenditure',y='meanMedian', kind="reg")

model = sm.OLS(dfq5.meanCleanExpenditure, dfq5.meanMedian)
dfq5['resid'] = model.fit().resid

head = dfq5.sort_values(by=['resid'], ascending=[False]).head(5)

def ann(row):
    r = row[1]
    x = -82 * (1-(r["meanCleanExpenditure"]/1e7) / 6)
    y = r["meanMedian"]
    plt.text(x, y, r['state'], horizontalalignment='left', size='medium', color='red', weight='semibold')

for row in head.iterrows():
    ann(row)
    
plt.savefig('Problem2_01.jpeg')

dfq6 = pd.read_csv('Problem2_02.csv')
# plt.scatter(dfq6['meanExpenditureIncreaseRate'], dfq6['meanMedian'])
g = sns.jointplot(data=dfq6, x='meanExpenditureIncreaseRate',y='meanMedian', kind="reg")

model = sm.OLS(dfq6.meanExpenditureIncreaseRate, dfq6.meanMedian)
dfq6['resid'] = model.fit().resid

head = dfq6.sort_values(by=['resid'], ascending=[False]).head(5)
# outliers = dfq6.loc[(dfq6['meanExpenditureIncreaseRate'] > 0.050) & (dfq6['meanMedian'] < 8e4)]
p1pre = dfq6.loc[(dfq6['state'] == 'New York') | (dfq6['state'] == 'California') | (dfq6['state'] == 'Texas')]

def ann(row, flag):
    r = row[1]
    x = -82 * (1-(r["meanExpenditureIncreaseRate"]*100 - 2.5) / 3.5)
    y = r["meanMedian"]
    if flag == 1:
        plt.text(x, y, r['state'], horizontalalignment='left', size='medium', color='black', weight='semibold')
    else:
        plt.text(x, y, r['state'], horizontalalignment='left', size='medium', color='red', weight='semibold')


for row in head.iterrows():
    ann(row, 1)
for row in p1pre.iterrows():
    ann(row, 0)
    
plt.savefig('Problem2_02.jpeg')

# drop the five states above
dfq6_dropped = dfq6.sort_values(by=['resid'], ascending=[False]).iloc[5: , :]
g = sns.jointplot(data=dfq6_dropped, x='meanExpenditureIncreaseRate',y='meanMedian', kind="reg")

p1pre = dfq6.loc[(dfq6['state'] == 'New York') | (dfq6['state'] == 'California') | (dfq6['state'] == 'Texas')]

def ann(row, flag):
    r = row[1]
    x = -82 * (1-(r["meanExpenditureIncreaseRate"]*100 - 2.5) / 3.5)
    y = r["meanMedian"]
    if flag == 1:
        plt.text(x, y, r['state'], horizontalalignment='left', size='medium', color='black', weight='semibold')
    else:
        plt.text(x, y, r['state'], horizontalalignment='left', size='medium', color='red', weight='semibold')


for row in p1pre.iterrows():
    ann(row, 0)
    
plt.savefig('Problem2_03.jpeg')

dfq9 = pd.read_csv('Problem3_01.csv')

g = sns.jointplot(data=dfq9, x='meanMedian',y='totalExpenditure', kind="reg")

model = sm.OLS(dfq9.totalExpenditure, dfq9.meanMedian)
dfq9['resid'] = model.fit().resid

head = dfq9.sort_values(by=['resid'], ascending=[False]).head(1)
tail = dfq9.sort_values(by=['resid'], ascending=[False]).tail(1)

def ann(row):
    r = row[1]
    x = -107 * (1-(r["meanMedian"]/1e4 - 2) / 16)
    y = r["totalExpenditure"] + 1000
    plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='red', weight='semibold')

for row in head.iterrows():
    ann(row)
for row in tail.iterrows():
    ann(row)
    
plt.savefig('Problem3_01.jpeg')

dfq10 = pd.read_csv('Problem3_02.csv')

g = sns.jointplot(data=dfq10, x='meanCleanExpenditure',y='meanMedian', kind="reg")

model = sm.OLS(dfq10.meanCleanExpenditure, dfq10.meanMedian)
dfq10['resid'] = model.fit().resid

head = dfq10.sort_values(by=['resid'], ascending=[False]).head(1)
tail = dfq10.sort_values(by=['resid'], ascending=[False]).tail(1)

def ann(row):
    r = row[1]
    x = -69 * (1-(r["meanCleanExpenditure"]/1e4 - 2) / 20)
    y = r["meanMedian"] + 1000
    plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='red', weight='semibold')

for row in head.iterrows():
    ann(row)
for row in tail.iterrows():
    ann(row)
    
plt.savefig('Problem3_02.jpeg')

dfq11 = pd.read_csv('Problem3_03.csv')

g = sns.jointplot(data=dfq11, x='meanExpenditureIncreaseRate',y='meanMedian', kind="reg")

model = sm.OLS(dfq11.meanExpenditureIncreaseRate, dfq11.meanMedian)
dfq11['resid'] = model.fit().resid

head = dfq11.sort_values(by=['resid'], ascending=[False]).head(5)
pre = dfq11.loc[(dfq11['county'] == 'Comanche County')]

def ann(row, flag):
    r = row[1]
    x = -70 * (1-(r["meanExpenditureIncreaseRate"]) / 6)
    y = r["meanMedian"]
    if r['county'] == 'Tulsa County':
        y = y + 8000
        plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='black', weight='semibold')
    elif flag == 1:
        y = y - 8000
        plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='black', weight='semibold')
    else:
        y = y + 8000
        plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='red', weight='semibold')


for row in head.iterrows():
    ann(row, 1)
for row in pre.iterrows():
    ann(row, 0)
    
plt.savefig('Problem3_03.jpeg')

# drop the five states above
dfq11_dropped = dfq11.sort_values(by=['resid'], ascending=[False]).iloc[5: , :]
g = sns.jointplot(data=dfq11_dropped, x='meanExpenditureIncreaseRate',y='meanMedian', kind="reg")

pre = dfq11.loc[(dfq11['county'] == 'Comanche County')]
def ann(row, flag):
    r = row[1]
    x = -82 * (1-(r["meanExpenditureIncreaseRate"]*100 - 2.5) / 3.5)
    y = r["meanMedian"]
    if flag == 1:
        plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='black', weight='semibold')
    else:
        plt.text(x, y, r['county'], horizontalalignment='left', size='medium', color='red', weight='semibold')


for row in pre.iterrows():
    ann(row, 0)
    
plt.savefig('Problem3_04.jpeg')