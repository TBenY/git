# coding: utf-8

import numpy as np
import pandas as pd
import datetime
import cPickle

np.set_printoptions(precision=4)
np.seterr(invalid='ignore')

# get_ipython().magic(u'pylab inline')
# pylab.rcParams['figure.figsize'] = (10, 6)


def days_hours_minutes(td):
    # type: (object) -> object
    return td.days, td.seconds//3600, (td.seconds//60)%60


def dateconvert(df, col):
    df[col] = pd.to_datetime(df[col], format="%d-%b-%Y")
    df.sort_values(by=col)
    return df


def getdate(v):
    v = v.sort_values(by=['AU_TIME'])

    try:
        start = v[v.new == 1].index[0]
        end_idx = v[v.done == 1].index[-1]
        return v.loc[start:end_idx], start, end_idx
    except:
        pass
        return np.array([None, None, None])


def modelSlice(v_, dt, duration):
    try:
        Model_end = dt[0] + datetime.timedelta(days=duration)
    # step = datetime.timedelta(days=1)
    except:
        return None
        pass
    # dates = []
    for i, x in enumerate(dt):
        if x > Model_end:
            # print len(v_.iloc[:i])
            return v_.iloc[:i]
            break


def featuresFunc(v):
    defects, closed, sps, change, mean_sp, std_sp, events, news, sp_events = None, None, None, None, None, None, None, None, None
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
                change = np.array([int(x[1].AP_NEW_VALUE) - int(x[1].AP_OLD_VALUE) for x in v.iterrows() if
                          x[1]["Story Points"] == 1])
                sp_events = len(change)
                mean_sp, std_sp = np.mean(change), np.std(change)
                sps = np.sum([abs(x) for x in change])
                change = np.sum(x)
                return int(defects), int(closed), int(sps), int(change), mean_sp, std_sp, int(events), v.new.dropna().sum(), int(sp_events)
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


with open('groupedData.pkl','rb') as fp:
    grouped=cPickle.load(fp)

duration = 14
featuresDict, durationDict = {}, {}
# columns=['defects', 'closed', 'sps', 'change', 'mean_sp', 'std_sp', 'events', 'news', 'sp_events', 'duration', 'label', 'feature']
df = pd.DataFrame(columns=['defects', 'closed', 'sps', 'change', 'mean_sp', 'std_sp', 'events', 'news', 'sp_events', 'duration', 'label', 'feature'])
print ['#features', len(grouped)]
for k, v in grouped:
    print 'feature', k

    try:
        v_, start_idx, end_idx = getdate(v)
        if None == start_idx:
            continue
        else:
            label = v_.label.values[0]
            dt = [datetime.datetime.utcfromtimestamp(x.tolist() / 1e9) for x in v_.AU_TIME.values]

            Model_end = dt[0] + datetime.timedelta(days=duration)
            data_end = dt[0] + datetime.timedelta(days=30)
            # data_end = dt[-1] - datetime.timedelta(days=duration)
            data_end = v[1 == v.done].AU_TIME.values[-1]
            data_end = datetime.datetime.utcfromtimestamp(data_end.tolist() / 1e9)


            modelData = modelSlice(v_, dt, duration)
            # end_of_feature = v[v.index==end_idx].AU_TIME
            # start_of_feature = v[v.index==start_idx].AU_TIME + datetime.timedelta(days=duration)
            #     print result.label[result.RBI_FEATURE_ID_x==v.RBI_FEATURE_ID.tolist()[0]]

            # durationDict[duration] = []
            # while Model_end <= data_end:
            diff = days_hours_minutes(data_end- Model_end)[0]
            for i, duration in enumerate(range(14, diff-1, 14)):
                #     x = start_of_feature + datetime.timedelta(days=duration)
                # duration += x

                print 'duration : ', duration

                model_data = modelSlice(v_, dt, duration)
                f = featuresFunc(model_data)
                if model_data is not None:
                    if None != f and len(model_data) > 1:
                        f = list(f)
                        featuresDict[int(k), label] = f
                        f.append(int(duration))
                        f.append(int(label))
                        f.append(int(k))
                        print(pd.Series(f))
                        # df.loc[-1] = f
                        df.loc[str(k) + ' ' + str(duration)] = f
                        # df.loc[len(df.index)] =pd.DataFrame(f)
                        # df_ = pd.DataFrame(f, columns=list(columns))
                        # df.loc[(int(k), label)] = pd.Series({col: x for col, x in zip(columns, f)})
                        # df.loc[int(k), label] = df_
                        # if duration not in durationDict.keys():
                        #     durationDict[duration] = []
                        #     durationDict[duration].append({(int(k), label): f})
                        # else:
                            # durationDict[duration] = durationDict[duration].append({(int(k), label): f})

                # print len(max(durationDict.values()))
    except:
        pass


    df.to_csv('/Users/talb/git/gitwork/data/risk_features.csv')
    print df
with open('durationDict.pkl', 'wb') as fp:
    cPickle.dump(durationDict, fp)



