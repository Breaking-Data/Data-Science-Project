from handler import MetadataQueryHandler, ProcessDataQueryHandler
from cultural_objects import *

class BasicMashup(object):
    def __init__(self, metadataQuery: list[MetadataQueryHandler] = [], processQuery: list[ProcessDataQueryHandler] = []) -> None:
        self.metadataQuery = metadataQuery
        self.processQuery = processQuery        

    def cleanMetadataHandlers(self) -> bool: #Romolo
        self.metadataQuery = []
        return len(self.metadataQuery) == 0
    
    def cleanProcessHandlers(self) -> bool: #Pietro
        self.processQuery = []
        return len(self.processQuery) == 0
            
    def addMetadataHandler(self, handler: MetadataQueryHandler) -> bool: #Simone
        len_processQuery = len(self.processQuery)
        self.processQuery.append(handler)
        return len_processQuery == (len(self.processQuery) + 1)

    def addProcessHandler(self) -> bool: #Ludovica
        pass

    def getEntityById(self, id: str) -> IdentifiableEntity|None: #Simone
        pass
    
    def getAllPeople(self) -> list[Person]: #Romolo
        people = []
        for metaGrinder in self.metadataQuery:
            df_people = metaGrinder.getAllPeople()
            
            for index, row in df_people.iterrows():
                person_name = row['name']
                person_id = row['id']
                person = Person(person_id, person_name)
                people.append(person)

        return people

    def getAllCulturalHeritageObjects(self) -> list[CulturalHeritageObject]: #Ludovica
        pass

    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> list[Person]: #Pietro
        pass

    def getCulturalHeritageObjectsAuthoredBy(self) -> list[CulturalHeritageObject]: #Pietro
        pass

    def getAllActivities(self) -> list[Activity]: #Simone
        pass

    def getActivitiesByResponsibleInstitution(self) -> list[Activity]: #Ludovica
        pass

    def getActivitiesByResponsiblePerson(self, name: str) -> list[Activity]: #Romolo
        pass

    def getActivitiesUsingTool(self) -> list[Activity]: #Simone
        pass

    def getActivitiesStartedAfter(self) -> list[Activity]: #Romolo
        pass

    def getActivitiesEndedBefore(self) -> list[Activity]: #Pietro
        pass

    def getAcquisitionsByTechnique(self) -> list[Acquisition]: #Ludovica
        pass
