
#include "joy_utility/kenels/harchive.h"
#include "joy_utility/kenels/hobject.h"
#ifdef _DEBUG
#define new DEBUG_NEW
#endif
_JOY_UTILITY_BEGIN_


HArchive& HArchive::operator<<(HObject* obj) {
    if (mode_ == Store) {
        const char* className = obj->GetRuntimeClass()->className_;
        *this << className; // 写入类名
        obj->Serialize(*this); // 写入对象数据
    }
    return *this;
}

HArchive& HArchive::operator>>(HObject*& obj) {
    if (mode_ == Load) {
        std::string className;
        *this >> className; // 读取类名
        obj = HRuntimeClass::CreateObject(className.c_str()); // 动态创建
        if (obj) obj->Serialize(*this); // 加载数据
    }
    return *this;
}
HArchive& HArchive::operator<<(int value)
{
    return *this;
}
HArchive& HArchive::operator<<(double value)
{
    return *this;
}
HArchive& HArchive::operator<<(long double value)
{
    return *this;
}
HArchive& HArchive::operator<<(size_t value)
{
    return *this;
}
HArchive& HArchive::operator<<(std::string value)
{
    return *this;
}
HArchive& HArchive::operator<<(bool value)
{
    return *this;
}
HArchive& HArchive::operator<<(float value)
{
    return *this;
}
HArchive& HArchive::operator<<(char value)
{
    return *this;
}
HArchive& HArchive::operator<<(unsigned value)
{
    return *this;
}
HArchive& HArchive::operator<<(const char* value)
{
    return *this;
}


HArchive& HArchive::operator>>(int& value)
{
    return *this;
}
HArchive& HArchive::operator>>(double& value)
{
    return *this;
}
HArchive& HArchive::operator>>(long double& value)
{
    return *this;
}
HArchive& HArchive::operator>>(size_t& value)
{
    return *this;
}
HArchive& HArchive::operator>>(std::string& value)
{
    return *this;
}
HArchive& HArchive::operator>>(bool& value)
{
    return *this;
}
HArchive& HArchive::operator>>(float& value)
{
    return *this;
}
HArchive& HArchive::operator>>(char& value)
{
    return *this;
}
HArchive& HArchive::operator>>(unsigned& value)
{
    return *this;
}
HArchive& HArchive::operator>>(char*& value)
{
    return *this;
}

void HArchive::Read(void* value, size_t count)
{

}
void HArchive::Write(const void* value, size_t max_count)
{

}
bool HArchive::IsLoading() const
{
    return mode_ == Mode::Load;
}
bool HArchive::IsStoring() const
{
    return mode_ == Mode::Store;
}
HArchive& HArchive::operator<<(unsigned char value)
{
    return *this;
}
HArchive& HArchive::operator<<(wchar_t value)
{
    return *this;
}
HArchive& HArchive::operator<<(short value)
{
    return *this;
}
HArchive& HArchive::operator<<(unsigned short value)
{
    return *this;
}
HArchive& HArchive::operator<<(long value)
{
    return *this;
}
HArchive& HArchive::operator<<(unsigned long value)
{
    return *this;
}
HArchive& HArchive::operator<<(__int64 value)
{
    return *this;
}

HArchive& HArchive::operator>>(unsigned char& value)
{
    return *this;
}
HArchive& HArchive::operator>>(wchar_t& value)
{
    return *this;
}
HArchive& HArchive::operator>>(short& value)
{
    return *this;
}
HArchive& HArchive::operator>>(unsigned short& value)
{
    return *this;
}
HArchive& HArchive::operator>>(long& value)
{
    return *this;
}
HArchive& HArchive::operator>>(unsigned long& value)
{
    return *this;
}
HArchive& HArchive::operator>>(__int64& value)
{
    return *this;
}



_JOY_UTILITY_END_