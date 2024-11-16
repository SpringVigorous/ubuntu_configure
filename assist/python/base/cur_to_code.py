
from clipboard import from_clipboard,to_clipboard

import requests

def curl_to_code(curl:str):

    cookies = {
        'Hm_lvt_75a21f203d323a988b1d8ce0eeae4de5': '1731668744',
        'Hm_lpvt_75a21f203d323a988b1d8ce0eeae4de5': '1731668744',
        'HMACCOUNT': '03AD22591AF7EB0C',
        '__gads': 'ID=a7eda3cd79aef42b:T=1723627833:RT=1731668794:S=ALNI_MaY248IzuDFV37-Lxe06flYgo6nAA',
        '__gpi': 'UID=00000ebecfa2bb08:T=1723627833:RT=1731668794:S=ALNI_MYtT6_Bx3Ga_deVvFaAyr1bROv6oQ',
        '__eoi': 'ID=ddf07f466f896aed:T=1723627833:RT=1731668794:S=AA-AfjaB-VDRYr-v9WWfnky_l7MI',
        'OUTFOX_SEARCH_USER_ID_NCOO': '361024416.9672013',
    }

    headers = {
        'authority': 'www.lddgo.net',
        'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="94"',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/json;charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
        'sec-ch-ua-platform': '"Android"',
        'origin': 'https://www.lddgo.net',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.lddgo.net/convert/curl-to-code',
        'accept-language': 'zh-CN,zh;q=0.9',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'Hm_lvt_75a21f203d323a988b1d8ce0eeae4de5=1731668744; Hm_lpvt_75a21f203d323a988b1d8ce0eeae4de5=1731668744; HMACCOUNT=03AD22591AF7EB0C; __gads=ID=a7eda3cd79aef42b:T=1723627833:RT=1731668794:S=ALNI_MaY248IzuDFV37-Lxe06flYgo6nAA; __gpi=UID=00000ebecfa2bb08:T=1723627833:RT=1731668794:S=ALNI_MYtT6_Bx3Ga_deVvFaAyr1bROv6oQ; __eoi=ID=ddf07f466f896aed:T=1723627833:RT=1731668794:S=AA-AfjaB-VDRYr-v9WWfnky_l7MI; OUTFOX_SEARCH_USER_ID_NCOO=361024416.9672013',
    }

    json_data = {
        'code': curl,
        'lang': 'python',
    }

    response = requests.post('https://www.lddgo.net/api/CurlGenerateCode', cookies=cookies, headers=headers, json=json_data)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应内容为 JSON 格式
        data = response.json().get("data")
        return data
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        
        
