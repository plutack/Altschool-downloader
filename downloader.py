import os
import base64
import ffmpeg
import requests
from tqdm import tqdm


def downloadVideo(masterJsonUrl, videoName, childPath):
    masterJsonUrl= masterJsonUrl.replace("\u0026", "&")
    
    substrings = masterJsonUrl.split('/')
    baseUrl = '/'.join(substrings[:5]) + '/parcel/'
   
    response = requests.get(masterJsonUrl)
    content = response.json()

    if os.path.exists(os.path.join(childPath, videoName)):
        print(f"{videoName} exists")
    else:
    # Video download here
        heights = [(i, d["height"]) for (i, d) in enumerate(content['video'])]
        idx = max(heights, key=lambda x: x[1])
        video = content['video'][idx[0]]
        videoBaseUrl = baseUrl + video["base_url"]
        filenameVideo = os.path.join(childPath, f'video_{video["id"]}')
        if os.path.exists(filenameVideo):
            os.remove(filenameVideo)
        with open(filenameVideo, "wb") as file:
            init_segment = base64.b64decode(video["init_segment"])
            file.write(init_segment)
            for segment in tqdm(video["segments"]):
                segment_url = videoBaseUrl + segment["url"].replace("\u0026", "&")
                response = requests.get(segment_url, stream=True)
                if response.status_code != 200:
                    print(response)
                    break
                for chunk in response:
                    file.write(chunk)
            file.flush()

        # Audio download here
        bitrate = [(i, d["bitrate"]) for (i, d) in enumerate(content['audio'])]
        idx = max(bitrate, key=lambda x: x[1])
        audio = content['audio'][idx[0]]
        audioBaseUrl = baseUrl + audio["base_url"]
        filenameAudio = os.path.join(childPath, f'audio_{audio["id"]}')
        if os.path.exists(filenameAudio):
            os.remove(filenameAudio)
        with open(filenameAudio, "wb") as file:
            init_segment = base64.b64decode(audio["init_segment"])
            file.write(init_segment)
            for segment in tqdm(audio["segments"]):
                segment_url = audioBaseUrl + segment["url"].replace("\u0026", "&")
                response = requests.get(segment_url, stream=True)
                if response.status_code != 200:
                    print(response)
                    break
                for chunk in response:
                    file.write(chunk)
            file.flush()
        
        try:
            inputVideo = ffmpeg.input(filenameVideo)
            inputAudio = ffmpeg.input(filenameAudio) 
            ffmpeg.concat(inputVideo, inputAudio, v=1, a=1).output(os.path.join(childPath, videoName)).run() 
            print("Merge completed!\nVideo saved successfully")

        except ffmpeg.Error as error:
            print(error.stderr)

        os.remove(filenameVideo)
        os.remove(filenameAudio)
        print("Temporary files removed!")    