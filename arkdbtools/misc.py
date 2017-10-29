from arky import api
import arkdbtools as at

at.set_connection(host="localhost",
                  database="ark_mainnet",
                  user="test",
                  password='test')

address = ['a', 'b', 'c']
addresses = 'IN {}'.format(tuple(address))
print(addresses)