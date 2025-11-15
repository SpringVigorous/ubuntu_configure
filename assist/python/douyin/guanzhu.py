import requests
from pathlib import Path
import os
import sys





from base import logger_helper,UpdateTimeType,exception_decorator,convert_seconds_to_datetime



import json
import time
import pandas as pd

@exception_decorator(error_state=False)
def transform_data(item):
    image_url=item["avatar_168x168"]["url_list"][0]
    name=item["nickname"]
    id=item["unique_id"]
    short_id=item["short_id"]
    #关注
    following_count=item["following_count"]
    #粉丝
    follower_count=item["follower_count"]
    #获赞
    total_favorited=item["total_favorited"]
    #签名
    signature=item["signature"]
    # #最火
    # favoriting_count=item['favoriting_count']
    #是否关注
    aweme_hotsoon_auth=item["aweme_hotsoon_auth"]
    #是否反向关注
    aweme_hotsoon_auth_relation=item["aweme_hotsoon_auth_relation"]
    #主页二维码
    qrcodes=item["share_info"]["share_qrcode_url"]["url_list"]
    qrcode=qrcodes[0] if qrcodes else ""
    #主页
    domain=f"https://www.douyin.com/user/{item["sec_uid"]}"
    
    
    create_time=item["create_time"]
    if create_time:
        create_time=convert_seconds_to_datetime(create_time)

    data={"image_url":image_url,"name":name,"id":id,"following_count":following_count,
        "follower_count":follower_count,"total_favorited":total_favorited,"signature":signature,
        "aweme_hotsoon_auth":aweme_hotsoon_auth,"aweme_hotsoon_auth_relation":aweme_hotsoon_auth_relation,
        "create_time":create_time,"short_id":short_id,"qrcode":qrcode,"domain":domain}

    return data


def get_raw_data(url,params,headers,logger):
    index=0
    org_datas=[]
    while True:
        params['offset']=str(index*20)
        logger.update_target(detail=f"第{index}页")
        
        index+=1
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200 or not response.text:
            break
        json_data = json.loads(response.text)

        #头像
        flags=["followings","followers"]
        flags=list(filter(lambda x:x in json_data,flags))
        if not flags:
            logger.error("没有对应的关键词", f"\n{json.dumps(json_data,ensure_ascii=False,indent=4)}\n")
            break
            
        items=json_data[flags[0]]
        org_datas.extend(items)
        logger.info("完成",update_time_type=UpdateTimeType.STAGE)
        
        if not json_data["has_more"]:
            break
        time.sleep(.2)
    logger.info("完成",f"一共{index}页",update_time_type=UpdateTimeType.ALL)
    return org_datas

