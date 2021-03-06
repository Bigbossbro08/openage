# Copyright 2019-2020 the openage authors. See copying.md for legal info.

"""
Objects that represent data structures in the original game.

These are simple containers that can be processed by the converter.
"""

from .value_members import ValueMember
from ...nyan.nyan_structs import NyanObject, MemberOperator
from .aoc.expected_pointer import ExpectedPointer
from .aoc.combined_sprite import CombinedSprite
from openage.convert.dataformat.value_members import NoDiffMember
from openage.convert.dataformat.aoc.combined_sound import CombinedSound


class ConverterObject:
    """
    Storage object for data objects in the to-be-converted games.
    """

    def __init__(self, obj_id, members=None):
        """
        Creates a new ConverterObject.

        :param obj_id: An identifier for the object (as a string or int)
        :param members: An already existing member dict.
        """
        self.obj_id = obj_id

        self.members = {}

        if members:
            member_list = list(members.values())

            if all(isinstance(member, ValueMember) for member in member_list):
                self.members.update(members)

            else:
                raise Exception("members must be an instance of ValueMember")

    def get_id(self):
        """
        Returns the object's ID.
        """
        return self.obj_id

    def add_member(self, member):
        """
        Adds a member to the object.
        """
        key = member.get_name()
        self.members.update({key: member})

    def add_members(self, members):
        """
        Adds multiple members to the object.
        """
        for member in members:
            key = member.get_name()
            self.members.update({key: member})

    def get_member(self, name):
        """
        Returns a member of the object.
        """
        return self.members[name]

    def has_member(self, name):
        """
        Returns True if the object has a member with the specified name.
        """
        return name in self.members

    def remove_member(self, name):
        """
        Removes a member from the object.
        """
        self.members.pop(name)

    def short_diff(self, other):
        """
        Returns the obj_diff between two objects as another ConverterObject.

        The object created by short_diff() only contains members
        that are different. It does not contain NoDiffMembers.
        """
        if type(self) is not type(other):
            raise Exception("type %s cannot be diffed with type %s"
                            % (type(self), type(other)))

        obj_diff = {}

        for member_id, member in self.members.items():
            member_diff = member.diff(other.get_member(member_id))

            if not isinstance(member_diff, NoDiffMember):
                obj_diff.update({member_id: member_diff})

        return ConverterObject("%s-%s-sdiff" % (self.obj_id, other.get_id()), members=obj_diff)

    def diff(self, other):
        """
        Returns the obj_diff between two objects as another ConverterObject.
        """
        if type(self) is not type(other):
            raise Exception("type %s cannot be diffed with type %s"
                            % (type(self), type(other)))

        obj_diff = {}

        for member_id, member in self.members.items():
            obj_diff.update({member_id: member.diff(other.get_member(member_id))})

        return ConverterObject("%s-%s-diff" % (self.obj_id, other.get_id()), members=obj_diff)

    def __getitem__(self, key):
        """
        Short command for getting a member of the object.
        """
        return self.get_member(key)

    def __repr__(self):
        raise NotImplementedError(
            "return short description of the object %s" % (type(self)))


class ConverterObjectGroup:
    """
    A group of objects that are connected together in some way
    and need each other for conversion. ConverterObjectGroup
    instances are converted to the nyan API.
    """

    def __init__(self, group_id, raw_api_objects=None):
        """
        Creates a new ConverterObjectGroup.

        :paran group_id:  An identifier for the object group (as a string or int)
        :param raw_api_objects: A list of raw API objects. These will become
                                proper API objects during conversion.
        """
        self.group_id = group_id

        # stores the objects that will later be converted to nyan objects
        # this uses a preliminary fqon as a key
        self.raw_api_objects = {}

        if raw_api_objects:
            self._create_raw_api_object_dict(raw_api_objects)

    def get_id(self):
        """
        Returns the object group's ID.
        """
        return self.group_id

    def add_raw_api_object(self, subobject):
        """
        Adds a subobject to the object.
        """
        key = subobject.get_id()
        self.raw_api_objects.update({key: subobject})

    def add_raw_api_objects(self, subobjects):
        """
        Adds several subobject to the object.
        """
        for subobject in subobjects:
            self.add_raw_api_object(subobject)

    def create_nyan_objects(self):
        """
        Creates nyan objects from the existing raw API objects.
        """
        for raw_api_object in self.raw_api_objects.values():
            raw_api_object.create_nyan_object()

    def create_nyan_members(self):
        """
        Fill nyan members of all raw API objects.
        """
        for raw_api_object in self.raw_api_objects.values():
            raw_api_object.create_nyan_members()

            if not raw_api_object.is_ready():
                raise Exception("%s: object is not ready for export. "
                                "Member or object not initialized." % (raw_api_object))

    def get_raw_api_object(self, obj_id):
        """
        Returns a subobject of the object.
        """
        return self.raw_api_objects[obj_id]

    def get_raw_api_objects(self):
        """
        Returns all raw API objects.
        """
        return self.raw_api_objects

    def has_raw_api_object(self, obj_id):
        """
        Returns True if the object has a subobject with the specified ID.
        """
        return obj_id in self.raw_api_objects

    def remove_raw_api_object(self, obj_id):
        """
        Removes a subobject from the object.
        """
        self.raw_api_objects.pop(obj_id)

    def _create_raw_api_object_dict(self, subobject_list):
        """
        Creates the dict from the subobject list passed to __init__.
        """
        for subobject in subobject_list:
            self.add_raw_api_object(subobject)

    def __repr__(self):
        raise NotImplementedError(
            "return short description of the object %s" % (type(self)))


