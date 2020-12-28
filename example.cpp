#include <iostream>
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/multiprecision/random.hpp>
#include <time.h>

// using namespace boost::multiprecision;

int main()
{
    boost::random::mt19937 gen((int)time(0));
    boost::random::uniform_int_distribution<boost::multiprecision::uint128_t> dist(0, boost::multiprecision::uint128_t(1) << 64);

    for (int i = 0; i < 10; ++i)
    {
        boost::multiprecision::uint128_t x = dist(gen);
        std::cout << x << std::endl;
    }
}