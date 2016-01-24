#lesson 1 algorithm

def initialize(context):
    #initializ a list of context stocks
    #context.uco = sid(37736) long oil
    #context.sco = sid(37737) short oil
    #context.boil = sid(41988) long natural gas
    #context.kold = sid(41987) short natural gas
    context.etf = sid(41988)
    context.shortEtf = sid(41987)
    
    #consecutive sequence counters
    context.sell_seq = 1
    context.buy_seq = 1
    context.sell_cd = 1
    context.buy_cd = 1
  
    #consecutive setup and countdown states
    context.in_buy_setup = False
    context.in_sell_setup = False
    context.in_buy_countdown = False
    context.in_sell_countdown = False

def reset(context):
    #consecutive sequence counters
    context.buy_seq = 1
    context.sell_seq = 1
    
    #consecutive countdown counters
    context.buy_cd = 1
    context.sell_cd = 1
    context.in_buy_setup = False
    context.in_sell_setup = False
    context.in_buy_countdown = False
    context.in_sell_countdown = False

#Will be called on every trade event for the securities you specify
def handle_data(context, data):
    
    #check if current close is higher or lower than the n-4 interval
    close_history = history(5, '1d', 'close_price')
    low_history = history(3, '1d', 'low')
    high_history = history(3, '1d', 'high')
    
    #get the previous closing
    #close from 4 previous sessions
    past_close = close_history[context.etf][0]
    current_close = close_history[context.etf][4]
    
    #get previous high and low
    past_low = low_history[context.etf][0]
    past_high =  high_history[context.etf][0]
    
    #increment the counters if close is lower or higher than close
    #4 days ago
    if current_close >= past_close:
        context.sell_seq += 1
        context.buy_seq = 1
    else:
        context.buy_seq += 1
        context.sell_seq = 1   
    
    #reached the 9 sell setup
    if context.sell_seq % 9 == 0:
        log.info('Sell sequence hit')
        #reset sequence check
        context.sell_seq = 1
        
        #check for recycle
        if context.in_sell_setup == True:
            reset(context)
        else:
            context.in_sell_countdown = True
            context.in_sell_setup = True
            
            #reset the buy setup and countdown
            context.in_buy_setup = False
            context.in_buy_countdown = False
            context.buy_cd = 1

    if context.buy_seq % 9 == 0:
        log.info('Buy sequence hit')
        context.buy_seq = 1
        
        #check for recycle
        if context.in_buy_setup == True:
            reset(context)
        else:
            context.in_buy_countdown = True
            context.in_buy_setup = True
            
            #reset the sell countdown and setup
            context.in_sell_countdown = False
            context.in_sell_setup = False
            context.sell_cd = 1

    #Countdown phase
    if context.in_buy_countdown == True:
        #check previous lows and highs
        if current_close <= past_low:
            context.buy_cd += 1

        #if we get to 13 sell signal
        if context.buy_cd == 13:
            log.info('Buying ETF')
            order_percent(context.etf, 0.33)
            #clear everything out
            reset(context)

    if context.in_sell_countdown == True:
        if current_close >= past_high:
            context.sell_cd += 1

        #if we get to 13 sell signal
        if context.sell_cd == 13:
            log.info('Buying ultra short ETF')
            order_percent(context.shortEtf, 0.33)
            #clear everything out
            reset(context)
        