def TermSignal(p0,p1,p2,p3,a,c,e,model,modelname):
    '''Term structure strategy: 
    Combine monthly contracts into term structure factors, 
    long the varieties with the highest strength of the term structure factor, 
    and the varieties with the lowest strength of the short factor
    params:
    p0-p3: open price of combine monthly contracts
    a,b,c,d: weigths of contracts
    '''
    term = pd.DataFrame()
    b=1-a
    d=1-c
    term=a*p0+b*p1+c*p2+d*p3 # term factor
    term1=term.copy()
    for i in term.columns:
        term[i]=term1[i]-term1[i].rolling(5).mean()
    term_factor=term.copy()
    for j in term.index:
        shortlist=term.sort_values(by=[j],axis=1,ascending=False).loc[j][len(term.columns)-e:len(term.columns)]
        shortlist=shortlist.index.tolist()
        shortlist=np.array(shortlist)
        longlist=term.sort_values(by=[j],axis=1,ascending=False).loc[j][:e]
        longlist=longlist.index.tolist()
        longlist=np.array(longlist)
        for i in term.columns:
            if term.loc[[j],[i]].values!=0:
                if i in longlist:
                    term.loc[[j],[i]]=1
                elif i in shortlist:
                    term.loc[[j],[i]]=-1
                else :
                    term.loc[[j],[i]]=0  
    timepred = term.iloc[-1,:]
    term=term.shift(periods=1,axis=0)
    term=term.fillna(0)
    term_factor=term_factor.shift(periods=1,axis=0)
    term_factor=term_factor.fillna(0)

    return term, term_factor