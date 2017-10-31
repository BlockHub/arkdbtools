arkdbtools
--------

To use, simply do::

    >>> pip install arkdbtools

This library requires a running ark-node to operate: https://github.com/ArkEcosystem/ark-node.

First create a new psql user::
    >>> $sudo -u postgres createuser <username>

You can add a password for security reasons, this is not necessary if you run your programs using a local
node, but a must if you ar querying over the internet.

    >>> $sudo -u postgres psql
    >>> psql=# ALTER USER <username> WITH ENCRYPTED PASSWORD '<password>';

Next we give the user SELECT only privilege. This ensures you don't mess with the ark-database, which would
otherwise break your node. Not necessary if you know what you are doing.

    >>> psql=# GRANT SELECT ON ALL TABLES IN SCHEMA public TO <username>;

When using arkdbtools, set the connection parameters first:

    >>> import arkdbtools as ark
    >>> ark.set_connection(host='localhost',
                       database='ark_mainnet',
                       user=<username>,
                       password=<password>,)

Now if you want to calculate the trueblockweight share for a given delegate, we set delegate parameters first:
If you specifiy your passphrase, arkdbtools will generate your keys using Arky (by Toons).

    >>> ark.set_delegate(address='Adressandsomemore',
                         pubkey='publickeyofdelegate',
                         )

Next generate a dictionary containing the payouts:

    >>> payouts, timestamp_at_calculation = ark.Delegate.share()
    >>> for i in payouts:
    >>>     print(i, payouts[i])

.share() starts adding a running balance from the last transaction between a voter and the delegate.
You can specify custom start point using the argument last_payout. This takes either an integer and uses that for every
single voter, or a map {address: timestamp} to customise it for each voter.

You can use Arky (https://github.com/Moustikitos/arky/) to send the transactions to your voters.

