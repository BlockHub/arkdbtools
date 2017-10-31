
import arkdbtools as ark
from arky import api
ark.set_connection(
    host="localhost",
    database="ark_mainnet",
    user="ark",
    password=None)


# address
# address = 'AJwHyHAArNmzGfmDnsJenF857ATQevg8HY'
# txhistory = ark.Address.transactions(address)
# balance = ark.Address.balance(address)
# votes = ark.Address.votes(address)
#
# for i in votes:
#     print(i, ': ', votes[i])

#node
# height = ark.Node.height()
# time = ark.Node.max_timestamp()
# up = ark.Node.check_node(51)

# print(height)
# print(time)
# print(up)

# delegate
# pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'
# votes = ark.Delegate.votes(pubkey)
# unvoters = ark.Delegate.unvotes(pubkey)
#
# voters = ark.Delegate.voters(pubkey)
# for i in voters:
#     print(i)
# print(len(votes))
# print(len(unvoters))
# print(len(voters))

ark.set_delegate(address='AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE',
                 pubkey='0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a')
# res = ark.Delegate.share()
# for i in res[0]:
#     print(i)
# payout1 = ark.Delegate.lastpayout(delegate_address=ark.DELEGATE['ADDRESS'])
# payout2 = ark.Delegate.lastpayout(delegate_address=ark.DELEGATE['ADDRESS'],
#                                   blacklist=['AJwHyHAArNmzGfmDnsJenF857ATQevg8HY'])
# for i in payout1:
#     print(i)
# print(len(payout1))
# print(len(payout2))

# blocks = ark.Delegate.blocks()
# for i in blocks:
#     print(i)
#
res = ark.Delegate.share(start_block=0,)
for i in res[0]:
    print(i, res[0][i]['share']/ark.ARK, res[0][i]['status'], res[0][i]['balance']/ark.ARK)
sums = 0
for x in res[0]:
    sums += res[0][x]['share']
print(sums/ark.ARK)

print(ark.Address.balance('AXzEMF7TC1aH3ax1Luxk6XdyKXDRxnBj4f')/ark.ARK)