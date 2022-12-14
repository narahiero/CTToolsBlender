#include "BRRESBuilder.hpp"


#include <CTLib/Ext/MDL0.hpp>
#include <CTLib/Utilities.hpp>


const std::string DEFAULT_RESOURCE_NAME = "___Default___";


void buildTexture(CTLib::Buffer& data, CTLib::BRRES& brres, const CTLib::Buffer& stringTable)
{
    uint32_t nameOff = data.getInt();
    std::string name = (char*)(*stringTable + nameOff);

    uint32_t width = data.getInt();
    uint32_t height = data.getInt();

    CTLib::ImageFormat format = static_cast<CTLib::ImageFormat>(data.get());
    bool genMipmaps = data.get();
    uint8_t genMipmapCount = data.get();
    data.get(); // padding

    CTLib::Buffer texData = data.slice();
    texData.limit(width * height * 0x04);
    CTLib::Image image(width, height, texData);

    CTLib::TEX0* tex0 = brres.add<CTLib::TEX0>(name);
    tex0->setTextureData(image, format);

    if (genMipmaps)
    {
        tex0->generateMipmaps(genMipmapCount, image);
    }
}

void createDefaultTexture(CTLib::BRRES& brres)
{
    if (brres.has<CTLib::TEX0>(DEFAULT_RESOURCE_NAME))
    {
        return; // default texture was overwritten in data file
    }

    CTLib::Image image(1, 1, CTLib::RGBAColour{0x7F, 0x7F, 0x7F, 0xFF});
    CTLib::TEX0* tex0 = brres.add<CTLib::TEX0>(DEFAULT_RESOURCE_NAME);
    tex0->setTextureData(image, CTLib::ImageFormat::I4);
}

void buildShader(CTLib::Buffer& data, CTLib::MDL0* mdl0, const CTLib::Buffer& stringTable)
{
    uint32_t nameOff = data.getInt();
    std::string name = (char*)(*stringTable + nameOff);

    CTLib::Ext::ShaderCode shaderCode;

    uint32_t stageCount = data.getInt();
    for (uint32_t i = 0; i < stageCount; ++i)
    {
        CTLib::Ext::ShaderCode::Stage& stageCode = shaderCode.addStage();
        stageCode.setUsesTexture(data.get());
        stageCode.setTexCoordIndex(data.get());

        data.getShort(); // padding

        stageCode.setColourConstantSource(static_cast<CTLib::Ext::ShaderCode::Stage::ColourConstant>(data.get()));

        CTLib::Ext::ShaderCode::Stage::ColourOp co;
        co.argA = static_cast<CTLib::Ext::ShaderCode::Stage::ColourOp::Arg>(data.get());
        co.argB = static_cast<CTLib::Ext::ShaderCode::Stage::ColourOp::Arg>(data.get());
        co.argC = static_cast<CTLib::Ext::ShaderCode::Stage::ColourOp::Arg>(data.get());
        co.argD = static_cast<CTLib::Ext::ShaderCode::Stage::ColourOp::Arg>(data.get());
        co.bias = static_cast<CTLib::Ext::ShaderCode::Stage::Bias>(data.get());
        co.op = static_cast<CTLib::Ext::ShaderCode::Stage::Op>(data.get());
        co.clamp = data.get();
        co.shift = static_cast<CTLib::Ext::ShaderCode::Stage::Shift>(data.get());
        co.dest = static_cast<CTLib::Ext::ShaderCode::Stage::Dest>(data.get());
        stageCode.setColourOp(co);

        stageCode.setAlphaConstantSource(static_cast<CTLib::Ext::ShaderCode::Stage::AlphaConstant>(data.get()));

        CTLib::Ext::ShaderCode::Stage::AlphaOp ao;
        ao.argA = static_cast<CTLib::Ext::ShaderCode::Stage::AlphaOp::Arg>(data.get());
        ao.argB = static_cast<CTLib::Ext::ShaderCode::Stage::AlphaOp::Arg>(data.get());
        ao.argC = static_cast<CTLib::Ext::ShaderCode::Stage::AlphaOp::Arg>(data.get());
        ao.argD = static_cast<CTLib::Ext::ShaderCode::Stage::AlphaOp::Arg>(data.get());
        ao.bias = static_cast<CTLib::Ext::ShaderCode::Stage::Bias>(data.get());
        ao.op = static_cast<CTLib::Ext::ShaderCode::Stage::Op>(data.get());
        ao.clamp = data.get();
        ao.shift = static_cast<CTLib::Ext::ShaderCode::Stage::Shift>(data.get());
        ao.dest = static_cast<CTLib::Ext::ShaderCode::Stage::Dest>(data.get());
        stageCode.setAlphaOp(ao);
    }

    CTLib::MDL0::Shader* shader = mdl0->add<CTLib::MDL0::Shader>(name);
    shader->setStageCount(stageCount);
    shader->setTexRef(0, 0); // temporarily hard-coded
    shader->setGraphicsCode(shaderCode.toStandardLayout());
}

