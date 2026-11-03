#pragma once
#include <cstddef>
#include <istream>
#include <set>
#include <string>
#include <stdexcept>
#include <utility>

inline bool read_pitch_requests(std::istream &input,std::size_t hop,std::set<std::size_t> &output)
{
    output.clear();
    if (!hop) return false;
    std::set<std::size_t> parsed;
    long long previous=0;
    std::string token;
    while (input>>token) {
        long long value=0;std::size_t used=0;
        try { value=std::stoll(token,&used); }
        catch (const std::exception &) { return false; }
        if (used!=token.size()) return false;
        if (value<=previous || value<=0 || static_cast<unsigned long long>(value)%hop) return false;
        parsed.insert(static_cast<std::size_t>(value));previous=value;
    }
    if (!input.eof()) return false;
    output=std::move(parsed);
    return true;
}
