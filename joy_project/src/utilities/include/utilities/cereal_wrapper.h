#pragma once
#ifndef __UTILITIES_CEREAL_WRAPPER_H__
#define __UTILITIES_CEREAL_WRAPPER_H__
#include <cereal/cereal.hpp> // 引入cereal核心头文件（关键）
#include <functional> // 用于 std::reference_wrapper
#include "utilities/utilities_macro.h"
#include <type_traits>
#include "joy_utility/tools/string_tools.h"
_UTILITIES_BEGIN_
// 主模板，接受任何类型 T
template <typename T>
struct AutoConvertGbk {
    std::reference_wrapper<T> value; // 使用 reference_wrapper 替代直接引用

    // 默认构造函数（必需）
    AutoConvertGbk() : value(std::ref(*static_cast<T*>(nullptr))) {} // 需要提供一个无效的默认状态
    // 但更安全的做法是使用指针并检查，或者确保不会用到默认构造的对象

    // 带参数的构造函数
    explicit AutoConvertGbk(T& val) : value(std::ref(val)) {}

    // 提供一个方法来获取真实的引用（在序列化函数中使用）
    T& get() const { return value.get(); }
};
template <typename T>
AutoConvertGbk<T> make_auto_convert(T& value) {
    return AutoConvertGbk<T>(value);

};
// 为 AutoConvertGbk<T> 特化 cereal 的序列化函数
_UTILITIES_END_
#define USE_AUTO_CONVERT_GBK



#ifdef USE_AUTO_CONVERT_GBK
    #define SERIALIZE_NVP_(name, value) ::cereal::make_nvp(JOY_UTILITY::string_tools::gbk_to_utf8(name), ::UTILITIES::make_auto_convert(value))
#else
    #define SERIALIZE_NVP_(name, value) CEREAL_NVP_(name,value)
#endif // 

#define SERIALIZE_NVP(T) SERIALIZE_NVP_(#T,T)

namespace cereal {
    // save 函数（序列化：内存 -> 存档）
    template <class Archive, typename T>
    void save(Archive& archive, const UTILITIES::AutoConvertGbk<T>& wrapper) {
        // 使用 if constexpr 在编译期判断类型是否为 std::string
        if constexpr (std::is_same_v<std::remove_cv_t<T>, std::string>) {
            // 对于 std::string 类型：进行 GBK -> UTF-8 转换
            std::string utf8Str = JOY_UTILITY::string_tools::gbk_to_utf8(wrapper.get());
            archive(utf8Str);
        }
        else {
            // 对于其他所有类型：直接序列化原始值
            archive(wrapper.get());
        }
    }

    // load 函数（反序列化：存档 -> 内存）
    template <class Archive, typename T>
    void load(Archive& archive, UTILITIES::AutoConvertGbk<T>& wrapper) {
        if constexpr (std::is_same_v<std::remove_cv_t<T>, std::string>) {
            // 对于 std::string 类型：先读到临时 UTF-8 字符串，然后转换回 GBK
            std::string utf8Str;
            archive(utf8Str);
            wrapper.get() = JOY_UTILITY::string_tools::utf8_to_gbk(utf8Str);
        }
        else {
            // 对于其他所有类型：直接反序列化到原始对象
            archive(wrapper.get());
        }
    }

} // namespace cereal






#endif