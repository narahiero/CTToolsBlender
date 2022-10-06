#include "KMPBuilder.hpp"


#include <CTLib/Utilities.hpp>


CTLib::KMP buildKMP(CTLib::Buffer& data)
{
    CTLib::KMP kmp;

    CTLib::KMP::STGI* stgi = kmp.add<CTLib::KMP::STGI>();
    data.get(); // track slot
    stgi->setLapCount(data.get());
    stgi->setStartSide(data.get() ? CTLib::KMP::STGI::StartSide::Right : CTLib::KMP::STGI::StartSide::Left);
    data.get(); // padding

    CTLib::KMP::KTPT* ktpt = kmp.add<CTLib::KMP::KTPT>();
    ktpt->setPosition({data.getFloat(), data.getFloat(), data.getFloat()});
    ktpt->setRotation({data.getFloat(), data.getFloat(), data.getFloat()});

    return kmp;
}
