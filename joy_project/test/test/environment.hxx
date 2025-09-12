#pragma once

#include <gtest/gtest.h>
#include <filesystem>

namespace environment {

#ifndef PROJECT_FOLDER
#error "Need a macro PROJECT_FOLDER for unit test environment!!!"
#endif

class GlobalEnvironment : public ::testing::Environment {
public:
    ~GlobalEnvironment() override {}

    /**
     * @brief 全局测试数据路径
     *
     * \return std::filesystem::path
     */
    static std::filesystem::path GetTestDataPath();

    /**
     * @brief 测试工程根目录
     *
     * \return std::filesystem::path
     */
    static std::filesystem::path GetProjectFolder();

    /**
     * @brief 全局事件开始处理
     */
    void SetUp() override;

    /**
     * @brief 全局事件结束处理
     *
     */
    void TearDown() override;
};
extern environment::GlobalEnvironment* env;
} // namespace environment