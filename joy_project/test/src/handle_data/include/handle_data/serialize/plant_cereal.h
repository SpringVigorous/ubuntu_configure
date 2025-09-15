
#pragma once
#ifndef __HANDLE_DATA_PLANT_CEREAL_H__
#define __HANDLE_DATA_PLANT_CEREAL_H__
#include <cereal/types/polymorphic.hpp>
#include "data/plant.h"
// 注册多态类型（必须）
CEREAL_REGISTER_TYPE(DATA::Flower);
CEREAL_REGISTER_TYPE(DATA::Tree);
CEREAL_REGISTER_POLYMORPHIC_RELATION(DATA::Plant, DATA::Flower);
CEREAL_REGISTER_POLYMORPHIC_RELATION(DATA::Plant, DATA::Tree);

CEREAL_SERIALIZE_FRIEND_IMPLEMENT(DATA::Plant) {

    CEREAL_SERIALIZE_FRIEND_FIELDS(

        CEREAL_NVP_("age",data.age)
    );
}
CEREAL_SERIALIZE_FRIEND_IMPLEMENT(DATA::Flower) {

    CEREAL_SERIALIZE_FRIEND_FIELDS(
        cereal::base_class<DATA::Plant>(&data),
        CEREAL_NVP_("breed",data.breed)
    );
}

CEREAL_SERIALIZE_FRIEND_IMPLEMENT(DATA::Tree) {

    CEREAL_SERIALIZE_FRIEND_FIELDS(
        cereal::base_class<DATA::Plant>(&data),
        CEREAL_NVP_("hasLongHair",data.hasLongHair)
    );
}
#endif