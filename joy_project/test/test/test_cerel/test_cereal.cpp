#include <gtest/gtest.h>
#include <fstream>
#include <cereal/archives/json.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <memory>


#include "handle_data/serialize/cereal_student.h"
using namespace DATA;


auto file_path = environment::GlobalEnvironment::GetTestDataPath() / "joy_utility" / "student.json";

// 模拟：用版本1的类序列化数据
void serialize() {
    std::shared_ptr < Person> student=std::make_shared<Student> ("Alice", 20,89);  // 版本1没有 score
    std::ofstream os(file_path);
    cereal::JSONOutputArchive archive(os);
    archive(CEREAL_NVP(student));
}

// 用版本2的类反序列化版本1的数据
void deserialize() {
    std::ifstream is(file_path);
    cereal::JSONInputArchive archive(is);
    
    std::shared_ptr<Person> student;  // 版本2的类
    archive( student);

    std::cout << "Deserialized student:\n";
    student->print();  // 应输出默认的 score=0.0
}



TEST(test_cereal,serialize ) {

    serialize();              // 生成版本1的数据
    deserialize();    // 用版本2的类读取版本1的数据

    HANDLE_DATA::test_save();
    HANDLE_DATA::test_load();

}