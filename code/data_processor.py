def tran_nan (netvalue):
    # trans non-num to nan
    for i in netvalue.columns:
        netvalue.loc[:,i] = pd.to_numeric(netvalue.loc[:,i],'coerce')
    netvalue.dropna(how='all',axis=0,inplace=True)
    netvalue.dropna(how='all',axis=1,inplace=True)
    return netvalue

def AskBid(inputprice):
    # extract highest ask and lowest bid (per sec)
    ask,bid = inputprice['ask'],inputprice['bid']
    output = pd.DataFrame()
    for i in range(len(ask)-1):
        if type(ask.index[i+1])== str or type(ask.index[i])== str:
            pass
        else:
            index1 = ask.index[i].strftime('%Y-%m-%d %H:%M:%S')
            index2 = ask.index[i+1].strftime('%Y-%m-%d %H:%M:%S')
            print(index1)
            if index1 == index2 :
                output.loc[index1,'ask'] = max(ask[i],ask[i+1])
                output.loc[index1,'bid'] = min(bid[i],bid[i+1])
        
    return output

def Outlier(df):
    # process outlier
    factor = df.copy()
    factor1 = factor.replace([np.inf,-np.inf],[np.nan,-np.nan])
    mean = np.nanmean(factor1)
    std_upper, std_lower = mean + factor1.std().mean()*2, mean - factor1.std().mean()*2
    scale = std_upper - std_lower
    name = []
    for i in factor.columns:
        for j in factor.index:
            if factor.loc[j,i] > std_upper or factor.loc[j,i]==float('inf'):
                factor.loc[j,i] = std_upper
                name.append(i)
            elif factor.loc[j,i] < std_lower or factor.loc[j,i]==float('-inf') :
                factor.loc[j,i] = std_lower
                name.append(i)
    for i in factor.columns:
        if i in name:
            factor[i] = (factor[i] - mean) / scale   
            factor[i] = (factor[i] - factor[i][0])+1
    return factor
