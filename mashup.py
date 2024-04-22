from handler import MetadataQueryHandler, ProcessDataQueryHandler
from cultural_objects import *
import importlib
import pandas as pd


class BasicMashup(object):
    def __init__(self) -> None:
        self.metadataQuery = list()
        self.processQuery = list()

    def cleanMetadataHandlers(self) -> bool:  # Romolo
        self.metadataQuery = []
        return len(self.metadataQuery) == 0

    def cleanProcessHandlers(self) -> bool:  # Pietro
        self.processQuery = []
        return len(self.processQuery) == 0

    def addMetadataHandler(self, handler: MetadataQueryHandler) -> bool:  # Simone
        len_metadataQuery = len(self.metadataQuery)
        self.metadataQuery.append(handler)
        return (
            len(self.metadataQuery) == len_metadataQuery + 1
            and self.metadataQuery[-1] == handler
        )

    def addProcessHandler(self, handler: ProcessDataQueryHandler) -> bool:  # Ludovica
        len_processQuery = len(self.processQuery)
        self.processQuery.append(handler)
        return (
            len(self.processQuery) == len_processQuery + 1
            and self.processQuery[-1] == handler
        )

    def getEntityById(self, id: str) -> IdentifiableEntity | None:  # Simone
        pass

    def getAllPeople(self) -> list[Person]:  # Romolo
        people = []
        for metaGrinder in self.metadataQuery:
            df_people = metaGrinder.getAllPeople()

            for index, row in df_people.iterrows():
                person_name = row["name"]
                person_id = row["id"]
                person = Person(person_id, person_name)
                people.append(person)

        return people

    def getAllCulturalHeritageObjects(self) -> list[CulturalHeritageObject]:  # Ludovica
        cultural_objects = []
        # import module to be used later
        module = importlib.import_module("cultural_objects")

        for metadata in self.metadataQuery:
            # cultural objects dataframe
            df_objects = metadata.getAllCulturalHeritageObjects().sort_values(by="id")

            for index, row in df_objects.iterrows():
                # info about the object
                ob_id = row.id
                title = row.title.strip()
                date = row.date if not pd.isna(row.date) else None
                owner = row.owner
                place = row.place

                # info about the author
                authors = []
                df_authors = metadata.getAuthorsOfCulturalHeritageObject(f"{ob_id}")
                for index, authors_row in df_authors.iterrows():
                    author_id = authors_row.id
                    author_name = authors_row.author_name.strip()
                    author = Person(id=author_id, name=author_name)
                    authors.append(author)

                # get the subclass name for the object
                object_subclass = row.type.removeprefix(
                    "https://breaking-data.github.io/Data-Science-Project/"
                ).removeprefix("http://schema.org/")

                # import the module and get the class
                subclass = getattr(module, object_subclass)
                instance = subclass(
                    id=ob_id,
                    title=title,
                    date=date,
                    owner=owner,
                    place=place,
                    hasAuthor=authors,
                )

                # add the cultural object to the list
                cultural_objects.append(instance)

        return cultural_objects

    def getAuthorsOfCulturalHeritageObject(
        self, objectId: str
    ) -> list[Person]:  # Pietro
        authors = []
        objects = self.getAllCulturalHeritageObjects()
        for ob in objects:
            if ob.getId() == objectId:
                authors_list = ob.getAuthors()
                for author in authors_list:
                    authors.append(author)

        return authors

    def getCulturalHeritageObjectsAuthoredBy(
        self, AuthorId: str
    ) -> list[CulturalHeritageObject]:  # Pietro
        objects = []
        all_objects = self.getAllCulturalHeritageObjects()
        for ob in all_objects:
            authors = ob.getAuthors()
            author_ids = []
            for author in authors:
                author_ids.append(author.getId())
            if AuthorId in author_ids:
                objects.append(ob)

        return objects

    def getAllActivities(self) -> list[Activity]:  # Simone
        pass

    def getActivitiesByResponsibleInstitution(self) -> list[Activity]:  # Ludovica
        pass

    def getActivitiesByResponsiblePerson(
        self, partialName: str
    ) -> list[Activity]:  # Romolo
        activities = []
        for activity in self.getAllActivities():
            if partialName in activity.getResponsiblePerson():
                activities.append(activity)
        return activities

    def getActivitiesUsingTool(self) -> list[Activity]:  # Simone
        pass

    def getActivitiesStartedAfter(self, date: str) -> list[Activity]:  # Romolo
        activities = []
        for activity in self.getAllActivities():
            if activity.getstartDate() >= date:
                activities.append(activity)
        return activities

    def getActivitiesEndedBefore(self, date: str) -> list[Activity]:  # Pietro
        activities = []
        for activity in self.getAllActivities():
            if activity.getendDate() <= date:
                activities.append(activity)
        return activities

    def getAcquisitionsByTechnique(self) -> list[Acquisition]:  # Ludovica
        pass


class AdvancedMashup(BasicMashup):
    def getActivitiesOnObjectsAuthoredBy(self, personId: str) -> list[Activity]:
        pass

    def getObjectsHandledByResponsiblePerson(
        self, partialName: str
    ) -> list[CulturalHeritageObject]:
        pass

    def getObjectsHandledByResponsibleInstitution(
        self, partialName: str
    ) -> list[CulturalHeritageObject]:
        pass

    def getAuthorsOfObjectsAcquiredInTimeFrame(
        self, start: str, end: str
    ) -> list[Person]:
        pass
