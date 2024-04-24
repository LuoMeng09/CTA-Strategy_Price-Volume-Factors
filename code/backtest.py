
def TradePreSec(askbid_open,askbid_close,capital1,i,lots,k,pred,pos,clopos,ask_bid):
    '''
    Trading Signal Triggers:
    Single-second order mechanism
    Check the date and time of a single second
    The number of lots to be ordered
    The price of the reserved signal for the number of days
    clopos: 1 - Rollover to close the position 
    '''
    price=0
    if clopos ==1: 
        askbid = askbid_close
    else:
        askbid = askbid_open
    if ask_bid == 'ask': 
        ask = SelectDate(pred,i,askbid['ask']) 
        if clopos ==1 : ask = ask[-lots:] 
        else : ask = ask[:lots]
        print(lots,len(ask))
        price = np.average(ask) 
    elif ask_bid == 'bid':
        bid = SelectDate(pred,i,askbid['bid'])
        if clopos ==1 : bid = bid[-lots:]
        else : bid = bid[:lots]
        print(lots,len(bid))
        price = np.average(bid)
    return price

#%%    
def BackTest(pred,name,p0,p1,close,askbid_open,askbid_close,net1,net2,pricesB,pricesS,lots,pos,code,n,z,k,lev,alpha):
    '''
    Backtesting Functions:
    p0: open price # The highest bid price is used to buy 1 hour after the opening of the market, and the lowest bid price is used to sell --askbid_open
    p1: settle price 
    close:close price # The last 1 hour price is used to calculate the rollover gain - askbid_close
    lots: lot size
    k: Handling fee
    code: the code of the contract
    n: window time/length of the original sequence
    z: the number of days before the rollover
    lev: leverage
    alpha: stop loss
    pos/pred -- the data stored on a daily basis

    net1 : floating P&L
    net2 : settling P&L
    '''
    m=len(pred) 
    capital=net2/lev
    pricesB=np.append(pricesB,np.full(m-n,np.nan))
    pricesS=np.append(pricesS,np.full(m-n,np.nan))  
    pos=np.append(pos,np.full(m-n,np.nan))    
    count=0
    clopos=0
    for i in range(n,m):
        clopos=0
        if count == 0: 
            p=p0
            c=close
        if pos[i-1]==1: 
            if pred[i]==1:
                if (count==0) and (i<=m-z-1) and (code[i]!=code[i+z]): # Closing profit and loss = (sell transaction price - buy transaction price) * trading unit * number of closed lots
                    count=z # # The code on the zth day is not equal to the code on the day, and the rollover is changed
                    capital=capital-pricesB[np.max(np.where(~np.isnan(pricesB)))]*lots
                    clopos=1
                    capital=capital+(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')*lots 
                    pricesB[i]=TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')
                    capital=capital-k*pricesB[i]*lots # Balance of the day = balance of the previous day (gradual hedging) + profit and loss of closing position + deposit - withdrawal - handling fee
                    pos[i]=1
                    net1=np.append(net1,capital+(-pricesB[np.max(np.where(~np.isnan(pricesB)))]+p1[i])*lots)
                    net2=np.append(net2,capital)
                else:
                    if (pricesB[np.max(np.where(~np.isnan(pricesB)))]-close[i])>alpha*(pricesB[np.max(np.where(~np.isnan(pricesB)))]): 
                        capital=capital-alpha*(pricesB[np.max(np.where(~np.isnan(pricesB)))])*lots
                        pos[i]=0
                        net1=np.append(net1,capital)
                        net2=np.append(net2,capital)                                            
                    else:
                        net1=np.append(net1,capital+(-pricesB[np.max(np.where(~np.isnan(pricesB)))]+p1[i])*lots) #持续做多：原有浮动收益+次日价格（open）
                        net2=np.append(net2,capital)
                        pos[i]=1
            elif pred[i]==0: 
                capital=capital-pricesB[np.max(np.where(~np.isnan(pricesB)))]*lots
                capital=capital+(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')*lots
                pos[i]=0
                net1=np.append(net1,capital)
                net2=np.append(net2,capital)
            elif pred[i]==-1:
                if (count==0) and (i<=m-z-1) and (code[i]!=code[i+z]):
                    count=z 
                    capital=capital-pricesB[np.max(np.where(~np.isnan(pricesB)))]*lots
                    clopos=1
                    capital=capital+(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')*lots
                    pricesS[i]=TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')
                    capital=capital-k*pricesS[i]*lots
                    pos[i]=-1
                    net1=np.append(net1,capital+(pricesS[np.max(np.where(~np.isnan(pricesS)))]-p1[i])*lots)
                    net2=np.append(net2,capital)
                else: 
                    capital=capital-pricesB[np.max(np.where(~np.isnan(pricesB)))]*lots
                    capital=capital+(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')*lots
                    pricesS[i]=TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')
                    capital=capital-k*pricesS[i]*lots
                    if (-pricesS[np.max(np.where(~np.isnan(pricesS)))]+close[i])>alpha*pricesS[np.max(np.where(~np.isnan(pricesS)))]:
                        capital=capital-alpha*(pricesS[np.max(np.where(~np.isnan(pricesS)))])*lots
                        net1=np.append(net1,capital)
                        net2=np.append(net2,capital)
                        pos[i]=0
                    else:
                        pos[i]=-1
                        net1=np.append(net1,capital+(pricesS[np.max(np.where(~np.isnan(pricesS)))]-p1[i])*lots)   
                        net2=np.append(net2,capital) 
        elif pos[i-1]==-1:          
            if pred[i]==-1:                 
                if (count==0) and (i<=m-z-1) and (code[i]!=code[i+z]):
                    count=z 
                    clopos=1
                    capital = capital+pricesS[np.max(np.where(~np.isnan(pricesS)))]*lots
                    capital = capital-(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')*lots
                    pricesS[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')
                    capital=capital-k*pricesS[i]*lots
                    pos[i]=-1
                    net1=np.append(net1,capital+(pricesS[np.max(np.where(~np.isnan(pricesS)))]-p1[i])*lots)
                    net2=np.append(net2,capital)
                else:                                      
                    if (-pricesS[np.max(np.where(~np.isnan(pricesS)))]+close[i])>alpha*(pricesS[np.max(np.where(~np.isnan(pricesS)))]):
                        capital=capital-alpha*(pricesS[np.max(np.where(~np.isnan(pricesS)))])*lots
                        net1=np.append(net1,capital)
                        net2=np.append(net2,capital)
                        pos[i]=0
                    else :
                        pos[i]=-1
                        net1=np.append(net1,(capital+(pricesS[np.max(np.where(~np.isnan(pricesS)))]-p1[i])*lots))
                        net2=np.append(net2,(capital))
            elif pred[i]==0:  
                capital=capital+pricesS[np.max(np.where(~np.isnan(pricesS)))]*lots
                capital=capital-(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')*lots
                pos[i]=0
                net1=np.append(net1,capital)
                net2=np.append(net2,capital)
            elif pred[i]==1:
                if (count==0) and (i<=m-z-1) and (code[i]!=code[i+z]):
                    count=z 
                    clopos=1
                    capital = capital+pricesS[np.max(np.where(~np.isnan(pricesS)))]*lots
                    capital = capital-(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')*lots
                    pricesB[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')
                    capital=capital-k*pricesB[i]*lots
                    pos[i]=1
                    net1=np.append(net1,capital+(-pricesB[np.max(np.where(~np.isnan(pricesB)))]+p1[i])*lots)
                    net2=np.append(net2,capital)
                else:   
                    capital = capital+pricesS[np.max(np.where(~np.isnan(pricesS)))]*lots
                    capital = capital-(1-k)*TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')*lots
                    pricesB[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')
                    capital=capital-k*pricesB[i]*lots
                    clopos=0
                    if (pricesB[np.max(np.where(~np.isnan(pricesB)))]-close[i])>alpha*pricesB[np.max(np.where(~np.isnan(pricesB)))]:
                        capital=capital-alpha*(pricesB[np.max(np.where(~np.isnan(pricesB)))])*lots
                        net1=np.append(net1,capital)
                        net2=np.append(net2,capital)
                        pos[i]=0
                    else:
                        pos[i]=1
                        net1=np.append(net1,capital+(-pricesB[np.max(np.where(~np.isnan(pricesB)))]+p1[i])*lots)
                        net2=np.append(net2,capital)
        elif pos[i-1]==0:          
            if pred[i]==1:      
                if (count==0) and (i<=m-z-1) and (code[i]!=code[i+z]):
                    count=z 
                    clopos=1
                    pricesB[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')
                    capital=capital-k*pricesB[i]*lots
                    pos[i]=1
                    net1=np.append(net1,capital+(-pricesB[np.max(np.where(~np.isnan(pricesB)))]+p1[i])*lots)
                    net2=np.append(net2,capital)
                    clopos=0
                else: 
                    pricesB[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')
                    capital=capital-k*pricesB[i]*lots
                    if (pricesB[np.max(np.where(~np.isnan(pricesB)))]-close[i])>alpha*pricesB[np.max(np.where(~np.isnan(pricesB)))]:
                        capital=capital-alpha*(pricesB[np.max(np.where(~np.isnan(pricesB)))])*lots
                        net1=np.append(net1,capital)
                        net2=np.append(net2,capital)
                        pos[i]=0
                    else:
                        pos[i]=1
                        net1=np.append(net1,capital+(-pricesB[np.max(np.where(~np.isnan(pricesB)))]+p1[i])*lots)
                        net2=np.append(net2,capital)
            elif pred[i]==-1:      
                if (count==0) and (i<=m-z-1) and (code[i]!=code[i+z]): 
                    count=z                    
                    clopos=1
                    pricesS[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'bid')
                    capital=capital-k*pricesS[i]*lots
                    pos[i]=-1
                    net1=np.append(net1,capital+(pricesS[np.max(np.where(~np.isnan(pricesS)))]-p1[i])*lots)
                    net2=np.append(net2,capital)
                    clopos=0
                else:     
                    pricesS[i] = TradePreSec(askbid_open,askbid_close,capital,i,lots,k,pred,pos,clopos,'ask')
                    capital=capital-k*pricesS[i]*lots
                    if (-pricesS[np.max(np.where(~np.isnan(pricesS)))]+close[i])>alpha*pricesS[np.max(np.where(~np.isnan(pricesS)))]:
                        capital=capital-alpha*(pricesS[np.max(np.where(~np.isnan(pricesS)))])*lots
                        net1=np.append(net1,capital)
                        net2=np.append(net2,capital)
                        pos[i]=0
                    else:
                        pos[i]=-1
                        net1=np.append(net1,capital+(pricesS[np.max(np.where(~np.isnan(pricesS)))]-p1[i])*lots)
                        net2=np.append(net2,capital)
            else:
                net1=np.append(net1,capital)
                net2=np.append(net2,capital)
                pos[i]=0
        if count>0:count=count-1
        print(i,pos[i-1],pred[i],clopos,p1[i],net1,net2)
    net1=pd.DataFrame(net1,index=pred.index)
    net2=pd.DataFrame(net2,index=pred.index)
    pricesB=pd.DataFrame(pricesB,index=pred.index)
    pricesS=pd.DataFrame(pricesS,index=pred.index)
    pos=pd.DataFrame(pos,index=pred.index)
    return net1,net2,pricesB,pricesS,pos
