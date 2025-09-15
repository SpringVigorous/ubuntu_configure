#pragma once
#ifndef __HANDLE_DATA_ANIMAL_CEREAL_H__
#define __HANDLE_DATA_ANIMAL_CEREAL_H__

#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>

#include "data/animal.h"
// 注册多态类型（必须）
CEREAL_REGISTER_TYPE(DATA::Dog);
CEREAL_REGISTER_TYPE(DATA::Cat);
CEREAL_REGISTER_POLYMORPHIC_RELATION(DATA::Animal, DATA::Dog);
CEREAL_REGISTER_POLYMORPHIC_RELATION(DATA::Animal, DATA::Cat);


_DATA_BEGIN_

CEREAL_SERIALIZE_MEMBER_IMPLEMENT(Animal) {

    CEREAL_SERIALIZE_MEMBER_FIELDS(

        CEREAL_NVP(age)
    );
}
CEREAL_SERIALIZE_MEMBER_IMPLEMENT(Dog) {

    CEREAL_SERIALIZE_MEMBER_FIELDS(
        cereal::base_class<DATA::Animal>(this),
        CEREAL_NVP(breed)
    );
}

CEREAL_SERIALIZE_MEMBER_IMPLEMENT(Cat) {

    CEREAL_SERIALIZE_MEMBER_FIELDS(
        cereal::base_class<DATA::Animal>(this),
        CEREAL_NVP(hasLongHair)
    );
}
_DATA_END_
#endif