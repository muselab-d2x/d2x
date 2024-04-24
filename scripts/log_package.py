import requests
print(os.environ)
f = open('./create-package-output.txt', 'r')
lines = f.readlines()
ancestorId = ''
versionNumber = ''
versionId = ''
installationKey = ''
packageName = ''
releaseTag = ''
for line in lines:
    if line.find('Resolved ') != -1:
        ancestorId = line.strip().split(':')[-1].strip()
    if line.find('Version Number: ') != -1:
        versionNumber = line.strip().split(':')[-1].strip()
    if line.find('SubscriberPackageVersion Id') != -1:
        versionId = line.strip().split(':')[-1].strip()
    if line.find('install_key') != -1:
        installationKey = line.strip().split(':')[-1].strip()
    if line.find('package_name') != -1:
        packageName = line.strip().split(':')[-1].strip()
    if line.find('tag:') != -1:
        releaseTag = line.strip().split(':')[-1].strip()
url = os.environ['PKG_API_URL'] + 'info'
print('Posting to URL')
print(url)
json = {
    'packageName': packageName,
    'releaseTag': releaseTag,
    'installationKey': installationKey,
    'packageVersionId': versionId,
    'packageVersion': versionNumber,
    'ancestorVersionId': ancestorId,
    'packageType': releaseTag.split("/")[0].strip(),
}
print('Input')
print(json)
res = requests.post(url, json=json, headers={
    'auth-token': os.environ['PKG_API_AUTH'],
    "Content-Type": "application/json; charset=utf-8"
})
print('Response Code')
print(res.status_code)
f.close()