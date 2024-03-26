from handler import MetadataQueryHandler, ProcessDataQueryHandler
from cultural_objects import *
from typing import List

class BasicMashup():
    MetadataQuery: List[MetadataQueryHandler] = []
    ProcessQuery: List[ProcessDataQueryHandler] = []

    def cleanMetadataHandlers(self):
        self.MetadataQuery = []
        if len(self.MetadataQuery) == 0:
            return True
        else:
            False
    
    def cleanProcessHandlers(self):
        self.processQuery = []
        if len(self.processQuery) == 0:
            return True
        else:
            False
    
    def addMetadataHandler(self):
        pass

    def addProcessHandler(self):
        pass

    def getEntityById(self):
        pass
    
    def getAllPeople(self):
        pass

    def getAllCulturalHeritageObjects(self):
        pass

    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> List[Person]:
        pass

    def getCulturalHeritageObjectsAuthoredBy(self):
        pass

    def getAllActivities(self):
        pass

    def getActivitiesByResponsibleInstitution(self):
        pass

    def getActivitiesByResponsiblePerson(self):
        pass

    def getActivitiesUsingTool(self):
        pass

    def getActivitiesStartedAfter(self):
        pass

    def getActivitiesEndedBefore(self):
        pass

    def getAcquisitionsByTechnique(self):
        pass


