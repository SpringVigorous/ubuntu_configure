#include "environment.hxx"
namespace environment {

GlobalEnvironment* env = reinterpret_cast<environment::GlobalEnvironment*>(
    ::testing::AddGlobalTestEnvironment(new environment::GlobalEnvironment()));

std::filesystem::path GlobalEnvironment::GetTestDataPath() {
    return GlobalEnvironment::GetProjectFolder().append("test").append("data");
}

std::filesystem::path GlobalEnvironment::GetProjectFolder() {
    return std::filesystem::path(PROJECT_FOLDER);
}

void GlobalEnvironment::SetUp() {
    GTEST_LOG_(INFO) << "Global environment setup";
}

void GlobalEnvironment::TearDown() {
    GTEST_LOG_(INFO) << "Global environment teardown";
}

}; // namespace environment