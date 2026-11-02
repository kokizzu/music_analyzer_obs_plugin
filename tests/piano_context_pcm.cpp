#include "native_timbre_features.hpp"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <vector>

int main(int argc,char **argv)
{
    if (argc!=4) return 2;
    const unsigned rate=std::stoul(argv[2]);
    if (rate!=16000 && rate!=44100 && rate!=48000) return 2;
    std::ifstream input(argv[1],std::ios::binary);std::ofstream output(argv[3]);
    if (!input || !output) return 3;
    const auto hop=std::size_t(std::lround(rate*.05)),count=std::size_t(std::lround(rate*.1));
    std::vector<float> fresh(hop),window(count,0);
    mao::timbre::CepstralExtractor extractor;
    output<<"end_sample\tmfcc_valid";
    for (int i=0;i<24;++i) output<<"\tmfcc"<<i;
    output<<'\n'<<std::setprecision(17);
    std::size_t end=0;
    while (input.read(reinterpret_cast<char *>(fresh.data()),hop*sizeof(float))) {
        for (float value:fresh) if (!std::isfinite(value)) return 4;
        end+=hop;
        std::move(window.begin()+hop,window.end(),window.begin());
        std::copy(fresh.begin(),fresh.end(),window.end()-hop);
        mao::timbre::Cepstra values{};
        const bool valid=extractor.extract(window.data(),window.size(),rate,values);
        output<<end<<'\t'<<valid;
        for (double value:values) output<<'\t'<<value;
        output<<'\n';
    }
    return input.eof() && end ? 0 : 5;
}
