

#include <gtest/gtest.h>

int main(int argc, char* argv[]) {
    //logger::AI_LOG_Init("recognition", "./data/log/test-ai-recognition.log");

    // 输出格式
    // testing::GTEST_FLAG(output) = "xml:";

    // 过滤去， TEST(fs_test, framework_test)
    //   filter使用正则匹配  如: fs_tes*
    //std::string testingFilter{ "joy_utility*" };
    std::string testingFilter{"test_cereal*"};
    testing::GTEST_FLAG(filter) = testingFilter;


    testing::InitGoogleTest(&argc, argv);

    return RUN_ALL_TESTS();
}