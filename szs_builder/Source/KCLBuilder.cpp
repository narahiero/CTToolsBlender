#include "KCLBuilder.hpp"


#include <CTLib/Utilities.hpp>


void appendObject(CTLib::Buffer& data, CTLib::Buffer& vertData, CTLib::Buffer& flagData)
{
    uint32_t count = data.getInt();
    uint16_t flag = data.getShort();
    data.getShort(); // padding

    data.limit(data.position() + count * 0x24);
    vertData.put(data);

    for (uint32_t tri = 0; tri < count; ++tri)
    {
        flagData.putShort(flag);
    }
}

CTLib::KCL buildKCL(CTLib::Buffer& data)
{
    uint32_t count = data.getInt();
    uint32_t faceCount = data.getInt();
    CTLib::Buffer vertData(faceCount * 0x24);
    CTLib::Buffer flagData(faceCount * 0x02);
    CTLib::Buffer objData = data.duplicate();
    for (uint32_t i = 0; i < count; ++i)
    {
        uint32_t dataOff = data.getInt();
        objData.position(dataOff);
        appendObject(objData.slice(), vertData, flagData);
    }

    return CTLib::KCL::fromModel(vertData.flip(), flagData.flip(), faceCount);
}
