def Panel_Signal(df_open,windows,lag,a,model,modelname):
    '''
    Cross-sectional strategy: 
    long the varieties with the highest momentum, 
    and short the varieties with the lowest momentum
    '''
    panel1 = pd.DataFrame()
    panel = pd.DataFrame()# MA（windows）-MA（windows）（lag）/std(t:t-lag)
    for i in df_open.columns:
        panel1[i]=df_open[i].rolling(windows).mean()
    for i in df_open.columns:
        panel[i]=(panel1[i]-panel1[i].shift(lag))/panel1[i].rolling(lag).std()
    panel=panel.fillna(0)
    panel_factor=panel.copy()
    for j in panel.index:
        shortlist=panel.sort_values(by=[j],axis=1,ascending=False).loc[j][len(panel.columns)-a:len(panel.columns)]
        shortlist=shortlist.index.tolist()
        shortlist=np.array(shortlist)
        longlist=panel.sort_values(by=[j],axis=1,ascending=False).loc[j][:a]
        longlist=longlist.index.tolist()
        longlist=np.array(longlist)
        for i in panel.columns:
            if panel.loc[[j],[i]].values!=0:
                if i in longlist:
                    panel.loc[[j],[i]]=1
                elif i in shortlist:
                    panel.loc[[j],[i]]=-1
                else :
                    panel.loc[[j],[i]]=0
    timepred = panel.iloc[-1,:]
    panel = panel.shift(periods=1,axis=0)
    panel = panel.fillna(0)
    panel_factor = panel_factor.shift(periods=1,axis=0)
    panel_factor = panel_factor.fillna(0)
    panel_factor = panel_factor.sum(axis=1)/len(panel_factor.columns)

    return panel, panel_factor