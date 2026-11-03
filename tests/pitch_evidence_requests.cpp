#include "pitch_evidence_requests.hpp"
#include <cassert>
#include <sstream>
#include <string>

int main()
{
    std::set<std::size_t> values;
    std::istringstream valid("2000\n3000\n");
    assert(read_pitch_requests(valid,1000,values) && values==std::set<std::size_t>({2000,3000}));
    for (const auto *text:{"3000 2000","2000 2000","-1","0","1500","2000 bad","2000 2.5"}) {
        std::istringstream invalid(text);
        assert(!read_pitch_requests(invalid,1000,values) && values.empty());
    }
    std::istringstream empty("");
    assert(read_pitch_requests(empty,1000,values) && values.empty());
    std::istringstream overflow("999999999999999999999999999999999999999");
    if (read_pitch_requests(overflow,1000,values)) return 12;
}
