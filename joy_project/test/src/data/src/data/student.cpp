
#include "data/student.h"

//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_DATA_BEGIN_
void Person::print() const {
    std::cout << "Name: " << name_ << "\n";
    std::cout << "Age: " << age_ << "\n";
}

void Student::print() const {
    Person::print();
    std::cout << "Score: " << score_ << "\n\n";  // 版本2新增打印
}







_DATA_END_