import requests


"""
    
https://www.kuaishou.com/graphql

    
Origin:
https://www.kuaishou.com
Referer:
https://www.kuaishou.com/brilliant
Sec-Ch-Ua:
"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"
Sec-Ch-Ua-Mobile:
?0
Sec-Ch-Ua-Platform:
"Windows"
Sec-Fetch-Dest:
empty
Sec-Fetch-Mode:
cors
Sec-Fetch-Site:
same-origin
User-Agent:
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
    
data:
operationName
: 
"brilliantTypeDataQuery"
query
: 
"fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment photoResult on PhotoResult {\n  result\n  llsid\n  expTag\n  serverExpTag\n  pcursor\n  feeds {\n    ...feedContent\n    __typename\n  }\n  webPageArea\n  __typename\n}\n\nquery brilliantTypeDataQuery($pcursor: String, $hotChannelId: String, $page: String, $webPageArea: String) {\n  brilliantTypeData(pcursor: $pcursor, hotChannelId: $hotChannelId, page: $page, webPageArea: $webPageArea) {\n    ...photoResult\n    __typename\n  }\n}\n"
variables
: 
{hotChannelId: "00", page: "brilliant"}    
    
    
    
    
"""
    
    
url="https://www.kuaishou.com/graphql"
headers={
    "Origin":"https://www.kuaishou.com",
    "Referer":"https://www.kuaishou.com/brilliant",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # "Cookie":"kpf=PC_WEB; clientid=3; did=web_6112d09c75b9e4e8badec4dcafa4c74f; kpn=KUAISHOU_VISION",
    # "Connection":"keep-alive",
    # "Content-Length":"1853",
    # "Content-Type":"application/json",
    "Sec-Ch-Ua-Platform":"Windows"
}
query_str="""
fragment photoContent on PhotoEntity {
  __typename
  id
  duration
  caption
  originCaption
  likeCount
  viewCount
  commentCount
  realLikeCount
  coverUrl
  photoUrl
  photoH265Url
  manifest
  manifestH265
  videoResource
  coverUrls {
    url
    __typename
  }
  timestamp
  expTag
  animatedCoverUrl
  distance
  videoRatio
  liked
  stereoType
  profileUserTopPhoto
  musicBlocked
  riskTagContent
  riskTagUrl
}

fragment recoPhotoFragment on recoPhotoEntity {
  __typename
  id
  duration
  caption
  originCaption
  likeCount
  viewCount
  commentCount
  realLikeCount
  coverUrl
  photoUrl
  photoH265Url
  manifest
  manifestH265
  videoResource
  coverUrls {
    url
    __typename
  }
  timestamp
  expTag
  animatedCoverUrl
  distance
  videoRatio
  liked
  stereoType
  profileUserTopPhoto
  musicBlocked
  riskTagContent
  riskTagUrl
}

fragment feedContent on Feed {
  type
  author {
    id
    name
    headerUrl
    following
    headerUrls {
      url
      __typename
    }
    __typename
  }
  photo {
    ...photoContent
    ...recoPhotoFragment
    __typename
  }
  canAddComment
  llsid
  status
  currentPcursor
  tags {
    type
    name
    __typename
  }
  __typename
}

fragment photoResult on PhotoResult {
  result
  llsid
  expTag
  serverExpTag
  pcursor
  feeds {
    ...feedContent
    __typename
  }
  webPageArea
  __typename
}

query brilliantTypeDataQuery($pcursor: String, $hotChannelId: String, $page: String, $webPageArea: String) {
  brilliantTypeData(pcursor: $pcursor, hotChannelId: $hotChannelId, page: $page, webPageArea: $webPageArea) {
    ...photoResult
    __typename
  }
}
""" 

data={
"operationName":"brilliantTypeDataQuery",
"query":query_str,


"variables":{
    "hotChannelId": "00", 
     "page": "brilliant"}  


}

url="https://v2.kwaicdn.com/ksc2/Zn59Wmf4MYON4kz8fr_QJWY5MTqZpVvs_Ba41nkfd3FXQLsGq_BXbRKzGB_e31DYm-ZgrUkBGDvxZ1OYSH6GR-QJgO5s6g76l4AfErviF21thlnRB6q_aIwrQLvP2Ir1.mp4?pkey=AAXGgeHHpfonzTyDudCw5WX7PLlmsD6zMM78SYZUbHogmxmD3bSuMQMe_GKp_9SLwd1yf0rAxYfYNyxpwoMrqtTFmkXYEPeLLSzZ1h7-t7sX8166HNl8o4daX3j3RzGIQN4&tag=1-1724114031-unknown-0-twbavrjvq3-a28575b3c09105d2&clientCacheKey=3x2azq4b76n5b5c_1953b5a7&di=JA4DjYcLzwB1RAoZC5KpEw==&bp=10004&tt=hd15&ss=vp"

response = requests.get(url)
# response = requests.post(url, headers=headers, data=data,verify=False)
if response.status_code!= 200:
    print("下载失败")
    exit()
# print(response.text)
    
with open("快手.mp4", "wb") as f:
    f.write(response.content)
print("下载完毕")