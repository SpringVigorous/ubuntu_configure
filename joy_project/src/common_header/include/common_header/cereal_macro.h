#pragma once
#ifndef __COMMON_HEADER_CEREAL_MACRO_H__
#define __COMMON_HEADER_CEREAL_MACRO_H__
#include <cereal/cereal.hpp> // 引入cereal核心头文件（关键）

//类前声明，没有命名空间
#define CEREAL_SERIALIZE_PRE_DECLEAR(DATA_CLASS) \
class DATA_CLASS; \
namespace cereal { \
template <class Archive> \
void serialize (Archive& ar, DATA_CLASS& data, std::uint32_t version); \
}

//类前声明，有命名空间

#define CEREAL_SERIALIZE_PRE_DECLEAR_(NAMESPACE,DATA_CLASS) \
namespace NAMESPACE{ \
class DATA_CLASS; \
}; \
namespace cereal { \
template <class Archive> \
void serialize (Archive& ar, NAMESPACE::DATA_CLASS& data, std::uint32_t version); \
}

//类内声明
#define CEREAL_SERIALIZE_DECLEAR(DATA_CLASS) \
friend class cereal::access; \
template <class Archive> \
friend void ::cereal::serialize(Archive& ar, DATA_CLASS& data, std::uint32_t version);



//实现（带命名空间eg: std::string）
#define CEREAL_SERIALIZE_IMPLEMENT(DATA_CLASS) \
namespace cereal { \
template <class Archive> \
void serialize(Archive& ar, DATA_CLASS& data, std::uint32_t version)



//包装参数
#define CEREAL_SERIALIZE_FIELDS(...) \
    ar(__VA_ARGS__); \
}
/* namespace cereal */




#endif