def handle_data(url,params,headers,flag,root_dir):
    logger=logger_helper(flag)
    logger.info("开始",update_time_type=UpdateTimeType.ALL)
    
    
    json_path=os.path.join(root_dir,f"{flag}.json")
    
    raw_datas=[]
    has_json=os.path.exists(json_path)
    if has_json:
        raw_datas=json.load(open(json_path,"r",encoding="utf-8"))
    else:
        raw_datas=get_raw_data(url,params,headers,logger)

        
    dest_datas=[transform_data(item) for item in raw_datas if item]
    if not dest_datas:
        logger.error("获取数据为空")    

    df=pd.DataFrame(dest_datas)
    df.sort_values("follower_count",ascending=False,inplace=True)
    df.to_excel(os.path.join(root_dir,f"{flag}.xlsx"),index=False)
    if not has_json:
        json.dump(raw_datas,open(os.path.join(root_dir,f"{flag}.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=4)

if __name__=="__main__":
    from base import worm_root

    root_dir=worm_root/r"douyin\account"
    headers = {
    'authority': 'www.douyin.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'bd-ticket-guard-client-data': 'eyJ0c19zaWduIjoidHMuMi45YjA5ZjM2NTlkNzY1ZjFmZDQ1NjlkNjE4NWYyZDIzNTE4ZmMyYTAwN2Q0MDEwMmI2NzlmZGZmM2I2M2Q4YmU2YzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50IjoidGlja2V0LHBhdGgsdGltZXN0YW1wIiwicmVxX3NpZ24iOiJkK0kvRTJ3SlRhK0NRUVlaQUs5Nk9wVTdLTTlwbHhYdFRlNjU0UVVkQ3RFPSIsInRpbWVzdGFtcCI6MTc0MTkxOTg2Nn0=',
    'bd-ticket-guard-iteration-version': '1',
    'bd-ticket-guard-ree-public-key': 'BHcM+k0DutKx61E3iAZHOa/nnMGo/OGoyZsh4JpR9QUuW5s9Kg4QCiz+vSKp/lxxhqn+GbraLQQgfD3otRqqme8=',
    'bd-ticket-guard-version': '2',
    'bd-ticket-guard-web-sign-type': '1',
    'bd-ticket-guard-web-version': '2',
    'cookie': 'bd_ticket_guard_client_web_domain=2; ttwid=1%7CPHS-ukXhjUh0buv7IddEZhu72zvYXaN0YBUJR5yOufM%7C1709112103%7C875a4f0b6870e87207ef6c6211bfdc00c0be1fa2af93a69ec6fbb225d6015097; LOGIN_STATUS=1; store-region=cn-sh; store-region-src=uid; my_rd=2; SEARCH_RESULT_LIST_TYPE=%22single%22; UIFID_TEMP=472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9ebdf0a037dd20cf02ecdbbb01964d1929f63992db7b4394c07777ac4394bd936bb19c6ac816ac58a553d75f509525bb1f; fpk1=U2FsdGVkX19lcYhMqXHiaqPwX7ZY6BUQ7azSNxTvFVMYzNWR3xkeEWkGCFXasMwUsWTwZUldhyPpEK8ILduy1w==; fpk2=f1927cbd6567920810f3ecd89caad74c; UIFID=472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9e03fc3c822b38f8e5514d81038f415df7d713b0de5040913dd08cb686117b59a47a13ab9c0ec53ad5ca677002639ce976e7f859cf3e14821d186078ff64ab9142bc7eb8b7c7d7842c6009f69c3f50c8f4f59ec93e85d018f01102a64abe47ec0f61e5b00d82f32aed17a09df15ccb4c4808454f4c15ecd9fa863d33d3a60a98974e94fb28fb942ecc73242c3612d52981; OUTFOX_SEARCH_USER_ID_NCOO=1210883312.5400972; xgplayer_user_id=437247443906; xgplayer_device_id=4758127484; d_ticket=2abcca871187b4d78f2adf24087f04549270f; theme=%22light%22; s_v_web_id=verify_m6sw69uq_n4XHzZdS_Lj0H_4kap_BcK1_Us3i8nNeS8ms; douyin.com; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; hevc_supported=true; upgrade_tag=1; dy_swidth=2560; dy_sheight=1440; strategyABtestKey=%221741918881.253%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.828%7D; passport_csrf_token=7e319b205d8db1ef7b770da613d6667e; passport_csrf_token_default=7e319b205d8db1ef7b770da613d6667e; __security_mc_1_s_sdk_crypt_sdk=964b32a4-41fa-b9fa; __security_mc_1_s_sdk_cert_key=2ba6e225-40b5-a8fe; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; is_dash_user=1; passport_assist_user=CkEdExR8fxNomV0A3b17n_1i2QjcsUTPVBoA8OZEtj6Aa6q3r4lmY5nqwBwmFgIhN-wXQ-3lapHLIPDVu2MwvF6D3xpKCjwAAAAAAAAAAAAATsEfRYGJWa0A0jI_ZsiBiv5g2isguesOVI4L2-JAJFJ-hXFhI4ENVokXWoX7JBX1P04Qm_zrDRiJr9ZUIAEiAQPRAfLC; n_mh=TXbOOF1fR4E2u7muBaLLTlFSAVYRUVwUFu-BMWC9pXs; sid_guard=4e0035ebd5224732af451af5f1fe10cb%7C1741918901%7C5184000%7CTue%2C+13-May-2025+02%3A21%3A41+GMT; uid_tt=ad71104a53e3cff488e63a8ad3193f41; uid_tt_ss=ad71104a53e3cff488e63a8ad3193f41; sid_tt=4e0035ebd5224732af451af5f1fe10cb; sessionid=4e0035ebd5224732af451af5f1fe10cb; sessionid_ss=4e0035ebd5224732af451af5f1fe10cb; is_staff_user=false; sid_ucp_v1=1.0.0-KDZlMTFlMWZkODE0ZWUwNGY3MzU0NWMxOWZlYTlmYzFiMmFmMzUzZWUKIQj_9ZCCq_ThBRC1pc6-BhjvMSAMMKKLrPEFOAJA7wdIBBoCbGYiIDRlMDAzNWViZDUyMjQ3MzJhZjQ1MWFmNWYxZmUxMGNi; ssid_ucp_v1=1.0.0-KDZlMTFlMWZkODE0ZWUwNGY3MzU0NWMxOWZlYTlmYzFiMmFmMzUzZWUKIQj_9ZCCq_ThBRC1pc6-BhjvMSAMMKKLrPEFOAJA7wdIBBoCbGYiIDRlMDAzNWViZDUyMjQ3MzJhZjQ1MWFmNWYxZmUxMGNi; login_time=1741918901435; __ac_nonce=067d392b500ede87be461; __ac_signature=_02B4Z6wo00f01SwLNIQAAIDATwH078C2MwksKzAAACzUdDdIpwsngSPJ7aEo0czw.mu0THeHaKDgLw-9B87Jy1kyEkt89XuAw4IBVIEGpYn8gJSlMLwX5GidUm81CNigh.sIodfG-WLhZx4H86; _bd_ticket_crypt_cookie=80bd0b8294e593c403e51292745dcd45; __security_mc_1_s_sdk_sign_data_key_web_protect=e57ab0b3-4711-8fad; __security_server_data_status=1; biz_trace_id=22f37cc1; publish_badge_show_info=%220%2C0%2C0%2C1741918907509%22; SelfTabRedDotControl=%5B%7B%22id%22%3A%227205119286531082298%22%2C%22u%22%3A224%2C%22c%22%3A224%7D%5D; FRIEND_NUMBER_RED_POINT_INFO=%22MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3%2F1741968000000%2F1741919285684%2F0%2F0%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3%2F1741968000000%2F1741918910839%2F0%2F1741919886158%22; xg_device_score=7.088786818960461; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A1%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2560%2C%5C%22screen_height%5C%22%3A1440%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.35%2C%5C%22effective_type%5C%22%3A%5C%223g%5C%22%2C%5C%22round_trip_time%5C%22%3A550%7D%22; IsDouyinActive=true; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3%2F1741968000000%2F0%2F1741919859279%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSGNNK2swRHV0S3g2MUUzaUFaSE9hL25uTUdvL09Hb3lac2g0SnBSOVFVdVc1czlLZzRRQ2l6K3ZTS3AvbHh4aHFuK0dicmFMUVFnZkQzb3RScXFtZTg9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; passport_fe_beating_status=true; odin_tt=85fc72f54cb79eb78c112b61fd6ca4b5a2a8f2d6e8212bdbc7a1931900138f5fe95601453b8ce4e7abb0eff8a66f7bfdd044b54b29544b3225f58b2973973b94',
    'referer': 'https://www.douyin.com/user/self?from_tab_name=main&showTab=watch_later',
    'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'uifid': '472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9e03fc3c822b38f8e5514d81038f415df7d713b0de5040913dd08cb686117b59a47a13ab9c0ec53ad5ca677002639ce976e7f859cf3e14821d186078ff64ab9142bc7eb8b7c7d7842c6009f69c3f50c8f4f59ec93e85d018f01102a64abe47ec0f61e5b00d82f32aed17a09df15ccb4c4808454f4c15ecd9fa863d33d3a60a98974e94fb28fb942ecc73242c3612d52981',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
    }

    params = {
        'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
        'user_id': '3245357555530495',
        'sec_user_id': 'MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3',
        'offset': '40',
        'min_time': '0',
        'max_time': '0',
        'count': '20',
        'source_type': '4',
        'gps_access': '0',
        'address_book_access': '0',
        'is_top': '1',
        'update_version_code': '170400',
        'pc_client_type': '1',
        'pc_libra_divert': 'Windows',
        'support_h265': '1',
        'support_dash': '1',
        'version_code': '170400',
        'version_name': '17.4.0',
        'cookie_enabled': 'true',
        'screen_width': '2560',
        'screen_height': '1440',
        'browser_language': 'zh-CN',
        'browser_platform': 'Win32',
        'browser_name': 'Sogou Explorer',
        'browser_version': '1.0',
        'browser_online': 'true',
        'engine_name': 'Blink',
        'engine_version': '116.0.5845.97',
        'os_name': 'Windows',
        'os_version': '10',
        'cpu_core_num': '4',
        'device_memory': '8',
        'platform': 'PC',
        'downlink': '1.35',
        'effective_type': '3g',
        'round_trip_time': '550',
        'webid': '7320185968332424713',
        'uifid': '472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9e03fc3c822b38f8e5514d81038f415df7d713b0de5040913dd08cb686117b59a47a13ab9c0ec53ad5ca677002639ce976e7f859cf3e14821d186078ff64ab9142bc7eb8b7c7d7842c6009f69c3f50c8f4f59ec93e85d018f01102a64abe47ec0f61e5b00d82f32aed17a09df15ccb4c4808454f4c15ecd9fa863d33d3a60a98974e94fb28fb942ecc73242c3612d52981',
        'verifyFp': 'verify_m6sw69uq_n4XHzZdS_Lj0H_4kap_BcK1_Us3i8nNeS8ms',
        'fp': 'verify_m6sw69uq_n4XHzZdS_Lj0H_4kap_BcK1_Us3i8nNeS8ms',
        'msToken': 'wTd-2qVjwPtvrdsofGB1zmt90BbQ1L7We6desdkPNN2u0R71GzXkloGAWP8veGNK8kbFM_nbYvwD-ojU7zMGz3M0jtA1wMfQX-FlOlMnZ5IeQQd2MhScSrj8teT8VaF2t6_QhgA_TMzzq6soHvtfzTQOBSKiFa3aAm8UxvaFKF8uK6l6z7k=',
        'a_bogus': 'djURgqU7EZWccV/bYCOTS-KUE8dMrTuy9MiKWieTCOOPTXeGZbNjpccwaoq5DbwPC8psk917aVsMbjVcKsUsZoHpompkSiJWSUACnh8L0qwpPF0sDrfTeukxyJHbWOvEuAKSJAWU1U/a2xC4L3rzUQ-J9/Tr4mipKNaWdaRGP9tvgzs9BNFKuNSDOXFOBc24Bf==',
    }
    handle_data("https://www.douyin.com/aweme/v1/web/user/following/list/",params,headers,"关注",root_dir)




    headers1 = {
        'authority': 'www.douyin.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'bd_ticket_guard_client_web_domain=2; ttwid=1%7CPHS-ukXhjUh0buv7IddEZhu72zvYXaN0YBUJR5yOufM%7C1709112103%7C875a4f0b6870e87207ef6c6211bfdc00c0be1fa2af93a69ec6fbb225d6015097; LOGIN_STATUS=1; store-region=cn-sh; store-region-src=uid; my_rd=2; SEARCH_RESULT_LIST_TYPE=%22single%22; UIFID_TEMP=472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9ebdf0a037dd20cf02ecdbbb01964d1929f63992db7b4394c07777ac4394bd936bb19c6ac816ac58a553d75f509525bb1f; fpk1=U2FsdGVkX19lcYhMqXHiaqPwX7ZY6BUQ7azSNxTvFVMYzNWR3xkeEWkGCFXasMwUsWTwZUldhyPpEK8ILduy1w==; fpk2=f1927cbd6567920810f3ecd89caad74c; UIFID=472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9e03fc3c822b38f8e5514d81038f415df7d713b0de5040913dd08cb686117b59a47a13ab9c0ec53ad5ca677002639ce976e7f859cf3e14821d186078ff64ab9142bc7eb8b7c7d7842c6009f69c3f50c8f4f59ec93e85d018f01102a64abe47ec0f61e5b00d82f32aed17a09df15ccb4c4808454f4c15ecd9fa863d33d3a60a98974e94fb28fb942ecc73242c3612d52981; OUTFOX_SEARCH_USER_ID_NCOO=1210883312.5400972; xgplayer_device_id=4758127484; xgplayer_user_id=437247443906; d_ticket=2abcca871187b4d78f2adf24087f04549270f; theme=%22light%22; s_v_web_id=verify_m6sw69uq_n4XHzZdS_Lj0H_4kap_BcK1_Us3i8nNeS8ms; douyin.com; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; hevc_supported=true; upgrade_tag=1; dy_swidth=2560; dy_sheight=1440; strategyABtestKey=%221741918881.253%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.828%7D; passport_csrf_token=7e319b205d8db1ef7b770da613d6667e; passport_csrf_token_default=7e319b205d8db1ef7b770da613d6667e; __security_mc_1_s_sdk_crypt_sdk=964b32a4-41fa-b9fa; __security_mc_1_s_sdk_cert_key=2ba6e225-40b5-a8fe; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; is_dash_user=1; passport_assist_user=CkEdExR8fxNomV0A3b17n_1i2QjcsUTPVBoA8OZEtj6Aa6q3r4lmY5nqwBwmFgIhN-wXQ-3lapHLIPDVu2MwvF6D3xpKCjwAAAAAAAAAAAAATsEfRYGJWa0A0jI_ZsiBiv5g2isguesOVI4L2-JAJFJ-hXFhI4ENVokXWoX7JBX1P04Qm_zrDRiJr9ZUIAEiAQPRAfLC; n_mh=TXbOOF1fR4E2u7muBaLLTlFSAVYRUVwUFu-BMWC9pXs; sid_guard=4e0035ebd5224732af451af5f1fe10cb%7C1741918901%7C5184000%7CTue%2C+13-May-2025+02%3A21%3A41+GMT; uid_tt=ad71104a53e3cff488e63a8ad3193f41; uid_tt_ss=ad71104a53e3cff488e63a8ad3193f41; sid_tt=4e0035ebd5224732af451af5f1fe10cb; sessionid=4e0035ebd5224732af451af5f1fe10cb; sessionid_ss=4e0035ebd5224732af451af5f1fe10cb; is_staff_user=false; sid_ucp_v1=1.0.0-KDZlMTFlMWZkODE0ZWUwNGY3MzU0NWMxOWZlYTlmYzFiMmFmMzUzZWUKIQj_9ZCCq_ThBRC1pc6-BhjvMSAMMKKLrPEFOAJA7wdIBBoCbGYiIDRlMDAzNWViZDUyMjQ3MzJhZjQ1MWFmNWYxZmUxMGNi; ssid_ucp_v1=1.0.0-KDZlMTFlMWZkODE0ZWUwNGY3MzU0NWMxOWZlYTlmYzFiMmFmMzUzZWUKIQj_9ZCCq_ThBRC1pc6-BhjvMSAMMKKLrPEFOAJA7wdIBBoCbGYiIDRlMDAzNWViZDUyMjQ3MzJhZjQ1MWFmNWYxZmUxMGNi; login_time=1741918901435; _bd_ticket_crypt_cookie=80bd0b8294e593c403e51292745dcd45; __security_mc_1_s_sdk_sign_data_key_web_protect=e57ab0b3-4711-8fad; __security_server_data_status=1; biz_trace_id=22f37cc1; publish_badge_show_info=%220%2C0%2C0%2C1741918907509%22; SelfTabRedDotControl=%5B%7B%22id%22%3A%227205119286531082298%22%2C%22u%22%3A224%2C%22c%22%3A224%7D%5D; FRIEND_NUMBER_RED_POINT_INFO=%22MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3%2F1741968000000%2F1741919285684%2F0%2F0%22; xg_device_score=7.088786818960461; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A1%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2560%2C%5C%22screen_height%5C%22%3A1440%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; __ac_nonce=067d3b91500fc40f86092; __ac_signature=_02B4Z6wo00f01gV7F.AAAIDDZnHXmvn8SfoFWxNAAOabfMzWKSNKuM5k7-Ludi0FvZPi4Ip4mr1.yps8U6BtrL4kAmpAzMHiOZ5HzyPPcDxfsJ12ApwnxubeOwsWuQCB17P19jbdeXK0V9oL39; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3%2F1741968000000%2F1741918910839%2F0%2F1741929330613%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3%2F1741968000000%2F0%2F0%2F1741929930614%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSGNNK2swRHV0S3g2MUUzaUFaSE9hL25uTUdvL09Hb3lac2g0SnBSOVFVdVc1czlLZzRRQ2l6K3ZTS3AvbHh4aHFuK0dicmFMUVFnZkQzb3RScXFtZTg9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; passport_fe_beating_status=true; odin_tt=de09ac6b74304d3dfc640aa14f981a074efe9729891dc5db9b105af3e0e324da78a98a34557e5252cd79f9847a1758014eace588132f7763bdb3ae4b9fee7c31; IsDouyinActive=true',
        'referer': 'https://www.douyin.com/user/self?from_tab_name=main&showSubTab=video&showTab=record',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'uifid': '472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9e03fc3c822b38f8e5514d81038f415df7d713b0de5040913dd08cb686117b59a47a13ab9c0ec53ad5ca677002639ce976e7f859cf3e14821d186078ff64ab9142bc7eb8b7c7d7842c6009f69c3f50c8f4f59ec93e85d018f01102a64abe47ec0f61e5b00d82f32aed17a09df15ccb4c4808454f4c15ecd9fa863d33d3a60a98974e94fb28fb942ecc73242c3612d52981',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 SE 2.X MetaSr 1.0',
    }

    params1 = {
           'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
        'user_id': '3245357555530495',
        'sec_user_id': 'MS4wLjABAAAABjYRelWyXTvWpI_JlfSXLxhxvcPvbd1T3n7N8ol9Ee3C3yt9ql-RDZXUoGDwbN_3',
        'offset': '0',
        'min_time': '0',
        'max_time': '1711770962',
        'count': '20',
        'source_type': '1',
        'gps_access': '0',
        'address_book_access': '0',
        'update_version_code': '170400',
        'pc_client_type': '1',
        'pc_libra_divert': 'Windows',
        'support_h265': '1',
        'support_dash': '1',
        'version_code': '170400',
        'version_name': '17.4.0',
        'cookie_enabled': 'true',
        'screen_width': '2560',
        'screen_height': '1440',
        'browser_language': 'zh-CN',
        'browser_platform': 'Win32',
        'browser_name': 'Sogou Explorer',
        'browser_version': '1.0',
        'browser_online': 'true',
        'engine_name': 'Blink',
        'engine_version': '116.0.5845.97',
        'os_name': 'Windows',
        'os_version': '10',
        'cpu_core_num': '4',
        'device_memory': '8',
        'platform': 'PC',
        'downlink': '1.35',
        'effective_type': '3g',
        'round_trip_time': '550',
        'webid': '7320185968332424713',
        'uifid': '472e73c773772401d587cd97efff6f2584234e33118897fe4f447176c49f4fc1b90e37546bbfc5b63d4facdd55dedc9e03fc3c822b38f8e5514d81038f415df7d713b0de5040913dd08cb686117b59a47a13ab9c0ec53ad5ca677002639ce976e7f859cf3e14821d186078ff64ab9142bc7eb8b7c7d7842c6009f69c3f50c8f4f59ec93e85d018f01102a64abe47ec0f61e5b00d82f32aed17a09df15ccb4c4808454f4c15ecd9fa863d33d3a60a98974e94fb28fb942ecc73242c3612d52981',
        'verifyFp': 'verify_m6sw69uq_n4XHzZdS_Lj0H_4kap_BcK1_Us3i8nNeS8ms',
        'fp': 'verify_m6sw69uq_n4XHzZdS_Lj0H_4kap_BcK1_Us3i8nNeS8ms',
        'msToken': 'YcU6DbqptwL_EPQHzCjwmxzNYJSD37rZtL8udtYphBqjtHIr6aZ9s9BO0vIRUHQODGCyvuUythnKu72ZccIqSqDsrm9nCr9lmfvns14y0fuW1PUQh7gK4qXeoFOw4pPC6IHM_5vuLrwXLZULIZolhRkZpoPH0OrAt6qJ_PGNCvPwvHebx6o=',
        'a_bogus': 'O70VktULOdARPdFGmOmzH-3lKS9MrB8y7BTOWJOTSOOhT1lYLmP6pxbrJoq2iN1eebZskla7ui-AFnVb/0UiZu3pqshfSp7WUtA5ngmohqwpa0zsEHfkezmEHJab8mJE8QKWJ1Wf602OIDA4DZrzUQ5r7/TnsYvpOHabdcUax9efgF49FNq/uNSdxXFcBQ94wE==',
}


   
    
    handle_data("https://www.douyin.com/aweme/v1/web/user/follower/list/",params1,headers1,"粉丝",root_dir)
    




