from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector


def detect_change(video_path,diff_time=.05):
    
    
    # 初始化
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=27.0))

    # 处理视频
    video_manager.set_downscale_factor(2)
    video_manager.start()
    scene_manager.detect_scenes(video_manager)
    
    # 获取结果
    scene_list = scene_manager.get_scene_list()
    timestamps = [scene[0].get_seconds() for scene in scene_list]
    
    # 保存结果
    # scene_manager.save_to_csv("scene_list.csv", scene_list)
    
    return [time-diff_time for time in timestamps[1:]]

if __name__ == "__main__":
    detect_change()