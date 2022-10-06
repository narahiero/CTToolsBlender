#include "SZSBuilder.hpp"


#include <CTLib/U8.hpp>
#include <CTLib/Utilities.hpp>
#include <CTLib/Yaz.hpp>

#include "BRRESBuilder.hpp"
#include "KCLBuilder.hpp"
#include "KMPBuilder.hpp"


CTLib::Buffer buildArchive(CTLib::Buffer& data)
{
    size_t trackInfoOff = data.getInt();
    size_t modelsDataOff = data.getInt();
    size_t collisionDataOff = data.getInt();
    size_t stringTableOff = data.getInt();

    data.position(modelsDataOff);
    CTLib::Buffer modelsData = data.slice();
    size_t courseModelDataOff = modelsData.getInt();
    size_t skyboxModelDataOff = modelsData.getInt();

    data.position(stringTableOff);
    CTLib::Buffer stringTable = data.slice();

    CTLib::U8Arc arc;
    CTLib::U8Dir* root = arc.addDirectory(".");

    data.position(trackInfoOff);
    CTLib::KMP kmp = buildKMP(data.slice());
    CTLib::Buffer kmpData = CTLib::KMP::write(kmp);
    root->addFile("course.kmp")->setData(kmpData);

    modelsData.position(courseModelDataOff);
    CTLib::BRRES courseBrres = buildBRRES(modelsData.slice(), "course", stringTable);
    CTLib::Buffer courseBrresData = CTLib::BRRES::write(courseBrres);
    root->addFile("course_model.brres")->setData(courseBrresData);

    modelsData.position(skyboxModelDataOff);
    CTLib::BRRES skyboxBrres = buildBRRES(modelsData.slice(), "vrcorn", stringTable);
    CTLib::Buffer skyboxBrresData = CTLib::BRRES::write(skyboxBrres);
    root->addFile("vrcorn_model.brres")->setData(skyboxBrresData);

    data.position(collisionDataOff);
    CTLib::KCL kcl = buildKCL(data.slice());
    CTLib::Buffer kclData = CTLib::KCL::write(kcl);
    root->addFile("course.kcl")->setData(kclData);

    CTLib::Buffer u8Data = CTLib::U8::write(arc);

    return CTLib::Yaz::compress(u8Data, CTLib::YazFormat::Yaz0);
}
