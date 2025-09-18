#include <gtest/gtest.h>
#include <fstream>
#include <cereal/archives/json.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <memory>
#include "handle_data/serialize/plant_cereal.h"
#include "utilities/cereal_utility.h"

#include "cereal_triple.h"

TEST(test_cereal, serialize_plant) {

    // 序列化
    std::shared_ptr<DATA::Plant> plant = std::make_shared<DATA::Flower>(3, "太阳花");

    auto data= std::dynamic_pointer_cast<DATA::Flower>(cereal_triple(plant, "plant"));
    data->grow();

    auto plant_obj = cereal_triple(*data, "plant_obj");
    plant_obj.grow();

}