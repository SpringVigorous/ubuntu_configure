#pragma once
#ifndef __HANDLE_DATA_CEREAL_STUDENT_H__
#define __HANDLE_DATA_CEREAL_STUDENT_H__
#include "utilities/cereal_macro.h"

#include <cereal/cereal.hpp>
#include <cereal/types/polymorphic.hpp>
#include <cereal/types/string.hpp>
#include "data/student.h"
#include "handle_data/handle_data_macro.h"


// 版本控制：升级为版本1（每次变更递增）
CEREAL_CLASS_VERSION(DATA::Person, 1);

CEREAL_CLASS_VERSION(DATA::Student, 1);
CEREAL_REGISTER_TYPE(DATA::Student);
CEREAL_REGISTER_POLYMORPHIC_RELATION(DATA::Person, DATA::Student);


CEREAL_SERIALIZE_FRIEND_IMPLEMENT(DATA::Person) {

    CEREAL_SERIALIZE_FRIEND_FIELDS(

        CEREAL_NVP_("name", data.name_),
        CEREAL_NVP_("age", data.age_)
    );
}

CEREAL_SERIALIZE_FRIEND_IMPLEMENT(DATA::Student) {

    CEREAL_SERIALIZE_FRIEND_FIELDS(
        cereal::base_class<DATA::Person>(&data),
        CEREAL_NVP_("score", data.score_)
    );
}



_HANDLE_DATA_BEGIN_


HANDLE_DATA_API void test_save();
HANDLE_DATA_API void test_load();





_HANDLE_DATA_END_
#endif
