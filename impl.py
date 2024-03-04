class IdentifiableEntity(object):
    def __init__(self, id):
        self.id = id
    
    def getId(self):
        return self.id
    
class Person(IdentifiableEntity):
    def __init__(self, id, name):
        self.name = name
        super().__init__(id)

    def getName(self):
        return self.name


class CulturalHeritageObject(IdentifiableEntity):
    def __init__(self, id, title, date, owner, place, hasAuthor):
        self.title = title
        self.date = date
        self.owner = owner
        self.place = place
        self.hasAuthor = set()
        for author in hasAuthor:
            self.hasAuthor.add(author)

        super().__init__(id)

    def getTitle(self):
        return self.title
    
    def getDate(self):
        return self.date
    
    def getOwner(self):
        return self.owner
    
    def getPlace(self):
        return self.place
    
    def getAuthors(self):
        result = []
        for author in self.hasAuthor:
            result.append(author)
        result.sort()
        return result
    
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
    

# Ho settato il valore di alcune variabili su None perché, come scritto nel data
# model sono attributi che potrebbero anche essere omessi. 
# tool è impostato su set(), se nulla viene dichiarato, allora viene restituito 
# un set vuoto.
# Per creare il collegamento tra oggetto Activity e oggetto CulturalHeritageObject,
# ho inserito nel costruttore un altro argomento obbligatorio.
class Activity:
    def __init__(self, institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None):
        self.institute = institute
        self.person = person
        self.tool = tool
        self.start = start
        self.end = end
        self.culturalHeritageObject = culturalHeritageObject

    def getResposibleInstitute(self):
        return self.institute

    def getResposiblePerson(self):
        return self.person

    def getTools(self):
        return self.tool

    def getStartDate(self):
        return self.start

    def getEndDate(self):
        return self.end

    def refersTo(self):
        return self.culturalHeritageObject
    
class Acquisition(Activity):
    def __init__(self, technique, institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None):
        super().__init__(institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None)
        self.technique = technique

    def getTechnique(self):
        return self.technique
    
class Processing(Activity):
    def __init__(self, institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None):
        super().__init__(institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None)

class Modelling(Activity):
    def __init__(self, institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None):
        super().__init__(institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None)

class Optimising(Activity):
    def __init__(self, institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None):
        super().__init__(institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None)

class Exporting(Activity):
    def __init__(self, institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None):
        super().__init__(institute, culturalHeritageObject, person=None, tool=set(), start=None, end=None)