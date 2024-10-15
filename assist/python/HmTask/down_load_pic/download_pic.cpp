#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <filesystem>
#include <curl/curl.h> // libcurl
#include <cimg/CImg.h> // CImg library for image processing
#include <spdlog/spdlog.h> // spdlog for logging
#include <inih/ini.h> // inih for reading INI files

// 日志初始化
void init_logging() {
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    auto logger = std::make_shared<spdlog::logger>("app_logger", console_sink);
    spdlog::register_logger(logger);
    spdlog::set_level(spdlog::level::info);
}

// 从配置文件读取配置项
struct Config {
    std::string download_dir;
    std::string final_dir;
    int max_download_workers;
    int max_conversion_workers;
};

Config read_config(const std::string& config_path) {
    Config config;
    ini_parse(config_path.c_str(), [](void* user, const char* section, const char* name, const char* value) {
        Config* cfg = static_cast<Config*>(user);
        if (!strcmp(section, "directories")) {
            if (!strcmp(name, "download_dir")) {
                cfg->download_dir = value;
            } else if (!strcmp(name, "final_dir")) {
                cfg->final_dir = value;
            }
        } else if (!strcmp(section, "threading")) {
            if (!strcmp(name, "max_download_workers")) {
                cfg->max_download_workers = std::stoi(value);
            } else if (!strcmp(name, "max_conversion_workers")) {
                cfg->max_conversion_workers = std::stoi(value);
            }
        }
    }, &config);
    return config;
}

size_t write_data(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// 下载文件
bool download_file(const std::string& url, const std::string& local_path) {
    CURL* curl;
    CURLcode res;
    std::string readBuffer;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if (curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        if (res == CURLE_OK) {
            std::ofstream file(local_path);
            if (file.is_open()) {
                file << readBuffer;
                file.close();
                spdlog::info("下载完成: {}", local_path);
                return true;
            }
        }
    }
    spdlog::error("下载失败: {} -> {}, 错误: {}", url, local_path, curl_easy_strerror(res));
    return false;
}

// 转换并添加文字
void convert_and_add_text(const std::string& src_path, const std::string& final_path) {
    CImg<unsigned char> image(src_path.c_str());
    if (image.is_empty()) {
        spdlog::error("无法打开图片: {}", src_path);
        return;
    }

    // 这里省略了具体的文字添加逻辑，可以参考Python版本实现细节
    // ...

    image.save(final_path.c_str());
    spdlog::info("转换并添加文字完成: {}", final_path);
}

// 任务队列
class TaskQueue {
public:
    void push(Task task) {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_queue.push(std::move(task));
        m_condition.notify_one();
    }

    Task pop() {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_condition.wait(lock, [this] { return !m_queue.empty(); });
        Task task = std::move(m_queue.front());
        m_queue.pop();
        return task;
    }

private:
    std::queue<Task> m_queue;
    std::mutex m_mutex;
    std::condition_variable m_condition;
};

// 生产者线程
void producer_thread(const std::vector<std::string>& urls, const std::vector<std::string>& names, TaskQueue& task_queue, const Config& config) {
    for (size_t i = 0; i < urls.size(); ++i) {
        std::string file_name = names[i] + ".jpg";
        std::string cur_path = config.download_dir + "/" + file_name;
        std::string final_path = config.final_dir + "/" + file_name;

        if (std::filesystem::exists(final_path)) {
            spdlog::info("最终文件已存在: {}", final_path);
            continue;
        }

        if (std::filesystem::exists(cur_path)) {
            task_queue.push([cur_path, final_path]() { convert_and_add_text(cur_path, final_path); });
        } else {
            if (download_file(urls[i], cur_path)) {
                task_queue.push([cur_path, final_path]() { convert_and_add_text(cur_path, final_path); });
            }
        }
    }
}

// 消费者线程
void consumer_thread(TaskQueue& task_queue) {
    while (true) {
        auto task = task_queue.pop();
        task();
    }
}

int main() {
    init_logging();
    Config config = read_config("config.ini");

    // 创建必要的目录
    std::filesystem::create_directories(config.download_dir);
    std::filesystem::create_directories(config.final_dir);

    // 示例数据
    std::vector<std::string> urls = {"http://example.com/image1.jpg", "http://example.com/image2.jpg"};
    std::vector<std::string> names = {"image1", "image2"};

    TaskQueue task_queue;
    std::thread producer(producer_thread, urls, names, std::ref(task_queue), config);
    std::thread consumer(consumer_thread, std::ref(task_queue));

    producer.join();
    consumer.join();

    spdlog::info("所有任务已完成");
    return 0;
}