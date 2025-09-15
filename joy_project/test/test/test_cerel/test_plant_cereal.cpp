#include <gtest/gtest.h>
#include <fstream>
#include <cereal/archives/json.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <memory>
#include "handle_data/serialize/plant_cereal.h"
#include "utilities/cereal_utility.h"
// 模拟：用版本1的类序列化数据



TEST(test_cereal, serialize_plant) {

    // 序列化
    std::shared_ptr<DATA::Plant> plant = std::make_unique<DATA::Flower>(3, "Sun Flower");
    UTILITIES::save_data_to_json(plant, "plant.json");
    UTILITIES::save_data_to_xml(plant, "plant.xml");
    UTILITIES::save_data_to_binary(plant, "plant.bin");


    // 反序列化
    std::shared_ptr<DATA::Plant> load_plant;
    UTILITIES::load_data_from_json(load_plant, "plant.json");
    load_plant->grow(); // 验证多态行为

    UTILITIES::load_data_from_xml(load_plant, "plant.xml");
    load_plant->grow(); // 验证多态行为


    UTILITIES::load_data_from_binary(load_plant, "plant.bin");
    load_plant->grow(); // 验证多态行为

}