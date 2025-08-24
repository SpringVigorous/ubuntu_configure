#include "ds_devops.hxx"

#include <gtest/gtest.h>
#include <logger/logger.h>

using namespace std;

#ifdef ENABLE_PROFILER
#include <gperftools/profiler.h>

class ProfileHoler {
public:
    explicit ProfileHoler(const std::string& file) {
        ProfilerStart(file.c_str()); // 指定所生成的profile文件名
    }
    ~ProfileHoler() {
        ProfilerStop(); // 结束profiling
    }
};
#else
class ProfileHoler {
public:
    explicit ProfileHoler(const std::string& file) {}
    ~ProfileHoler() {}
};
#endif

void test_profile() {
    { ProfileHoler p("./my.prof"); }
}

int main(int argc, char* argv[]) {
    logger::AI_LOG_Init("recognition", "./data/log/test-ai-recognition.log");

    // 输出格式
    // testing::GTEST_FLAG(output) = "xml:";

    // 过滤去， TEST(fs_test, framework_test)
    //   filter使用正则匹配  如: fs_tes*
    std::string testingFilter{"close_polyline_test*"};
    testing::GTEST_FLAG(filter) = testingFilter;
    devops::GetTestingFilter(testingFilter);

    testing::InitGoogleTest(&argc, argv);

    return RUN_ALL_TESTS();
}