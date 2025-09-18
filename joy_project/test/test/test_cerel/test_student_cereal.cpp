#include <gtest/gtest.h>
#include <fstream>
#include <cereal/archives/json.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <memory>


#include "handle_data/serialize/student_cereal.h"
#include <utilities/cereal_wrapper.h>
#include "utilities/cereal_utility.h"
#include "cereal_triple.h"

using namespace DATA;




TEST(test_cereal,serialize ) {

    std::shared_ptr < Person> student = std::make_shared<Student>("Alice", 20, 89);  // 版本1没有 score
    auto data = cereal_triple(student, "student");
    data->print();

    auto student_obj = cereal_triple(*data, "student_obj");
    student_obj.print();

}