class RawAPIObject:
    """
    An object that contains all the necessary information to create
    a nyan API object. Members are stored as (membername, value) pairs.
    Values refer either to primitive values (int, float, str),
    expected pointers to objects or expected media files.
    The 'expected' values two have to be resolved in an additional step.
    """

    def __init__(self, obj_id, name, api_ref, location=""):
        """
        Creates a raw API object.

        :param obj_id: Unique identifier for the raw API object.
        :type obj_id: str
        :param name: Name of the nyan object created from the raw API object.
        :type name: str
        :param api_ref: The openage API objects used as reference for creating the nyan object.
        :type api_ref: dict
        :param location: Relative path of the nyan file in the modpack or another raw API object.
        :type location: str, .expected_pointer.ExpectedPointer
        """

        self.obj_id = obj_id
        self.name = name

        self.api_ref = api_ref

        self.raw_members = []
        self.raw_parents = []

        self._location = location
        self._filename = None

        self.nyan_object = None

    def add_raw_member(self, name, value, origin):
        """
        Adds a raw member to the object.

        :param name: Name of the member (has to be a valid inherited member name).
        :type name: str
        :param value: Value of the member.
        :type value: int, float, bool, str, list
        :param origin: from which parent the member was inherited.
        :type origin: str
        """
        self.raw_members.append((name, value, origin))

    def add_raw_parent(self, parent_id):
        """
        Adds a raw parent to the object.

        :param parent_id: fqon of the parent in the API object dictionary
        :type parent_id: str
        """
        self.raw_parents.append(parent_id)

    def create_nyan_object(self):
        """
        Create the nyan object for this raw API object. Members have to be created separately.
        """
        parents = []
        for raw_parent in self.raw_parents:
            parents.append(self.api_ref[raw_parent])

        self.nyan_object = NyanObject(self.name, parents)

    def create_nyan_members(self):
        """
        Fills the nyan object members with values from the raw members.
        References to nyan objects or media files with be resolved.
        The nyan object has to be created before this function can be called.
        """
        if self.nyan_object is None:
            raise Exception("%s: nyan object needs to be created before"
                            "member values can be assigned" % (self))

        for raw_member in self.raw_members:
            member_name = raw_member[0]
            member_value = raw_member[1]
            member_origin = self.api_ref[raw_member[2]]

            if isinstance(member_value, ExpectedPointer):
                member_value = member_value.resolve()

            elif isinstance(member_value, CombinedSprite):
                member_value = member_value.get_relative_sprite_location()

            elif isinstance(member_value, CombinedSound):
                member_value = member_value.get_relative_file_location()

            elif isinstance(member_value, list):
                # Resolve elements in the list, if it's not empty
                if member_value:
                    temp_values = []

                    for temp_value in member_value:
                        if isinstance(temp_value, ExpectedPointer):
                            temp_values.append(temp_value.resolve())

                        elif isinstance(temp_value, CombinedSprite):
                            temp_values.append(temp_value.get_relative_sprite_location())

                        elif isinstance(temp_value, CombinedSound):
                            temp_values.append(temp_value.get_relative_file_location())

                        else:
                            temp_values.append(temp_value)

                    member_value = temp_values

            elif isinstance(member_value, float):
                # Round floats to 6 decimal places for increased readability
                # should have no effect on balance, hopefully
                member_value = round(member_value, ndigits=6)

            nyan_member_name = member_name
            nyan_member = self.nyan_object.get_member_by_name(nyan_member_name, member_origin)
            nyan_member.set_value(member_value, MemberOperator.ASSIGN)

    def get_filename(self):
        """
        Returns the filename of the raw API object.
        """
        return self._filename

    def get_file_location(self):
        """
        Returns a tuple with 
            1. the relative path to the directory
            2. the filename
        where the nyan object will be stored.

        This method can be called instead of get_location() when
        you are unsure whether the nyan object will be nested.
        """
        if isinstance(self._location, ExpectedPointer):
            # Work upwards until we find the root object
            nesting_raw_api_object = self._location.resolve_raw()
            nesting_location = nesting_raw_api_object.get_location()

            while isinstance(nesting_location, ExpectedPointer):
                nesting_raw_api_object = nesting_location.resolve_raw()
                nesting_location = nesting_raw_api_object.get_location()

            return (nesting_location, nesting_raw_api_object.get_filename())

        return (self._location, self._filename)

    def get_id(self):
        """
        Returns the ID of the raw API object.
        """
        return self.obj_id

    def get_location(self):
        """
        Returns the relative path to a directory or an ExpectedPointer
        to another RawAPIObject.
        """
        return self._location

    def get_nyan_object(self):
        """
        Returns the nyan API object for the raw API object.
        """
        if self.nyan_object:
            return self.nyan_object

        raise Exception("nyan object for %s has not been created yet" % (self))

    def is_ready(self):
        """
        Returns whether the object is ready to be exported.
        """
        return self.nyan_object is not None and not self.nyan_object.is_abstract()

    def set_filename(self, filename, suffix="nyan"):
        """
        Set the filename of the resulting nyan file.

        :param filename: File name prefix (without extension).
        :type filename: str
        :param suffix: File extension (defaults to "nyan")
        :type suffix: str
        """
        self._filename = "%s.%s" % (filename, suffix)

    def set_location(self, location):
        """
        Set the relative location of the object in a modpack. This must
        be a path to a nyan file or an ExpectedPointer to a nyan object.

        :param location: Relative path of the nyan file in the modpack or another raw API object.
        :type location: str, .expected_pointer.ExpectedPointer
        """
        self._location = location

    def __repr__(self):
        return "RawAPIObject<%s>" % (self.obj_id)


class ConverterObjectContainer:
    """
    A conainer for all ConverterObject instances in a converter process.

    It is recommended to create one ConverterObjectContainer for everything
    and pass the reference around.
    """

    def __repr__(self):
        return "ConverterObjectContainer"
