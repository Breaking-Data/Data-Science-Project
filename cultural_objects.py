class IdentifiableEntity(object):
    def __init__(self, id: str):
        self.id = id

    def getId(self) -> str:
        return self.id


class Person(IdentifiableEntity): # Simone
    def __init__(self, id: str, name: str):
        self.name = name
        super().__init__(id)

    def getName(self) -> str:
        return self.name


class CulturalHeritageObject(IdentifiableEntity): # Simone
    def __init__(self, id: str, title: str, owner: str, place: str, date: str = None, hasAuthor: list = list()):
        self.title = title
        self.date = date
        self.owner = owner
        self.place = place
        self.hasAuthor = hasAuthor

        super().__init__(id)

    def getTitle(self) -> str:
        return self.title

    def getDate(self) -> str | None:
        return self.date

    def getOwner(self) -> str:
        return self.owner

    def getPlace(self) -> str:
        return self.place

    def getAuthors(self) -> list:
        return self.hasAuthor


class NauticalChart(CulturalHeritageObject):
    pass


class ManuscriptPlate(CulturalHeritageObject):
    pass


class ManuscriptVolume(CulturalHeritageObject):
    pass


class PrintedVolume(CulturalHeritageObject):
    pass


class PrintedMaterial(CulturalHeritageObject):
    pass


class Herbarium(CulturalHeritageObject):
    pass


class Specimen(CulturalHeritageObject):
    pass


class Painting(CulturalHeritageObject):
    pass


class Model(CulturalHeritageObject):
    pass


class Map(CulturalHeritageObject):
    pass


""" 
All the arguments have suggested input type. The optionals arguments are None by
default, except tool, that by default is an empty set.
"""


class Activity(object): # Romolo
    def __init__(
        self,
        institute: str,
        culturalHeritageObject: CulturalHeritageObject,
        person: str = None,
        tool: set = set(),
        start: str = None,
        end: str = None,
    ):
        self.institute = institute
        self.person = person
        self.tool = tool
        self.start = start
        self.end = end
        self.culturalHeritageObject = culturalHeritageObject

    def getResponsibleInstitute(self) -> str:
        return self.institute

    def getResponsiblePerson(self) -> str | None:
        return self.person

    def getTools(self) -> set:
        return self.tool

    def getstartDate(self) -> str | None:
        return self.start

    def getendDate(self) -> str | None:
        return self.end

    def refersTo(self) -> CulturalHeritageObject:
        return self.culturalHeritageObject


class Acquisition(Activity): # Romolo
    def __init__(
        self,
        technique: str,
        institute: str,
        culturalHeritageObject: CulturalHeritageObject,
        person: str = None,
        tool: set = set(),
        start: str = None,
        end: str = None,
    ):
        super().__init__(institute, culturalHeritageObject, person, tool, start, end)
        self.technique = technique

    def getTechnique(self) -> str:
        return self.technique


class Processing(Activity):
    pass


class Modelling(Activity):
    pass


class Optimising(Activity):
    pass


class Exporting(Activity):
    pass
