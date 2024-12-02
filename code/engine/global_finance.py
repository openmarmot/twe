'''
module : engine/global_exchange_rates.py
language : Python 3.x
email : andrew@openmarmot.com
notes : sets the global exchange rates for various currencies and commodities
'''

# at initialization 1 can be thought of as 1 US dollar.
# thus initially all values are relative to the US dollar

# currencies 
#'currency name',value relative to 1
currencies={}
currencies['US Dollar']=1
currencies['German Reichsmark']=0.1
currencies['German Military Script']=1 # heavily controlled
currencies['Soviet Ruble']=0.2
currencies['Soviet Military Script']=1 # heavily controlled
currencies['Polish Zloty']=0.08

commodities={}
# 'commodity name',value relative to 1
commodities['gold']=33.85 # unit oz
