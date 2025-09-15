#pragma once
#ifndef __UTILITIES_CEREAL_MACRO_H__
#define __UTILITIES_CEREAL_MACRO_H__
#include <cereal/cereal.hpp> // 引入cereal核心头文件（关键）


//-----------------------------友元函数方式-----------------------------
//类前声明，没有命名空间
#define CEREAL_SERIALIZE_FRIEND_PRE_DECLEAR(DATA_CLASS) \
class DATA_CLASS; \
namespace cereal { \
template <class Archive> \
void serialize (Archive& ar, DATA_CLASS& data, std::uint32_t version); \
}

//类前声明，有命名空间

#define CEREAL_SERIALIZE_FRIEND_PRE_DECLEAR_(NAMESPACE,DATA_CLASS) \
namespace NAMESPACE{ \
class DATA_CLASS; \
}; \
namespace cereal { \
template <class Archive> \
void serialize (Archive& ar, NAMESPACE::DATA_CLASS& data, std::uint32_t version); \
}

//类内声明
#define CEREAL_SERIALIZE_FRIEND_DECLEAR(DATA_CLASS) \
friend class ::cereal::access; \
template <class Archive> \
friend void ::cereal::serialize(Archive& ar, DATA_CLASS& data, std::uint32_t version);



//实现（带命名空间eg: std::string）
#define CEREAL_SERIALIZE_FRIEND_IMPLEMENT(DATA_CLASS) \
namespace cereal { \
template <class Archive> \
void serialize(Archive& ar, DATA_CLASS& data, std::uint32_t version)



//包装参数
#define CEREAL_SERIALIZE_FRIEND_FIELDS(...) \
    ar(__VA_ARGS__); \
}
/* namespace cereal */
//-----------------------------友元函数方式-----------------------------



//-----------------------------成员函数方式-----------------------------
//成员函数方式，声明
#define CEREAL_SERIALIZE_MEMBER_DECLEAR() \
friend class ::cereal::access; \
template <class Archive> \
void serialize(Archive& ar, std::uint32_t version);

//成员函数方式，定义
#define CEREAL_SERIALIZE_MEMBER_IMPLEMENT(DATA_CLASS) \
template <class Archive> \
void DATA_CLASS::serialize(Archive& ar, std::uint32_t version)

//包装参数
#define CEREAL_SERIALIZE_MEMBER_FIELDS(...) \
    ar(__VA_ARGS__); 
//-----------------------------成员函数方式-----------------------------

//-----------------------------友元类方式-----------------------------

#ifdef CEREAL_SERIALIZE_HELPER
namespace cereal {
// 前置声明主模板
template<class Archive, class T>
    class SerializeHelper;
template<class Archive,class T>
class SerializeHelper
{
    inline static void serialize_imp(Archive&ar ,T& data, std::uint32_t version)
    {
        // 默认行为：抛出一个异常或使用静态断言给出友好错误信息
        throw std::runtime_error("Serialization not implemented for this type.");

    }
};
template<class Archive, class T>
void serialize(Archive& ar, T& data, std::uint32_t version)
{
  SerializeHelper<Archive, T>::serialize_imp(ar, data, version);
};
}
#endif

#define CEREAL_SERIALIZE_FRIEND_CLASS_DECLEAR() \
friend class cereal::access; \
template<class Archive,class T> friend class ::cereal::SerializeHelper; 



#define CEREAL_SERIALIZE_FRIEND_CLASS_IMPLEMENT(DATA_CLASS) \
namespace cereal { \
template<class Archive> \
class SerializeHelper<Archive, DATA_CLASS> \
{ \
    inline static void serialize_imp(Archive& ar, DATA_CLASS& data, std::uint32_t version) 

//{ \
//} \
//}; \
//}

#define CEREAL_SERIALIZE_FRIEND_CLASS_FIELDS(...) \
    ar(__VA_ARGS__);  \
} \
}



//-----------------------------友元类方式-----------------------------





#endif
