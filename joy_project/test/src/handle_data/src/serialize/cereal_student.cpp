
#include "handle_data/serialize/cereal_student.h"
#include <fstream>
#include <cereal/archives/json.hpp>
#include <cereal/types/memory.hpp>
#include <memory>
//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_HANDLE_DATA_BEGIN_



void test_save()
{
    using namespace DATA;
    std::ofstream os("F:/test/joy_project/test/test/data/joy_utility/student_1.json");
    cereal::JSONOutputArchive archive(os);
    std::shared_ptr <Person> student = std::make_shared<Student>("Alice", 20, 89);  // 版本1没有 score
    archive(student);

    std::cout << "Deserialized v1 data with v2 class:\n";
    student->print();  // 应输出默认的 score=0.0
}

void test_load()
{
    using namespace DATA;
    std::ifstream is("F:/test/joy_project/test/test/data/joy_utility/student_1.json");
    cereal::JSONInputArchive archive(is);
    std::shared_ptr<Person> student;  // 版本2的类
    archive(student);
    std::cout << "Deserialized v1 data with v2 class:\n";
    student->print();  // 应输出默认的 score=0.0
}








_HANDLE_DATA_END_