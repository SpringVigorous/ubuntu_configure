#include <gtest/gtest.h>
#include <fstream>
#include <memory>
#include <cereal/archives/json.hpp>
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include "data/animal.h"
#include "handle_data/serialize/animal_cereal.h"
#include "environment.hxx"
#include "utilities/cereal_utility.h"

// 模拟：用版本1的类序列化数据



TEST(test_cereal, serialize_animal) {


    // 序列化
    std::unique_ptr<DATA::Animal> animal = std::make_unique<DATA::Dog>(3, "Husky");

    UTILITIES::save_data_to_json(animal, "animal.json");


    // 反序列化
    std::unique_ptr<DATA::Animal> loadedPet;
    UTILITIES::load_data_from_json(loadedPet, "animal.json");


    loadedPet->speak(); // 验证多态行为

}