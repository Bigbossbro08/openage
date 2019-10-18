# Copyright 2013-2017 the openage authors. See copying.md for legal info.

# TODO pylint: disable=C,R

from . import unit
from openage.convert.dataformat.genie_structure import GenieStructure
from openage.convert.dataformat.read_members import MultisubtypeMember, EnumLookupMember
from ..dataformat.member_access import READ, READ_EXPORT
from ..dataformat.value_members import MemberTypes as StorageType


class Civ(GenieStructure):
    name_struct = "civilisation"
    name_struct_file = name_struct
    struct_description = "describes a civilisation."

    data_format = [
        (READ, "player_type", StorageType.INT_MEMBER, "int8_t"),           # always 1
        (READ_EXPORT, "name", StorageType.STRING_MEMBER, "char[20]"),
        (READ, "resources_count", StorageType.INT_MEMBER, "uint16_t"),
        (READ_EXPORT, "tech_tree_id", StorageType.ID_MEMBER, "int16_t"),  # links to effect bundle id (to apply its effects)
    ]

    # TODO: Enable conversion for AOE1; replace "team_bonus_id"
    # ===========================================================================
    # if (GameVersion.aoe_1 or GameVersion.aoe_ror) not in game_versions:
    #     data_format.append((READ_EXPORT, "team_bonus_id", "int16_t"))
    # ===========================================================================
    data_format.append((READ_EXPORT, "team_bonus_id", StorageType.ID_MEMBER, "int16_t"))         # links to tech id as well

    # TODO: Enable conversion for SWGB
    # ===========================================================================
    # if (GameVersion.swgb_10 or GameVersion.swgb_cc) in game_versions:
    #     data_format.extend([
    #         (READ, "name2", "char[20]"),
    #         (READ, "unique_unit_techs", "int16_t[4]"),
    #     ])
    # ===========================================================================

    data_format.extend([
        (READ, "resources", StorageType.CONTAINER_MEMBER, "float[resources_count]"),
        (READ, "icon_set", StorageType.ID_MEMBER, "int8_t"),                      # building icon set, trade cart graphics, changes no other graphics
        (READ_EXPORT, "unit_count", StorageType.INT_MEMBER, "uint16_t"),
        (READ, "unit_offsets", StorageType.CONTAINER_MEMBER, "int32_t[unit_count]"),

        (READ_EXPORT, "units", StorageType.CONTAINER_MEMBER, MultisubtypeMember(
            type_name          = "unit_types",
            subtype_definition = (READ, "unit_type", StorageType.ID_MEMBER, EnumLookupMember(
                type_name      = "unit_type_id",
                lookup_dict    = unit.unit_type_lookup,
                raw_type       = "int8_t",
            )),
            class_lookup       = unit.unit_type_class_lookup,
            length             = "unit_count",
            offset_to          = ("unit_offsets", lambda o: o > 0),
        )),
    ])
