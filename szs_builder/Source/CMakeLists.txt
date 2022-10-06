
add_executable(SZSBuilder
    BRRESBuilder.cpp
    KCLBuilder.cpp
    KMPBuilder.cpp
    Main.cpp
    SZSBuilder.cpp
)

target_link_libraries(SZSBuilder CTLib)