void createDefaultShader(CTLib::MDL0* mdl0)
{
    if (mdl0->has<CTLib::MDL0::Shader>(DEFAULT_RESOURCE_NAME))
    {
        return; // default shader was overwritten in data file
    }

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
    CTLib::MDL0::Shader* shader = mdl0->add<CTLib::MDL0::Shader>(DEFAULT_RESOURCE_NAME);
    shader->setStageCount(1);
    shader->setGraphicsCode(shaderCode.toStandardLayout());
}

void buildMaterial(CTLib::Buffer& data, CTLib::BRRES& brres, CTLib::MDL0* mdl0, const CTLib::Buffer& stringTable)
{
    uint32_t nameOff = data.getInt();
    std::string name = (char*)(*stringTable + nameOff);

    uint32_t shaderNameOff = data.getInt();
    std::string shaderName = (char*)(*stringTable + shaderNameOff);

    CTLib::Ext::MaterialCode matCode;
    matCode.setConstColour(0, {data.get(), data.get(), data.get(), data.get()});
    CTLib::MDL0::Material* mat = mdl0->add<CTLib::MDL0::Material>(name);
    mat->setGraphicsCode(matCode.toStandardLayout());

    uint32_t layerCount = data.getInt();
    for (uint32_t i = 0; i < layerCount; ++i)
    {
        uint32_t texNameOff = data.getInt();
        std::string texName = (char*)(*stringTable + texNameOff);

        CTLib::MDL0::TextureLink* link = mdl0->linkTEX0(brres.get<CTLib::TEX0>(texName));
        CTLib::MDL0::Material::Layer* layer = mat->addLayer(link);

        CTLib::MDL0::Material::Layer::TextureWrap wrapMode = static_cast<CTLib::MDL0::Material::Layer::TextureWrap>(data.get());
        CTLib::MDL0::Material::Layer::MinFilter minFilter = static_cast<CTLib::MDL0::Material::Layer::MinFilter>(data.get());
        CTLib::MDL0::Material::Layer::MagFilter magFilter = static_cast<CTLib::MDL0::Material::Layer::MagFilter>(data.get());

        layer->setTextureWrapMode(wrapMode);
        layer->setMinFilter(minFilter);
        layer->setMagFilter(magFilter);
    }

    mat->setShader(mdl0->get<CTLib::MDL0::Shader>(shaderName));
}

void createDefaultMaterial(CTLib::MDL0* mdl0)
{
    if (mdl0->has<CTLib::MDL0::Material>(DEFAULT_RESOURCE_NAME))
    {
        return; // default material was overwritten in data file
    }

    CTLib::Ext::MaterialCode matCode;
    matCode.setConstColour(0, {0x7F, 0x7F, 0x7F, 0xFF});
    CTLib::MDL0::Material* mat = mdl0->add<CTLib::MDL0::Material>(DEFAULT_RESOURCE_NAME);
    mat->setGraphicsCode(matCode.toStandardLayout());
    mat->setShader(mdl0->get<CTLib::MDL0::Shader>(DEFAULT_RESOURCE_NAME));
}

void buildPart(CTLib::Buffer& data, CTLib::MDL0* mdl0, const std::string& objName, uint32_t colourCount, uint32_t texcoordCount, const CTLib::Buffer& stringTable)
{
    uint32_t nameOff = data.getInt();
    std::string name = (char*)(*stringTable + nameOff);

    uint32_t matNameOff = data.getInt();
    std::string matName = (char*)(*stringTable + matNameOff);

    CTLib::MDL0::Bone* bone = mdl0->get<CTLib::MDL0::Bone>(objName);

    CTLib::MDL0::Object* obj = mdl0->add<CTLib::MDL0::Object>(name);
    obj->setBone(bone);
    obj->setVertexArray(mdl0->get<CTLib::MDL0::VertexArray>(objName));
    obj->setVertexArrayIndexSize(2);
    obj->setNormalArray(mdl0->get<CTLib::MDL0::NormalArray>(objName));
    obj->setNormalArrayIndexSize(2);

    for (uint32_t i = 0; i < colourCount; ++i)
    {
        obj->setColourArray(mdl0->get<CTLib::MDL0::ColourArray>(CTLib::Strings::format("%s___#%d", objName.c_str(), i)), i);
        obj->setColourArrayIndexSize(i, 2);
    }

    for (uint32_t i = 0; i < texcoordCount; ++i)
    {
        obj->setTexCoordArray(mdl0->get<CTLib::MDL0::TexCoordArray>(CTLib::Strings::format("%s___#%d", objName.c_str(), i)), i);
        obj->setTexCoordArrayIndexSize(i, 2);
    }

    uint32_t idxSize = 0x04 + colourCount * 0x02 + texcoordCount * 0x02;

    CTLib::Buffer geoData = data.slice();
    uint16_t idxCount = geoData.getShort(0x01);
    geoData.limit(0x03 + idxCount * idxSize);
    obj->setGeometryData(geoData);

    CTLib::MDL0::Material* mat = mdl0->get<CTLib::MDL0::Material>(matName);
    mdl0->getDrawOpaSection()->link(obj, mat, bone);
}

