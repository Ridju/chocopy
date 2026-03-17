from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    pass

    def is_subtype_of(self, other: "Type") -> bool:
        if isinstance(other, ClassType) and other.name == "object":
            return True
        return self == other


@dataclass(frozen=True)
class IntType(Type):
    pass

    def is_subtype_of(self, other: "Type") -> bool:
        return super().is_subtype_of(other)


@dataclass(frozen=True)
class BoolType(Type):
    pass

    def is_subtype_of(self, other: "Type") -> bool:
        return super().is_subtype_of(other)


@dataclass(frozen=True)
class StringType(Type):
    pass

    def is_subtype_of(self, other: "Type") -> bool:
        return super().is_subtype_of(other)


@dataclass(frozen=True)
class ListType(Type):
    element_type: Type

    def is_subtype_of(self, other: "Type") -> bool:
        if isinstance(other, ListType):
            return self.element_type == other.element_type
        elif super().is_subtype_of(other):
            return True

        return False


@dataclass(frozen=True)
class NoneType(Type):
    def is_subtype_of(self, other: "Type") -> bool:
        if isinstance(other, ClassType):
            return True
        elif isinstance(other, ListType):
            return True

        return False


@dataclass(frozen=True)
class EmptyListType(Type):
    def is_subtype_of(self, other: "Type") -> bool:
        if isinstance(other, ListType):
            return True

        return False


@dataclass(frozen=True)
class ClassType(Type):
    name: str

    def is_subtype_of(self, other: "Type", hierarchy: dict[str, str]) -> bool:
        if not isinstance(other, ClassType):
            return super().is_subtype_of(other)

        curr = self.name
        while curr is not None:
            if curr == other.name:
                return True
            curr = hierarchy.get(curr)

        return super().is_subtype_of(other)
