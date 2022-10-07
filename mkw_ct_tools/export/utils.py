
def get_enum_number(data, prop):
    prop_rna = data.bl_rna.properties[prop]
    return data.get(prop, prop_rna.enum_items[prop_rna.default].value)