void buildObject(CTLib::Buffer& data, CTLib::MDL0* mdl0, const CTLib::Buffer& stringTable)
{
    uint32_t nameOff = data.getInt();
    std::string name = (char*)(*stringTable + nameOff);

    uint32_t vertDataOff = data.getInt();
    uint32_t normDataOff = data.getInt();
    uint32_t colourDataOff = data.getInt();
    uint32_t texcoordDataOff = data.getInt();
    uint32_t partDataOff = data.getInt();

    CTLib::MDL0::Bone* bone = mdl0->getRootBone()->insert(name);
    bone->setPosition({data.getFloat(), data.getFloat(), data.getFloat()});
    bone->setRotation({data.getFloat(), data.getFloat(), data.getFloat()});
    bone->setScale({data.getFloat(), data.getFloat(), data.getFloat()});

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

    data.position(colourDataOff);
    CTLib::Buffer colourData = data.slice();
    uint32_t colourLayerCount = colourData.getInt();
    for (uint32_t i = 0; i < colourLayerCount; ++i)
    {
        colourData.limit(colourData.position() + 0x04);
        uint32_t colourCount = colourData.getInt();
        colourData.limit(colourData.position() + colourCount * 0x04);
        CTLib::MDL0::ColourArray* ca = mdl0->add<CTLib::MDL0::ColourArray>(CTLib::Strings::format("%s___#%d", name.c_str(), i));
        ca->setData(colourData);
    }

    data.position(texcoordDataOff);
    CTLib::Buffer texcoordData = data.slice();
    uint32_t texcoordLayerCount = texcoordData.getInt();
    for (uint32_t i = 0; i < texcoordLayerCount; ++i)
    {
        texcoordData.limit(texcoordData.position() + 0x04);
        uint32_t texcoordCount = texcoordData.getInt();
        texcoordData.limit(texcoordData.position() + texcoordCount * 0x08);
        CTLib::MDL0::TexCoordArray* tca = mdl0->add<CTLib::MDL0::TexCoordArray>(CTLib::Strings::format("%s___#%d", name.c_str(), i));
        tca->setData(texcoordData);
    }

    data.position(partDataOff);
    CTLib::Buffer partData = data.slice();
    uint32_t partCount = data.getInt();
    for (uint32_t i = 0; i < partCount; ++i)
    {
        uint32_t partOff = data.getInt();
        partData.position(partOff);
        buildPart(partData.slice(), mdl0, name, colourLayerCount, texcoordLayerCount, stringTable);
    }
}

CTLib::BRRES buildBRRES(CTLib::Buffer& data, const char* name, const CTLib::Buffer& stringTable)
{
    CTLib::BRRES brres;
    CTLib::MDL0* mdl0 = brres.add<CTLib::MDL0>(name);
    mdl0->add<CTLib::MDL0::Bone>("root");

    uint32_t texsOff = data.getInt();
    uint32_t shadersOff = data.getInt();
    uint32_t matsOff = data.getInt();
    uint32_t objsOff = data.getInt();

    data.position(texsOff);
    CTLib::Buffer texData = data.slice();
    uint32_t texCount = data.getInt();
    for (uint32_t i = 0; i < texCount; ++i)
    {
        uint32_t texOff = data.getInt();
        texData.position(texOff);
        buildTexture(texData.slice(), brres, stringTable);
    }

    createDefaultTexture(brres);

    data.position(shadersOff);
    CTLib::Buffer shaderData = data.slice();
    uint32_t shaderCount = data.getInt();
    for (uint32_t i = 0; i < shaderCount; ++i)
    {
        uint32_t shaderOff = data.getInt();
        shaderData.position(shaderOff);
        buildShader(shaderData.slice(), mdl0, stringTable);
    }

    createDefaultShader(mdl0);

    data.position(matsOff);
    CTLib::Buffer matData = data.slice();
    uint32_t matCount = data.getInt();
    for (uint32_t i = 0; i < matCount; ++i)
    {
        uint32_t matOff = data.getInt();
        matData.position(matOff);
        buildMaterial(matData.slice(), brres, mdl0, stringTable);
    }

    createDefaultMaterial(mdl0);

    data.position(objsOff);
    CTLib::Buffer objData = data.slice();
    uint32_t objCount = data.getInt();
    for (uint32_t i = 0; i < objCount; ++i)
    {
        uint32_t objOff = data.getInt();
        objData.position(objOff);
        buildObject(objData.slice(), mdl0, stringTable);
    }

    return brres;
}
