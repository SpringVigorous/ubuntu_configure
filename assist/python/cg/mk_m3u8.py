


def sec_str(durations:list,sec=10):
    start=durations[-1]
    end=start+sec
    
    results=[f"#EXTINF:{sec},",f"http://vali01.cp31.ott.cibntv.net/657313A8E084A721DF9902951/03000B010067FBB5BED26659BC3635D50C8015-451A-435D-BD40-D842CEB56A8B.mp4.ts?ccode=0502&duration=18&expire=18000&psid=d39e6ceaf35627fd93fd710eeb2ae5f241346&ups_client_netip=240exb8fx3175x4f00xc868x9fa3x8ebdx4d25&ups_ts=1751615233&ups_userid=3760073884&apscid=&mnid=&umt=2&type=mp4&utid=ArEsIEQEnkgCAWVd%2FGueTwU3&vid=XNjQ3NDkzMzgxNg%3D%3D&t=70e2fd6b4cb4209&cug=2&bc=2&si=565&eo=1&ckt=5&m_onoff=0&vkey=B94e93900bd7037b244739eb2a09f9e08&fms=4a0396ae8216c1d5&tr=18&le=36853a6e4af7225bc3d827013538c3fd&app_key=24679788&app_ver=9.5.72&ts_start={start:03}&ts_end={end:03}&ts_seg_no=1&ts_keyframe=1"]
    durations.append(end)
    return "\n".join(results)

if __name__ == "__main__":
    
    
    from base import worm_root
    durations=[11.733,18.833]
    with open(worm_root/r"player\m3u8/durations.txt","w") as f:
        while durations[-1]<8640:
            f.write(sec_str(durations,10)+"\n")
