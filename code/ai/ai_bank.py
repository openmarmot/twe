
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : a bank.
'''


#import built in modules

#import custom packages
import engine.global_finance

#global variables

class AIBank():
    def __init__(self):

        # unique bank name
        self.name=''

        # list of currencies this bank will accept
        self.currencies_accepted=[]

        # list of commodities this bank will accept
        self.commodities_accepted=[]

        # factions with good relations
        self.factions_accepted=[]

        # markup on currency exchange
        self.exchange_markup=0

        # ------------

        # -- accounts --
        # the index for the account that the bank owns. normally 0
        self.bank_internal_account=0

        # unique account number for the bank. increments for each account
        self.account_increment=0
        # {account number : {'currency':amount}}
        self.accounts={}

    #---------------------------------------------------------------------------
    def create_account(self):
        '''creates a new account. returns the account number'''
        self.account_increment+=1
        self.accounts[self.account_increment]={}
        return self.account_increment
    
    #---------------------------------------------------------------------------
    def deposit(self,account_number,currency_name,amount):
        '''deposity currency to an account'''
        # return [Bool as to whether it was accepted,'Flavor Text']
        
        
        # check that the account number exists
        if account_number not in self.accounts:
            return [False,'This account does not exist']
        
        # check that we are accepting the currency
        if currency_name not in self.currencies_accepted:
            return [False,'This currency is not accepted']
        
        # got this far so it is accepted

        # add amount to the account
        if currency_name not in self.accounts[account_number]:
            self.accounts[account_number]={currency_name:amount}
        else:
            self.accounts[account_number][currency_name]+=amount

        # add amount to the banks real holdings 
        if currency_name not in self.currencies:
            self.currencies[currency_name]=amount
        else:
            self.currencies[currency_name]+=amount

        return [True,'Deposit Accepted']



    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        pass

    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def withdrawl(self,account_number,currency_name,amount):
        '''withdraw currency from an account '''
        # return [Bool as to whether it was accepted,'Flavor Text']

        # check that the account number exists
        if account_number not in self.accounts:
            return [False,'This account does not exist']
        
        # check that the account has the currency and at least the amount requested
        if currency_name not in self.accounts[account_number]:
            return [False,'This account does not hold this currency']
        
        # check that there is enough currency in the account
        if self.accounts[account_number][currency_name]<amount:
            return [False,'The account has insufficient funds']
        
        # check that the bank itself has the funds
        # if it was deposited the bank will have it in at least 0 amount
        if self.currencies[currency_name]<amount:
            return [False,'The bank is low on funds at the moment, and is limiting withdrawls.']
        
        # got past all the checks, so withdraw the amount
        self.accounts[account_number][currency_name]-=amount
        self.currencies[currency_name]-=amount
        return [True,'The withdrawl has completed']


