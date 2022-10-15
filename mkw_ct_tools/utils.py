
import re


INDEX_SUFFIX_RE = re.compile(r'\.[0-9]{3}$')


def unique_name(coll, name: str):
    changed = True
    while changed:
        changed = False
        for item in coll:
            if name == item.name:
                if INDEX_SUFFIX_RE.search(name) is not None:
                    name = f"{name[:-3]}{int(name[-3:])+1:03d}"
                else:
                    name += '.001'
                changed = True
                break

    return name
