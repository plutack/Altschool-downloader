import os
import requests
from dotenv import load_dotenv
from downloader import downloadVideo


load_dotenv()

LOGINURL = "https://actors-services.herokuapp.com/api/v1/auth/login"
headers = {"Content-type": "application/json"}
SECRET = {"email": os.getenv("EMAILADDRESS"), "password": os.getenv("PASSWORD")}

session = requests.Session()
session.post(LOGINURL, headers=headers, json=SECRET)


CSRFTOKENURL = "https://portal.altschoolafrica.com/api/auth/csrf"
response = session.get(CSRFTOKENURL)
csrfTokenJson = response.json()
csrfToken = csrfTokenJson["csrfToken"]



CREDENTIALURL = "https://portal.altschoolafrica.com/api/auth/callback/credentials?"
payload = {
    "email": os.getenv("EMAILADDRESS"),
    "password": os.getenv("PASSWORD"),
    "redirect": "false",
    "callbackUrl": "/applications/school",
    "csrfToken": csrfToken,
    "json": "true",
}
session.post(CREDENTIALURL, headers=headers, json=payload)



sessionUrl = "https://portal.altschoolafrica.com/api/auth/session"
response = session.get(sessionUrl)
sessionInfo = response.json()
bearerCode = sessionInfo["user"]["token"]

headers = {"Authorization": f"Bearer {bearerCode}"}
USERINFOURL = "https://actors-services.herokuapp.com/api/v1/auth/me" 
response = session.get(USERINFOURL, headers=headers)
userInfo = response.json()

schoolId = userInfo["data"]["schoolId"]
courseId = userInfo["data"]["courseId"]

payload = {"limit": 50}
STUDYKITURL = "https://actors-services.herokuapp.com/api/v1/study-kits"
response = session.get(STUDYKITURL, headers=headers, params=payload)
videoDetails = response.json()
 
schoolCategory = videoDetails["data"]
videoList = []

for subcategory in schoolCategory:
    if courseId == subcategory['facultyId']['_id']:
        courseName = subcategory['facultyId']['name']

    if schoolId == subcategory['schoolId']['_id'] and courseId == subcategory['facultyId']['_id']:
        folderDict = {}
        topic = subcategory['topic']
        subtopics = subcategory['subTopics']    
        folderDict['Topic'] = topic
        folderDict['Subtopics'] = subtopics
        videoList.append(folderDict)
        
rootPath = os.path.join(os.getcwd(), f'Altschool {courseName}')
os.makedirs(rootPath)
for folder in videoList:
    childPath = os.path.join(rootPath, folder['Topic'])
    os.makedirs(childPath)
    for subtopic in folder['Subtopics']:
        videoName = f"{subtopic['name']}.mp4"
        videoUrl = subtopic['videoLink'].split('?')[0] + '/config'
        response = requests.get(videoUrl)
        data = response.json()
        masterJsonUrl = data['request']['files']['dash']['cdns']['fastly_skyfire']['avc_url']
        downloadVideo(masterJsonUrl, videoName, childPath)
        print("study kit downloaded successfully!")



        




