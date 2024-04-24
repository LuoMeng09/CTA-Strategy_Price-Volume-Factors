def Net_Values(signal):
    return signal.iloc[-1].sum()/len(signal.columns)

def Sharpe_Ratio(signal,trading_days=256):
    mean = ((signal).diff()).mean() * trading_days
    std = ((signal).diff()).std(ddof=1) * (trading_days ** 0.5)
    return round(mean / std,4)


def Maximum_dd(signal,initial):
    cum_ret = signal
    mdd     = 0
    peak    = cum_ret[0]
    for x in np.array(cum_ret):
        if x > peak:
            peak = x    
        dd = (peak - x) /initial
        if dd > mdd:
            mdd = dd
    return round(mdd*100,4)


def Calmar_ratio(mdd,signal,trading_days=256):
    mean = ((signal).diff()).mean() * trading_days
    mdd=mdd/100
    return round(mean/mdd,4)


def Open_Times(signal,trading_days=256):
    difference=signal.copy()
    difference1=signal.copy()
    difference1[difference1.values==0]=2
    for i in difference.columns:
        difference[i]=difference1[i]-difference1[i].shift(-1)
    difference=difference.shift(1)
    difference.loc['open_times',:]=0
    difference=difference.fillna(0)
    for i in range(len(difference.columns)):
        for j in range(len(difference.index)-1):
            if difference.iloc[j,i]>0 or difference.iloc[j,i]==-2:
                difference.iloc[-1,i]+=1
    nums=difference.loc['open_times',:]*trading_days/len(signal.index) # Annualized Indicator
    nums=nums.sum()
    return nums


def MovingStd(rtn):
    '''20 days vol'''
    m  = len(rtn)
    std_list = []
    for i in range(m):
        if i < 19:
            std_list = np.append(std_list,np.NaN)
        else:
            std_list = np.append(std_list,rtn[i-19:i+1].diff()[1:].std())            
    return std_list

