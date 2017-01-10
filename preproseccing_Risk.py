
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import cPickle

np.set_printoptions(precision=4)
np.seterr(invalid='ignore')

# get_ipython().magic(u'pylab inline')
# pylab.rcParams['figure.figsize'] = (10, 6)

def dateconvert(df, col):
    df[col] = pd.to_datetime(df[col], format="%d-%b-%Y")
    df.sort_values(by=col)
    return df


def getdate(v):
    v = v.sort_values(by=['AU_TIME'])
    start = v[v.new == 1].index[0]
    end_idx = v[v.done == 1].index[-1]
    return v.loc[start:end_idx], start, end_idx


def modelSlice(v_, start, end_idx, duration):
    dt = [datetime.datetime.utcfromtimestamp(x.tolist() / 1e9) for x in v_.AU_TIME.values]
    Model_end = dt[0] + datetime.timedelta(days=duration)
    # step = datetime.timedelta(days=1)

    # dates = []
    for i, x in enumerate(dt):
        if x > Model_end:
            # print len(v_.iloc[:i])
            return v_.iloc[:i]
            break


def featuresFunc(v):
    defects, closed, sps, change, mean_sp, std_sp, events, news = None, None, None, ['None'], None, None, None, None
    try:
        events = len(v)
        v = v.sort_values(by=['AU_TIME'])
    except:
        return defects, closed, sps, change, mean_sp, std_sp, events, news

    if v.new.dropna().sum() < 1:
        return None
    else:
        defects = v.opened.dropna().sum()
        closed = v.Closed.dropna().sum()
        if v["Story Points"].dropna().sum() != 0:
            try:
                v["AP_OLD_VALUE"] = v["AP_OLD_VALUE"].fillna('0')
                change = [int(x[1].AP_NEW_VALUE) - int(x[1].AP_OLD_VALUE) for x in v.iterrows() if
                          x[1]["Story Points"] == 1]
                sp_events = len(change)
                mean_sp, std_sp = np.mean(change), np.std(change)
                sps = np.sum([abs(x) for x in change])
            except:
                pass
            return defects, closed, sps, change, mean_sp, std_sp, events, v.new.dropna().sum(), sp_events


def convert(s):
    ls = s.split()
    d = {'day': 1, 'week': 7, 'month': 30, 'year': 360}
    for k, v in d.items():
        if ls[1].startswith(k):
            return int(ls[0]) * v


def get_label(k, df):
    try:
        x = df.label[df.RBI_FEATURE_ID_x == k].values[0]
    except:
        x = None
        pass
    return x


# getdata
# df           = pd.read_csv("../../../OneDrive - Hewlett Packard Enterprise/featuresRiskEvaluator/sql_data/features_backlog.csv")#, dtype={"RBI_FEATURE_ID":int, "RBI_ENTITY_ID":int})
features = pd.read_csv(
    "../../../OneDrive - Hewlett Packard Enterprise/featuresRiskEvaluator/sql_data/features_HISTORY.csv")
df1 = pd.read_csv("../../../OneDrive - Hewlett Packard Enterprise/featuresRiskEvaluator/sql_data/DEFECTs_HISTORY.csv")
df2 = pd.read_csv(
    "../../../OneDrive - Hewlett Packard Enterprise/featuresRiskEvaluator/sql_data/DEFECTs_status_done.csv")

df3 = pd.read_csv("../../../OneDrive - Hewlett Packard Enterprise/featuresRiskEvaluator/sql_data/US_HISTORY.csv")
df4 = pd.read_csv(
    "../../../OneDrive - Hewlett Packard Enterprise/featuresRiskEvaluator/sql_data/US_status_done_or_progress.csv")
BL = pd.read_csv("/Users/talb/git/gitwork/data/result.csv")

df3[df3.AP_PROPERTY_NAME == 'Status']
df3['new'] = np.where((df3.AP_NEW_VALUE == "In Progress") & (df3.AP_OLD_VALUE == "New"), 1, 0)
df4['new'] = np.where((df4.AP_NEW_VALUE == "In Progress") & (df4.AP_OLD_VALUE == "New"), 1, 0)
# print df3.new.sum()

