#include <gtest/gtest.h>
#include <fstream>
#include <cereal/archives/json.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <memory>
#include "animal_cereal.h"

// 模拟：用版本1的类序列化数据



TEST(test_cereal, serialize_temp) {

    // 序列化
    std::unique_ptr<Animal> pet = std::make_unique<Dog>(3, "Husky");


    {
        std::ofstream os("pet.json");
        cereal::JSONOutputArchive archive(os);
        archive(pet);
    }

    // 反序列化
    std::unique_ptr<Animal> loadedPet;
    {
        std::ifstream is("pet.json");
        cereal::JSONInputArchive archive(is);
        archive(loadedPet);
    }

    loadedPet->speak(); // 验证多态行为

}