if __name__=='__main__':
#     curl="""curl 'https://www.lddgo.net/api/CurlGenerateCode' \
#   -H 'authority: www.lddgo.net' \
#   -H 'sec-ch-ua: ";Not A Brand";v="99", "Chromium";v="94"' \
#   -H 'accept: application/json, text/javascript, */*; q=0.01' \
#   -H 'content-type: application/json;charset=UTF-8' \
#   -H 'x-requested-with: XMLHttpRequest' \
#   -H 'sec-ch-ua-mobile: ?1' \
#   -H 'user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36' \
#   -H 'sec-ch-ua-platform: "Android"' \
#   -H 'origin: https://www.lddgo.net' \
#   -H 'sec-fetch-site: same-origin' \
#   -H 'sec-fetch-mode: cors' \
#   -H 'sec-fetch-dest: empty' \
#   -H 'referer: https://www.lddgo.net/convert/curl-to-code' \
#   -H 'accept-language: zh-CN,zh;q=0.9' \
#   -H 'cookie: Hm_lvt_75a21f203d323a988b1d8ce0eeae4de5=1731668744; Hm_lpvt_75a21f203d323a988b1d8ce0eeae4de5=1731668744; HMACCOUNT=03AD22591AF7EB0C; __gads=ID=a7eda3cd79aef42b:T=1723627833:RT=1731668794:S=ALNI_MaY248IzuDFV37-Lxe06flYgo6nAA; __gpi=UID=00000ebecfa2bb08:T=1723627833:RT=1731668794:S=ALNI_MYtT6_Bx3Ga_deVvFaAyr1bROv6oQ; __eoi=ID=ddf07f466f896aed:T=1723627833:RT=1731668794:S=AA-AfjaB-VDRYr-v9WWfnky_l7MI; OUTFOX_SEARCH_USER_ID_NCOO=361024416.9672013' \
#   --data-raw $'{"code":"curl \'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes\' \\\\\\n  -H \'accept: application/json, text/plain, */*\' \\\\\\n  -H \'accept-language: zh-CN,zh;q=0.9\' \\\\\\n  -H \'content-type: application/json;charset=UTF-8\' \\\\\\n  -H \'cookie: acw_tc=0ad520dd17316761461776835ec16f35fdc95b61d13555278934c1a49dea26; abRequestId=4582f617-d60c-5959-b862-cb93ba8e4725; webBuild=4.43.0; xsecappid=xhs-pc-web; a1=1932ff0f0acn4wjzm6sx23fubf0u68si1jlb49s0s50000103754; webId=6f204f98f1ce886ad830d1b734dc6b02; websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; sec_poison_id=b3bc1eaf-0274-4712-ac24-fe2e1f188930; gid=yjqJiiySJ2yfyjqJii8i8VjM0SI4EVu6KMCJ18Mqi7Di8D287KYM34888y8qW248KK4Sdi0J; web_session=040069b26ead56dc3c1f450002354bbc3f32f1; unread={%22ub%22:%22672cbac2000000001901abcd%22%2C%22ue%22:%2267302fe7000000001b02ac08%22%2C%22uc%22:13}\' \\\\\\n  -H \'origin: https://www.xiaohongshu.com\' \\\\\\n  -H \'priority: u=1, i\' \\\\\\n  -H \'referer: https://www.xiaohongshu.com/\' \\\\\\n  -H \'sec-ch-ua: \\"Not;A=Brand\\";v=\\"24\\", \\"Chromium\\";v=\\"128\\"\' \\\\\\n  -H \'sec-ch-ua-mobile: ?0\' \\\\\\n  -H \'sec-ch-ua-platform: \\"Windows\\"\' \\\\\\n  -H \'sec-fetch-dest: empty\' \\\\\\n  -H \'sec-fetch-mode: cors\' \\\\\\n  -H \'sec-fetch-site: same-site\' \\\\\\n  -H \'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36\' \\\\\\n  -H \'x-b3-traceid: 70302c0b25a033f1\' \\\\\\n  -H \'x-s: XYW_eyJzaWduU3ZuIjoiNTUiLCJzaWduVHlwZSI6IngyIiwiYXBwSWQiOiJ4aHMtcGMtd2ViIiwic2lnblZlcnNpb24iOiIxIiwicGF5bG9hZCI6ImY5MTcwZGZkMGYyY2Q4ZjMxMGQ1MmU3MmFmZmFhOWI5YWYxMmJiODhkZTY1MGI4MjE0ZjU3MGE1MWZhNDAzNTIyNGQ1ZmU4ZTA4MjExNWUwZmU4ZjQ0YzY4YjgwYjhiNzVhMWUwYWQ2M2E4NmFjNDg3NjVmODEyOTJkMjdlMzE0Y2RjNDZhNDYxODI0NzVjZDFjOWQ4MTQ3NDNiZTExMGM3OTI0YTM3YjhkMzczYmQyYmFiMTgyZmUwOTUxYjRmMjY0MjM4NGYxNDcwNDM2NzJhMjkxZWViNjEwZTI0ODg0ZTI5ZjU2MGQ4YTY0ZGU3OGI3OWRhZjg1NWYwZTQ4NzY3OTZlZDg4MTdhNjdmODhiNjUzZjBlYWY2YTJlYjE1ODQ4ZjFiZDFkYmI2ZjA0ZDRhNmIxMzQ2YjA3YzRmOTM4ZWZlNWVkMjBhYzIyZDdjZTM5YzFjYzBjODM1NzUzOWY2NTE4NDdkNGUyZDAwOGNlODM5MjBmODdjNGJhOWVkZDFhNTU1Y2JkYjljMTM5N2U1MjVlODI2N2YxOWE4N2VkIn0=\' \\\\\\n  -H \'x-s-common: 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\' \\\\\\n  -H \'x-t: 1731676213630\' \\\\\\n  -H \'x-xray-traceid: c997f9087145082c57436fa8fa9bffbc\' \\\\\\n  --data-raw \'{\\"keyword\\":\\"静坐\\",\\"page\\":1,\\"page_size\\":20,\\"search_id\\":\\"2e101st40we794n7govud\\",\\"sort\\":\\"general\\",\\"note_type\\":0,\\"ext_flags\\":[],\\"image_formats\\":[\\"jpg\\",\\"webp\\",\\"avif\\"]}\'","lang":"python"}' \
#   --compressed"""
  
  
    curl=from_clipboard()
    code=curl_to_code(curl)
    print(code)
    to_clipboard(code)