featuresClosed = features[
    (features.AP_PROPERTY_NAME == 'Status') & (features.AP_NEW_VALUE == 'Done') & (features.AP_OLD_VALUE != 'Done')]

# x = df3[(df3.AP_NEW_VALUE=="In Progress") & (df3.AP_OLD_VALUE=="New")]
# x.loc[:,'new']=1
# df3.where[(df3.AP_NEW_VALUE=="In Progress") & (df3.AP_OLD_VALUE=="New")]
df3['new'] = np.where((df3.AP_NEW_VALUE == "In Progress") & (df3.AP_OLD_VALUE == "New"), 1, 0)
df4['new'] = np.where((df4.AP_NEW_VALUE == "In Progress") & (df4.AP_OLD_VALUE == "New"), 1, 0)
df3['done'] = np.where((df3.AP_NEW_VALUE == "Done") & (df3.AP_PROPERTY_NAME == "Status"), 1, 0)
df4['done'] = np.where((df4.AP_NEW_VALUE == "Done") & (df4.AP_PROPERTY_NAME == "Status"), 1, 0)

df1 = dateconvert(df1, "AU_TIME")
df3 = dateconvert(df3, "AU_TIME")
features = dateconvert(features, "AU_TIME")

# concat

frames = [df1, df3]
data = pd.concat(frames, )
data.new.describe()

# pattern

list_of_values = ['Feature', 'Story Points']
pattern = '|'.join(list_of_values)

# print pattern
# df.a.str.contains(pattern)
# y = df[df['AP_PROPERTY_NAME'].str.contains(pattern)]
# df = df1[df1.AP_PROPERTY_NAME==[]


# preprocessing:

DefectOpened = df1[
    (df1.AP_PROPERTY_NAME == 'Feature') & (df1.AP_OLD_VALUE.isnull() == True) & (df1.AP_NEW_VALUE.notnull() == True)]
df1['opened'] = np.where(
    (df1.AP_PROPERTY_NAME == 'Feature') & (df1.AP_OLD_VALUE.isnull() == True) & (df1.AP_NEW_VALUE.notnull() == True), 1,
    0)
# DefectOpened.loc[:,'opened']=1
df1['Closed'] = np.where(
    (df1.AP_PROPERTY_NAME == 'Status') & (df1.AP_OLD_VALUE != 'Done') & (df1.AP_NEW_VALUE == 'Done'), 1, 0)

# DefectClosed = df2[(df2.AP_PROPERTY_NAME == 'Status') & (df2.AP_NEW_VALUE == 'Done') & (df2.AP_OLD_VALUE != 'Done')]
# DefectClosed.loc[:,'closed']=1
# sp = df3[(df3.AP_PROPERTY_NAME == 'Story Points')]
df3['Story Points'] = np.where(df3.AP_PROPERTY_NAME == 'Story Points', 1, 0)

# df3['changedSP'] = [int(x[1].AP_NEW_VALUE)- int(x[1].AP_OLD_VALUE) for x in df3.iterrows() if x[1]["Story Points"]==1]
# df3.AP_OLD_VALUE.describe()

df3['Story Points'].fillna(0)
# df3['changedSP'] = [int(x[1].AP_NEW_VALUE)- int(x[1].AP_OLD_VALUE) for x in df3.iterrows() if x[1]['Story Points']==1]

# concat
frames = [df1, df3]
result = pd.concat(frames, )

sp = pd.concat(frames, )

# merge
merged = result.merge(BL , left_on='RBI_FEATURE_ID', right_on='RBI_ENTITY_ID', how='right')
merged = merged.drop_duplicates()

# groupby:

result.drop_duplicates()
# result = result[result.RBI_FEATURE_ID != 0]
merged = merged[merged.RBI_FEATURE_ID_x != 0]

# grouped = result.groupby(['RBI_FEATURE_ID'])
grouped = merged.groupby(['RBI_FEATURE_ID_x'])

with open('groupedData.pkl','wb') as fp:
    cPickle.dump(grouped,fp)
