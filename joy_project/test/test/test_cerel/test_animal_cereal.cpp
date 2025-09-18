#include <gtest/gtest.h>
#include <fstream>
#include <memory>
#include <cereal/archives/json.hpp>
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include "data/animal.h"
#include "handle_data/serialize/animal_cereal.h"
#include "utilities/cereal_utility.h"
#include "cereal_triple.h"

// 模拟：用版本1的类序列化数据



TEST(test_cereal, serialize_animal) {


    // 序列化
    std::unique_ptr<DATA::Animal> animal = std::make_unique<DATA::Dog>(3, "Husky");
    auto data = cereal_triple(animal, "animal");

    data->speak();


    auto animal_obj = cereal_triple(*data, "animal_obj");
    animal_obj.speak();
}