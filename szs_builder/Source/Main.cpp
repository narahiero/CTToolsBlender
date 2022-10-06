
#include <filesystem>
#include <iostream>

#include <CTLib/Utilities.hpp>

#include "SZSBuilder.hpp"


int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        std::cout << "ERROR: No input file" << std::endl;
        return -1;
    }
    std::filesystem::path input(argv[1]);

    if (!std::filesystem::is_regular_file(input))
    {
        std::cout << "ERROR: Input is not a file" << std::endl;
        return -1;
    }
    CTLib::Buffer data = CTLib::IO::readFile(input.string());

    CTLib::Buffer szsData;
    try
    {
        szsData = buildArchive(data);
    }
    catch (const std::runtime_error& ex)
    {
        std::cout << ex.what() << std::endl;
        return -1;
    }

    std::filesystem::path output = input.replace_extension();
    if (output.extension() != ".szs")
    {
        output.replace_extension(".szs");
    }

    if (!CTLib::IO::writeFile(output.string(), szsData))
    {
        std::cout << "ERROR: Could not write output file" << std::endl;
        return -1;
    }
}
