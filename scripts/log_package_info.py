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
url = 'https://qekae5pu5jwysp7qcn7eh6cozu0yyvum.lambda-url.ca-central-1.on.aws/info'
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
    'auth-token': 'sjkldfjklsdjklfasjlkdf',
    "Content-Type": "application/json; charset=utf-8"
})
print('Response')
print(res.json())
f.close()