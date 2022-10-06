#include "BRRESBuilder.hpp"


#include <CTLib/Ext/MDL0.hpp>


void buildObject(CTLib::Buffer& data, CTLib::MDL0* mdl0, const CTLib::Buffer& stringTable)
{
    uint32_t nameOff = data.getInt();
    std::string name = (char*)(*stringTable + nameOff);

    uint32_t vertDataOff = data.getInt();
    uint32_t normDataOff = data.getInt();
    uint32_t geoDataOff = data.getInt();

    CTLib::MDL0::Bone* bone = mdl0->getRootBone()->insert(name);
    bone->setPosition({data.getFloat(), data.getFloat(), data.getFloat()});
    bone->setRotation({data.getFloat(), data.getFloat(), data.getFloat()});
    bone->setScale({data.getFloat(), data.getFloat(), data.getFloat()});

    CTLib::Ext::MaterialCode matCode;
    matCode.setConstColour(0, {data.get(), data.get(), data.get(), data.get()});
    CTLib::MDL0::Material* mat = mdl0->add<CTLib::MDL0::Material>(name);
    mat->setGraphicsCode(matCode.toStandardLayout());
    mat->setShader(mdl0->get<CTLib::MDL0::Shader>("Shader0"));

    data.position(vertDataOff);
    CTLib::Buffer vertData = data.slice();
    uint32_t vertCount = vertData.getInt();
    vertData.limit(vertData.position() + vertCount * 0x0C);
    CTLib::MDL0::VertexArray* va = mdl0->add<CTLib::MDL0::VertexArray>(name);
    va->setData(vertData);

    data.position(normDataOff);
    CTLib::Buffer normData = data.slice();
    uint32_t normCount = normData.getInt();
    normData.limit(normData.position() + normCount * 0x0C);
    CTLib::MDL0::NormalArray* na = mdl0->add<CTLib::MDL0::NormalArray>(name);
    na->setData(normData);

    CTLib::MDL0::Object* obj = mdl0->add<CTLib::MDL0::Object>(name);
    obj->setBone(bone);
    obj->setVertexArray(va);
    obj->setVertexArrayIndexSize(2);
    obj->setNormalArray(na);
    obj->setNormalArrayIndexSize(2);

    data.position(geoDataOff);
    CTLib::Buffer geoData = data.slice();
    uint16_t idxCount = geoData.getShort(0x01);
    geoData.limit(0x03 + idxCount * 0x04);
    obj->setGeometryData(geoData);

    mdl0->getDrawOpaSection()->link(obj, mat, bone);
}

CTLib::BRRES buildBRRES(CTLib::Buffer& data, const char* name, const CTLib::Buffer& stringTable)
{
    CTLib::BRRES brres;
    CTLib::MDL0* mdl0 = brres.add<CTLib::MDL0>(name);
    mdl0->add<CTLib::MDL0::Bone>("root");

    CTLib::Ext::ShaderCode shaderCode;
    CTLib::Ext::ShaderCode::Stage& stageCode = shaderCode.addStage();
    stageCode.setColourConstantSource(CTLib::Ext::ShaderCode::Stage::ColourConstant::MaterialConstColour0_RGB);
    stageCode.setColourOp({
        CTLib::Ext::ShaderCode::Stage::ColourOp::Arg::Zero,
        CTLib::Ext::ShaderCode::Stage::ColourOp::Arg::Zero,
        CTLib::Ext::ShaderCode::Stage::ColourOp::Arg::Zero,
        CTLib::Ext::ShaderCode::Stage::ColourOp::Arg::Constant,
        CTLib::Ext::ShaderCode::Stage::Bias::Zero,
        CTLib::Ext::ShaderCode::Stage::Op::Add,
        true,
        CTLib::Ext::ShaderCode::Stage::Shift::Shift0,
        CTLib::Ext::ShaderCode::Stage::Dest::PixelOutput,
    });
    CTLib::MDL0::Shader* shader = mdl0->add<CTLib::MDL0::Shader>("Shader0");
    shader->setStageCount(1);
    shader->setGraphicsCode(shaderCode.toStandardLayout());

    uint32_t count = data.getInt();
    CTLib::Buffer objData = data.duplicate();
    for (uint32_t i = 0; i < count; ++i)
    {
        uint32_t objOff = data.getInt();
        objData.position(objOff);
        buildObject(objData.slice(), mdl0, stringTable);
    }

    return brres;
}
