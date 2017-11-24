import arkdbtools.dbtools as ark

CONNECTION = {
    'HOST': 'localhost',
    'DATABASE': 'ark_mainnet',
    'USER': 'ark',
    'PASSWORD': None,
}

DELEGATE = {
    'PUBKEY'      : '031641ff081b93279b669f7771b3fbe48ade13eadb6d5fd85bdd025655e349f008',
    'ADDRESS'     : 'ANwjGUcVbLXpqbBUWbjUBQWkr4MWVDuJu9',
    'PASSPHRASE'  : None,
    'REWARDWALLET': None,
    }

ark.set_connection(
        host=CONNECTION['HOST'],
        database=CONNECTION['DATABASE'],
        user=CONNECTION['USER'],
        password=CONNECTION['PASSWORD'])


ark.set_delegate(
        address= DELEGATE['ADDRESS'],
        pubkey=  DELEGATE['PUBKEY'],
        secret=  DELEGATE['PASSPHRASE'],
    )

a, b = ark.Delegate.trueshare()

for i in a:
        print(i)