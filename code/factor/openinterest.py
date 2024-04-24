def OpenInterest (oi_buy,oi_sell,w):
    '''
    params:
    oi_buy: net long position of large institutions
    oi_sell: net short position of large institutions
    w : windows for smoothing data
    '''

    signal= pd.DataFrame()
    signal=oi_buy-oi_sell

    for i in oi_buy.columns:
        signal[i] = signal[i].rolling(w).mean()
    signal=signal.fillna(0)
    signal_factor=signal.copy()
    for i in signal.columns:
        signal.loc[:,i] = signal.loc[:,i].apply(lambda x: 1 if x>0 else(-1 if x<0 else 0)) 
    timepred = signal.iloc[-1,:]                
    signal = signal.shift(periods=1,axis=0)
    signal=signal.fillna(0)
    signal_factor = signal_factor.shift(periods=1,axis=0)
    signal_factor=signal_factor.fillna(0)
    signal_factor=signal_factor.sum(axis=1)/len(signal_factor.columns)

    return signal,signal_factor