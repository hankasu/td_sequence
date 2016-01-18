# Put any initialization logic here.  The context object will be passed to
# the other methods in your algorithm.
def initialize(context):
    context.security = sid(37736) #UCO
    context.setupPeriod = 13
    context.SEQUENCE_COUNT = 9
    context.COUNTDOWN_COUNT = 13
    context.buy_setup_count = 0
    context.sell_setup_count = 0
    context.countdown_period = 0
    context.recycle = 0
    context.last_setup = None

#check for a buy setup which is a close lower than the close
#from 4 sessions previous
def checkSetup(context):
    #in the history dataframe the 0th index is the start of the history
    set_history = history(context.setupPeriod, '1d', 'close_price')
    period_high = history(context.setupPeriod, '1d', 'high')[context.security].max()
    period_low = history(context.setupPeriod, '1d', 'low')[context.security].min()
    sec_series = set_history[context.security]
    setupCounter = 0
    
    #check the past 9 intervals
    for idx in range(4, context.setupPeriod):
        #buy setup security going down
        if  sec_series[idx] <= sec_series[idx - 4]:
            setupCounter -= 1
        #sell setup going up
        if sec_series[idx] >= sec_series[idx - 4]:
            setupCounter += 1
        
    if setupCounter == context.SEQUENCE_COUNT and sec_series.min() > period_low:
        return 'sell'
    elif setupCounter == -context.SEQUENCE_COUNT and sec_series.max() < period_high:
        return 'buy'
    else:
        return None
 

def checkCountdown(context):
    close_series = history(context.countdown_period, '1d', 'close_price')[context.security]
    high_series = history(context.countdown_period, '1d', 'high')[context.security]
    low_series = history(context.countdown_period, '1d', 'low')[context.security]
    
    setup_counter = 0
    
    for idx in range(context.countdown_period):
        if close_series[idx] <= low_series[idx - 2]:
            setup_counter -= 1
        if close_series[idx] >= high_series[idx - 2]:
            setup_counter += 1
    #return which setup based on the sign
    if setup_counter == context.COUNTDOWN_COUNT:
        return 'sell'
    elif setup_counter == -context.COUNTDOWN_COUNT:
        return 'buy'
    else:
        return None

def reset_counters(context):
    context.sell_setup_count = 0
    context.buy_setup_count = 0
    context.countdown_period = 0
    
    
# Will be called on every trade event for the securities you specify. 
def handle_data(context, data):
    #check for the setup
    setup_type = checkSetup(context)
    
    if last_setup == 'buy' or last_setup == 'sell':
        context.recycle += 1
        
    if setup_type == 'buy':
        log.info('Buy Setup Hit')
        context.buy_setup_count += 1
               
    elif setup_type == 'sell':
        log.info('Sell Setup Hit')
        context.sell_setup_count += 1
  
    #check for trend cancellations
    if (context.sell_setup_count > 1 or context.buy_setup_count > 1 or
        context.sell_setup_count == 1 and context.buy_setup_count == 1):
        reset_counters(context)
        
    #check if we are in a countdown phase
    if context.sell_setup_count == 1 or context.buy_setup_count == 1:
        context.countdown_period += 1
        
    #sell countdown
    if (context.sell_setup_count == 1 and 
        context.countdown_period >= context.COUNTDOWN_COUNT + 2):#15 intervals
        setup_cd = checkCountdown(context)
        if setup_cd == 'sell':
            log.info('Sell Countdown Hit')
            reset_counters(context)
    
    #buy countdown
    if (context.buy_setup_count == 1 and 
        context.countdown_period >= context.COUNTDOWN_COUNT + 2):#15 intervals
        setup_cd = checkCountdown(context)
        if setup_cd == 'buy':
            log.info('Buy Countdown Hit')
            reset_counters(context)
    
    #set the setup marker
    context.last_setup = setup_type