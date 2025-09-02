#pragma once
#ifndef __JOY_UTILITY_TEMPLATE_UTILITY_H__
#define __JOY_UTILITY_TEMPLATE_UTILITY_H__
#include <type_traits>
#include "joy_utility/joy_utility_macro.h"




_JOY_UTILITY_BEGIN_


// 递归处理：先移除所有指针，再处理其他修饰符
//template <typename T>
//struct raw_type {
//private:
//    // 第一步：递归移除所有指针（处理多级指针）
//    // 若T是指针类型，则先移除一级指针，再递归处理剩余部分
//    using no_ptr = std::conditional_t<
//        std::is_pointer_v<T>,
//        typename raw_type<std::remove_pointer_t<T> >::type,
//        T  // 若不是指针，直接保留原类型
//    >;
//
//    // 第二步：移除引用（& 或 &&）
//    using no_ref = std::remove_reference_t<no_ptr>;
//
//    // 第三步：移除const
//    using no_const = std::remove_const_t<no_ref>;
//
//    // 第四步：移除volatile
//    using no_volatile = std::remove_volatile_t<no_const>;
//
//public:
//    // 最终类型
//    using type = no_volatile;
//};
// 基础模板：递归终止
template <typename T>
struct raw_type {
    using type = T;
};

// 特化：处理指针
template <typename T>
struct raw_type<T*> {
    using type = typename raw_type<T>::type;
};

// 扩展：处理引用、const、volatile
template <typename T>
struct raw_type<T&> {
    using type = typename raw_type<T>::type;
};

template <typename T>
struct raw_type<const T> {
    using type = typename raw_type<T>::type;
};

template <typename T>
struct raw_type<volatile T> {
    using type = typename raw_type<T>::type;
};
// 简化使用的模板别名
template <typename T>
using raw_type_t = typename raw_type<T>::type;

/*
// 基础类型测试
static_assert(std::is_same_v<raw_type_t<int>, int>, "int 测试失败");

// 指针测试（一级、多级）
static_assert(std::is_same_v<raw_type_t<int*>, int>, "int* 测试失败");
static_assert(std::is_same_v<raw_type_t<int**>, int>, "int** 测试失败");
static_assert(std::is_same_v<raw_type_t<int*** const>, int>, "int***const 测试失败");

// 混合引用、const、volatile测试
static_assert(std::is_same_v<raw_type_t<const int&>, int>, "const int& 测试失败");
static_assert(std::is_same_v<raw_type_t<volatile int*&>, int>, "volatile int*& 测试失败");
static_assert(std::is_same_v<raw_type_t<const volatile int**&&>, int>, "const volatile int**&& 测试失败");
*/


// 通用模板宏（基础功能）
#define HAS_MEM_FUNC_BASE(func_name) \
template <typename T, typename... Args> \
struct has_##func_name##_impl { \
    static constexpr bool value = requires(T a, Args... args) { \
        a.func_name(args...); \
    }; \
}; \
template <typename T, typename... Args> \
inline constexpr bool has_##func_name##_v = has_##func_name##_impl<T, Args...>::value;

//带参数的成员函数
#define HAS_MEM_FUNC_WITH_ARGS(func_name,lat,...) \
    /*HAS_MEM_FUNC_BASE(func_name)*/ \
    template <typename T> \
    inline constexpr bool has_##func_name##_##lat##_v = has_##func_name##_v<T,__VA_ARGS__>;


#define HAS_MEM_FUNC_BASE_WITH_ARGS(func_name,lat,...) \
    HAS_MEM_FUNC_BASE(func_name) \
    HAS_MEM_FUNC_WITH_ARGS(func_name,lat,__VA_ARGS__)


//不带参数的成员函数
#define HAS_MEM_FUNC_NO_ARGS(func_name,lat) \
    /*HAS_MEM_FUNC_BASE(func_name)*/ \
    template <typename T> \
    inline constexpr bool has_##func_name##_##lat##_v = has_##func_name##_v<T>;



#define HAS_MEM_FUNC_BASE_NO_ARGS(func_name,lat) \
    HAS_MEM_FUNC_BASE(func_name) \
    HAS_MEM_FUNC_NO_ARGS(func_name,lat)


_JOY_UTILITY_END_
#endif
