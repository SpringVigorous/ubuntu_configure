#include <gtest/gtest.h>
#include <fstream>
#include <cereal/archives/json.hpp>
#include "environment.hxx"
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <memory>
#include "animal.h"
// 注册多态类型（必须）
CEREAL_REGISTER_TYPE(Dog);
CEREAL_REGISTER_TYPE(Cat);
CEREAL_REGISTER_POLYMORPHIC_RELATION(Animal, Dog);
CEREAL_REGISTER_POLYMORPHIC_RELATION(Animal, Cat);

CEREAL_SERIALIZE_IMPLEMENT(Animal) {

    CEREAL_SERIALIZE_FIELDS(

        CEREAL_NVP_("age", data.age)
    );
}
CEREAL_SERIALIZE_IMPLEMENT(Dog) {

    CEREAL_SERIALIZE_FIELDS(
        cereal::base_class<Animal>(&data),
        CEREAL_NVP_("breed", data.breed)
    );
}

CEREAL_SERIALIZE_IMPLEMENT(Cat) {

    CEREAL_SERIALIZE_FIELDS(
        cereal::base_class<Animal>(&data),
        CEREAL_NVP_("hasLongHair", data.hasLongHair)
    );
}

