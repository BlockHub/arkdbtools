arkdbtools
--------

arkdbtools is basically a set of functions and SQL used to query the ark-blockchain through an ark-node.
Since I noticed that I often reused the same code in different projects related to Ark, I decided to generalize the code
a bit.


To use, simply:

    >>> pip install arkdbtools

This library requires a running ark-node to operate: https://github.com/ArkEcosystem/ark-node.
We will set one up here as well. I recommend digitalocean as a vps provider. There are no fees for using arkdbtools,
so using my referral link does support further arkdbtools development: https://m.do.co/c/b5eee933a448

Use this guide to setup your ubuntu 16.04 vps. The 5$ per month one has enough RAM to contain the querysets + maintain ark-node:

https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04

Now download the ark-node. I recommend using the Ark-commander script to install and run it:

    cd
    wget https://ark.io/ARKcommander.sh
    bash ARKcommander.sh

After installing and rebooting, create a new psql user:

     $sudo -u postgres createuser <username>

You can add a password for security reasons, this is not necessary if you run query through localhost, but a must if you are querying over the internet.
Replace everything between <> with your user and password (erase <> as well )

     $sudo -u postgres psql
      psql=# ALTER USER <username> WITH ENCRYPTED PASSWORD '<password>';

Next we give the user SELECT only privilege. This ensures you don't mess with the ark-database, which would
otherwise break your node. Not necessary if you know what you are doing.

      psql=# GRANT SELECT ON ALL TABLES IN SCHEMA public TO <username>;

If you use the rebuild DB option in Ark-commander, you will have to redo these steps before connecting, as the user is deleted.

When using arkdbtools, set the connection parameters first:

    >>> import arkdbtools as ark
    >>> ark.set_connection(host='localhost',
                           database='ark_mainnet',
                           user=<username>,
                           password=<password>,)

Now if you want to calculate the trueblockweight share for a given delegate, we set delegate parameters first:
If you specifiy your passphrase, arkdbtools will generate your keys using Arky (by Toons).

    >>> ark.set_delegate(address='Adressandsomemore', delegate_pubkey='publickeyofdelegate',)

Next generate a dictionary containing the payouts:

    >>> payouts, timestamp_at_calculation = ark.Delegate.share()

.share() starts adding a running balance from the last transaction between a voter and the delegate.
You can specify custom start point using the argument last_payout. This takes either an integer and uses that for every
single voter, or a map {address: timestamp} to customise it for each voter.

Customizing calculations
------------------------

Calculation settings
    arkdbtools contains a config.py file where different settings influence Delegate.share() flow controls.
    >>> CALCULATION SETTINGS{...}

    are performed at the calculation level. Capitalized keys need to remain capitalized.

Blacklisting voters
    The option blacklist completely removes an address from the calculation. The share is evenly divided over all voters.

    >>> 'BLACKLIST': ['address',],

An Ark balance exception for a single address
    Exceptions allow you to replace the amount of Ark someone votes with. Use this to decrease the amount of large voters for example.
    If they remove Ark from their balance, and it drops below the amount specified in REPLACE, their current balance is used.

    >>> 'EXCEPTIONS': {'address': {'REPLACE': 'int else None'}},

Maximum voteweight
    This is the maximum value for the balance of a voter. If someone votes with more, his voteweight is reduced to the max amount for calculation
    purposes.

    >>> 'MAX': float('inf'),

Share fees
    A delegate receives both a block reward (2 Ark per block) and transaction fees. Set share_fees to True if you
    wish to share these fees as well. In my experience the average weekly fees for a delegate are +30 Ark.

    >>> 'share_fees': False,


You can modify these settings using:

    >>>set_calculation(blacklist, exceptions, max_amount, share_fees)

    This will make sure that these settings are only used in the namespace of the module

Core
----

Sending transactions
    dbtools also contains a Core class, which uses Arky to send transactions.
    This function will make 5 attempts to send a transaction before raising an ApiError. Smartbridge takes a string as argumen.

    >>> arkdbtools.dbtools.Core.send(address, amount, smartbridge)

Payoutsender
    This custom payoutsender uses a set of parameters to determine if a transaction should be sent. Data is a tuple,
    where data[0] is the address, and data[1] the dictionary value with the same schema as the return of the share() function.
    frq_dct is a map of addresses and frequencies, where 1 is daily, 2 is weekly, and 3 is monthly.
    Calculation_timestamp can be set if you wait some time between calculating and sending, else it will use the current Node timestamp (recommended).

    >>> arkdbtools.dbtools.Core.payoutsender(data, frq_dct, calculation_timestamp)

    Payoutsender returns 3 values as a tuple:
        1.) the result of send function, which is the api response (if the transaction was a success)
        2.) the delegate_share, which is the part that should go to the rewardswallet of the delegate.
        3.) the amount sent to the voter.

    if a transaction did not pass the parameters of payoutsender (for example the amount was below the minimum payout amount),
    payoutsender raises a TxParameterError

    taxes (the part that goes to the delegate) are calculated at sending level.


Setting the sender is also quite easy.

    >>> dbtools.set_sender(default_share=0, cover_fees=False, share_percentage_exceptions=None, timestamp_brackets=None,
    >>>                    min_payout_daily=1, min_payout_weekly=0, min_payout_monthly=0, day_weekly_payout=0, day_monthly_payout=10,
    >>>                    payoutsender_test=True, sender_exception=None)


share_percentage_exceptions
    takes a map of address: float. This allows you to set custom share percentages for certain addresses.

timestamp_brackets
    Are a bit more complicated. You need to pass a dictionary where the key is a timestamp, and the value is the share ratio.

>>>        {
>>>         float('inf'): 0.95,
>>>         16247647    : 0.96
>>>                             }

    The sender will check the keys from high to low, where the order of operations is low > high. So in this example if the
    vote_timestamp is smaller than 16247647, the share ratio is 0.96 (or 96%)

day_weekly_payout and day_monthly_payout
    Are the days where you want to send payouts for frequency 2 and 3 (weekly and monthly) 0 is monday, 6 is sunday for day_weekly_payout
    day_monthly_payout takes integers from 0 to 30, however don't use 30 as you'll skip every other month then.


sender_exception
    allows you to set absolute exceptions for a specific address. If the amount is greater than their trueblockweight allocated
    amount, an AllocationError is thrown and the payoutsender quits.

The order of operations of all of these settings is as follows:

    *.) sender_exceptions are executed or throw an error.
    *.) share_percentage_exceptions go above all others, except for sender_exceptions.
    *.) timestamp_brackets are used for all voters, unless they are also in share_percentage_exceptions.
    *.) default_share is used if none of the above apply.

Cover_fees has one catch, you need to have a sufficient balance from your delegateshare to cover them, else
your balance will run out while transmitting the transactions. An ApiError would then be raised.



