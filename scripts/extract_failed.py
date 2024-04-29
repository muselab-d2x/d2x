import os
f = open('./failed.txt', 'r')

version = f.readlines()[0].strip().split(':')[-1].strip()

f.close()
url = os.environ['PKG_API_URL'] + 'key/' + version +'?auth-token=' + os.environ['PKG_API_AUTH']

print(url)