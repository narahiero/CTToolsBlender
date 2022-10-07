#include "KCLBuilder.hpp"


CTLib::KCL buildKCL(CTLib::Buffer& data)
{
    uint32_t count = data.getInt();
    CTLib::Buffer vertData = data.slice().limit(count * 0x24);
    CTLib::Buffer flagData = data.position(data.position() + vertData.remaining()).slice().limit(count * 0x02);

    return CTLib::KCL::fromModel(vertData, flagData, count);
}
