#pragma once
#ifndef __JOY_UTILITY_HOBJECT_H__
#define __JOY_UTILITY_HOBJECT_H__
#include <map>
#include <string>
#include "joy_utility/joy_utility_macro.h"
#include "joy_utility/kenels/harchive.h"


_JOY_UTILITY_BEGIN_
class HArchive;
class HObject;
class JOY_UTILITY_API HRuntimeClass {

public:
    typedef HObject* (*ObjFunc)();
public:
    HRuntimeClass(const char* name, const char* base_class, ObjFunc func);
public:
    // 类型继承关系检查
    bool IsDerivedFrom(const HRuntimeClass* target) const;
    static HObject* CreateObject(const std::string& className);
    static void RegisterRuntimeClass(const std::string& class_name, HRuntimeClass* base_class);
    const HRuntimeClass* BaseRuntimeClass()const;

    static const HRuntimeClass* GetRuntimeClassByName(const std::string& class_name);

    static bool ExistName(const std::string& className);
public:

    const char* className_ = {};
    const char* baseClassName_ = {};

    HObject* (*createObject)() = {}; // 动态创建函数

    // 全局类注册表
    inline static std::map<std::string, HRuntimeClass*> classMap{};
};
class JOY_UTILITY_API HObject {

public:
    virtual const HRuntimeClass* GetRuntimeClass() const;
    virtual bool Serialize(HArchive& ar);
    virtual ~HObject() = default;
    virtual std::string GetClassName()const;

    // 动态类型检查与转换
    template <typename T>
    static T* DynamicCast(HObject* obj) {
        return (obj && obj->GetRuntimeClass()->IsDerivedFrom(T::GetThisRuntimeClass()))
            ? static_cast<T*>(obj) : nullptr;
    }
public:
    inline static const char* class_name_{ "HObject" };
    static const HRuntimeClass classHObject;
};



// 声明运行时信息（头文件）
#define DECLARE_RUNTIME_CLASS(className) \
public: \
    inline static const char* class_name_= #className; \
    inline std::string GetClassName() const  override { return #className; } \
    static const HRuntimeClass class##className; \
    static HObject* CreateObject(); \
    virtual const HRuntimeClass* GetRuntimeClass() const override; \
    static const HRuntimeClass* GetThisRuntimeClass();


// 实现运行时信息（源文件）
#define IMPLEMENT_RUNTIME_CLASS(className, baseClassName) \
    HObject* className::CreateObject() { return new className(); } \
    const HRuntimeClass className::class##className = { \
        #className, \
        baseClassName::##class_name_, \
        className::CreateObject \
    }; \
    const HRuntimeClass* className::GetThisRuntimeClass() { return &className::class##className;} \
    /*HRuntimeClass::RegisterRuntimeClass(#className, &className::class##className);*/ \
    const HRuntimeClass* className::GetRuntimeClass() const { return &className::class##className; }







// 序列化支持
#define DECLARE_SERIAL(className) \
    DECLARE_RUNTIME_CLASS(className) \
    virtual bool Serialize(HArchive& ar);

#define IMPLEMENT_SERIAL(className, baseClassName) \
    IMPLEMENT_RUNTIME_CLASS(className, baseClassName) \
    bool className::Serialize(HArchive& ar) { \
        baseClassName::Serialize(ar); \
        if (ar.IsStoring()) { /* 存储数据 */ } \
        else { /* 加载数据 */ } \
        return true; \
    }









_JOY_UTILITY_END_
#endif
