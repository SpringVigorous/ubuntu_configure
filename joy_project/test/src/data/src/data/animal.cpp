
#include "data/animal.h"

//#ifdef _DEBUG
//#define new DEBUG_NEW
//#endif
_DATA_BEGIN_
void Animal::speak() const {};

void Dog::speak() const  {
    std::cout << "Woof! Age:" << age << " Breed:" << breed << "\n";
}

void Cat::speak() const  {
    std::cout << "Meow! Age:" << age << " LongHair:" << hasLongHair << "\n";
}



_DATA_END_