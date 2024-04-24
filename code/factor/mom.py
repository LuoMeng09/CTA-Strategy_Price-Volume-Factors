#%%
#%%
def Mom(data,w,l,a,b):
   '''
   according moment to format trading signal
   params:
   data: prices
   w : windows
   l : lags 
   a : upper threshold
   b : lower threshold
   '''
   w = int(w) # windows for Smoothing data
   l = int(l) # lags
   print(w,l,a,b)
   data_rl = data.rolling(w).mean() 
   if l ==1 :
       data_lg = (data_rl-data_rl.shift(l))/data_rl
   else:
       data_lg = (data_rl-data_rl.shift(l))/data_rl.rolling(l).std()
   # factor 
   data_lg.dropna(inplace=True) 
   # processing outlier
   std_upper, std_lower = data_lg[np.isfinite(data_lg)].mean() + data_lg[np.isfinite(data_lg)].std()*3, data_lg[np.isfinite(data_lg)].mean() - data_lg[np.isfinite(data_lg)].std()*3 # 去除了
   data_lg = data_lg.replace(np.inf,std_upper)
   data_lg = data_lg.replace(-np.inf,std_lower)
   # formatting signals
   sgl = pd.Series(0, index=data_lg.index)
   a_roll = data_lg.expanding().apply(lambda x: np.percentile(x, a), raw=True)
   b_roll = data_lg.expanding().apply(lambda x: np.percentile(x, b), raw=True)
   if icvalue >= 0:
       sgl[data_lg>a_roll] = 1
       sgl[data_lg<b_roll] = -1
   
   sgl_pred = sgl.copy()
   sgl = sgl.shift().dropna()

   return sgl
