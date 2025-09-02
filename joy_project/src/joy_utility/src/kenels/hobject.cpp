
#include "joy_utility/kenels/hobject.h"
#include "joy_utility/kenels/harchive.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#endif
_JOY_UTILITY_BEGIN_

HRuntimeClass::HRuntimeClass(const char* name, const char* base_class, ObjFunc func) : className_(name), baseClassName_(base_class), createObject(func)
{
    HRuntimeClass::RegisterRuntimeClass(name, this);
}

const HRuntimeClass* HRuntimeClass::BaseRuntimeClass()const
{
    if (baseClassName_)
        return nullptr;
    return GetRuntimeClassByName(baseClassName_);
}
// 类型继承关系检查
bool HRuntimeClass::IsDerivedFrom(const HRuntimeClass* target) const {
    const HRuntimeClass* cls = this;
    while (cls) {
        if (cls == target) return true;
        cls = cls->BaseRuntimeClass();
    }
    return false;
}
const HRuntimeClass* HRuntimeClass::GetRuntimeClassByName(const std::string& class_name)
{
    if (class_name.empty())
        return nullptr;

    auto it = HRuntimeClass::classMap.find(class_name);
    return it != classMap.end() ? it->second : nullptr;
}

bool HRuntimeClass::ExistName(const std::string& className)
{
    return HRuntimeClass::classMap.find(className)!= classMap.end();
}

HObject* HRuntimeClass::CreateObject(const std::string& className) {
    auto class_time = HRuntimeClass::GetRuntimeClassByName(className);
    auto func = class_time !=nullptr? class_time->createObject : nullptr;
    return func != nullptr ? func() : nullptr;
}

void HRuntimeClass::RegisterRuntimeClass(const std::string& class_name, HRuntimeClass* class_ptr)
{
    if (class_name.empty() || class_ptr == nullptr)
        return;
    if (HRuntimeClass::ExistName(class_name))
    {
        //重复
        std::cout << "注册类时，类名重复" << class_name << std::endl;
        return;
    }
    std::cout << "注册类" << class_name << std::endl;
    HRuntimeClass::classMap[class_name] = class_ptr;
}

const HRuntimeClass* HObject::GetRuntimeClass() const
{
    return &HObject::classHObject;
}

bool HObject::Serialize(HArchive& ar)
{
    return true;
}
std::string HObject::GetClassName() const
{
    return HObject::class_name_;
}
const HRuntimeClass HObject::classHObject={ "HObject", nullptr, nullptr };

_JOY_UTILITY_END_