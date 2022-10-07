
def get_enum_number(data, prop):
    prop_rna = data.bl_rna.properties[prop]
    return data.get(prop, prop_rna.enum_items[prop_rna.default].value)


def print_buffer(buf):
    for pos in range(len(buf)):
        if (pos & 0xF) == 0:
            print(f"\n[{pos:04X}] ", end=" ")
        print(f"{buf.data[pos]:02X}", end=" ")

    print(f"\n\n{buf.pos=:04X} {buf.limit=:04X}\n")
