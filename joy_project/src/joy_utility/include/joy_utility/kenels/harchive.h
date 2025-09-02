#pragma once
#ifndef __JOY_UTILITY_HARCHIVE_H__
#define __JOY_UTILITY_HARCHIVE_H__
#include <iostream>
#include <string>
#include "joy_utility/joy_utility_macro.h"




_JOY_UTILITY_BEGIN_
using namespace std;
class HObject;

class JOY_UTILITY_API HArchive {
public:
    enum Mode { Load, Store };

    HArchive(std::iostream& stream, Mode mode) : stream_(stream), mode_(mode) {}
    
    void Read(void* value, size_t count);
    void Write(const void* value, size_t max_count);
    bool IsLoading() const;
    bool IsStoring() const;


    // 基础类型序列化
    HArchive& operator<<(int value);
    HArchive& operator<<(double value);
    HArchive& operator<<(long double value);
    HArchive& operator<<(size_t value);
    HArchive& operator<<(std::string value);
    HArchive& operator<<(bool value);
    HArchive& operator<<(float value);
    HArchive& operator<<(char value);
    HArchive& operator<<(unsigned value);
    HArchive& operator<<(const char* value);
    HArchive& operator<<(unsigned char value);
    HArchive& operator<<(wchar_t value);
    HArchive& operator<<(short value);
    HArchive& operator<<(unsigned short value);
    HArchive& operator<<(long value);
    HArchive& operator<<(unsigned long value);
    HArchive& operator<<(__int64 value);


    HArchive& operator>>(int& value);
    HArchive& operator>>(double& value);
    HArchive& operator>>(long double& value);
    HArchive& operator>>(size_t& value);
    HArchive& operator>>(std::string& value);
    HArchive& operator>>(bool& value);
    HArchive& operator>>(float& value);
    HArchive& operator>>(char& value);
    HArchive& operator>>(unsigned& value);
    HArchive& operator>>(char*& value);
    HArchive& operator>>(unsigned char& value);
    HArchive& operator>>(wchar_t& value);
    HArchive& operator>>(short& value);
    HArchive& operator>>(unsigned short& value);
    HArchive& operator>>(long& value);
    HArchive& operator>>(unsigned long& value);
    HArchive& operator>>(__int64& value);


    // 对象序列化
    HArchive& operator<<(HObject* obj);
    HArchive& operator>>(HObject*& obj);


private:
    Mode mode_;
    std::iostream& stream_;
};








_JOY_UTILITY_END_
#endif
