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

    def getEntityById(self, entity_id: str) -> IdentifiableEntity | None:  # Simone
        connected_metahandler = None
        entity_dataframe = None
        for meta in self.metadataQuery:
            entity_dataframe = meta.getById(entity_id)
            if len(entity_dataframe.index) != 0:
                connected_metahandler = meta
                break
        if len(entity_dataframe.index) == 0:
            return None
        else:
            if ":" in entity_id:
                row = entity_dataframe.loc[0]
                person_name = row["name"]
                person_id = entity_id
                result = Person(person_id, person_name)
                return result
            else:
                list_of_authors = list()
                authors = connected_metahandler.getAuthorsOfCulturalHeritageObject(
                    entity_id
                )
                for indx, row in authors.iterrows():
                    person_name = row["author_name"]
                    person_id = row["id"]
                    author = Person(person_id, person_name)
                    list_of_authors.append(author)

                row = entity_dataframe.loc[0]
                object_title = row["title"]
                if row["date"] != "":
                    object_date = row["date"]
                else:
                    object_date = None
                object_authors = list_of_authors
                object_owner = row["owner"]
                object_place = row["place"]
                object_type = row["type"]

                base_url = "https://breaking-data.github.io/Data-Science-Project/"

                if object_type == base_url + "NauticalChart":
                    new_object = NauticalChart(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "ManuscriptPlate":
                    new_object = ManuscriptPlate(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "ManuscriptVolume":
                    new_object = ManuscriptVolume(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "PrintedVolume":
                    new_object = PrintedVolume(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "PrintedMaterial":
                    new_object = PrintedMaterial(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "Herbarium":
                    new_object = Herbarium(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "Specimen":
                    new_object = Specimen(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "Painting":
                    new_object = Painting(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == base_url + "Model":
                    new_object = Model(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                elif object_type == "http://schema.org/Map":
                    new_object = Map(
                        entity_id,
                        object_title,
                        object_owner,
                        object_place,
                        object_date,
                        object_authors,
                    )
                else:
                    new_object = None

                return new_object

    def getAllPeople(self) -> list[Person]:  # Romolo
        people = dict()
        for metaGrinder in self.metadataQuery:
            df_people = metaGrinder.getAllPeople()

            for index, row in df_people.iterrows():
                person_name = row["name"]
                person_id = row["id"]
                person = Person(person_id, person_name)
                people[person_id] = person

        return list(people.values())

    def getAllCulturalHeritageObjects(self) -> list[CulturalHeritageObject]:  # Ludovica
        cultural_objects = dict()
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
                cultural_objects[ob_id] = instance

        return list(cultural_objects.values())

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
        activities = []
        for processGrinder in self.processQuery:
            df_process = processGrinder.getAllActivities()
            for idx, row in df_process.iterrows():
                object_id = str(row["objectId"])
                cultural_object = self.getEntityById(object_id)
                institute = row["responsibleInstitute"]
                person = row["responsiblePerson"]
                tool = row["tool"]
                start = row["startDate"]
                end = row["endDate"]
                internal = row["internalId"]

                if "acquisition" in internal.lower():
                    technique = row["technique"]
                    activity = Acquisition(
                        technique, institute, cultural_object, person, tool, start, end
                    )
                elif "processing" in internal:
                    activity = Processing(
                        institute, cultural_object, person, tool, start, end
                    )
                elif "exporting" in internal:
                    activity = Exporting(
                        institute, cultural_object, person, tool, start, end
                    )
                elif "modelling" in internal:
                    activity = Modelling(
                        institute, cultural_object, person, tool, start, end
                    )
                else:
                    activity = Optimising(
                        institute, cultural_object, person, tool, start, end
                    )

                activities.append(activity)

        return activities

    def getActivitiesByResponsibleInstitution(
        self, partialName: str
    ) -> list[Activity]:  # Ludovica
        activities = []
        for activity in self.getAllActivities():
            resp_inst = activity.getResposibleInstitute()
            # check if a responsible institute exists and if the input matches it
            if resp_inst and partialName.lower() in resp_inst.lower():
                activities.append(activity)
        return activities

    def getActivitiesByResponsiblePerson(
        self, partialName: str
    ) -> list[Activity]:  # Romolo
        activities = []
        for activity in self.getAllActivities():
            if partialName in activity.getResponsiblePerson():
                activities.append(activity)
        return activities

    def getActivitiesUsingTool(self, partialName) -> list[Activity]:  # Simone
        activities = []
        for activity in self.getAllActivities():
            for tl in activity.getTools():
                if partialName in tl:
                    activities.append(activity)
                    break
        return activities

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

    def getAcquisitionsByTechnique(
        self, partialName: str
    ) -> list[Acquisition]:  # Ludovica
        activities = []
        for activity in self.getAllActivities():
            if isinstance(activity, Acquisition):
                tecnique = activity.getTechnique()
                # check if a technique exists and if the input matches it
                if tecnique and partialName.lower() in tecnique.lower():
                    activities.append(activity)
        return activities


class AdvancedMashup(BasicMashup):
    def getActivitiesOnObjectsAuthoredBy(
        self, personId: str
    ) -> list[Activity]:  # Ludovica
        for obj in self.getCulturalHeritageObjectsAuthoredBy(personId):
            pass

    def getObjectsHandledByResponsiblePerson(
        self, partialName: str
    ) -> list[CulturalHeritageObject]:  # Simone
        pass

    def getObjectsHandledByResponsibleInstitution(
        self, partialName: str
    ) -> list[CulturalHeritageObject]:  # Romolo
        objects = set()
        for activity in self.getActivitiesByResponsibleInstitution(partialName):
            objects.add(activity.refersTo())
        return list(objects)

    def getAuthorsOfObjectsAcquiredInTimeFrame(
        self, start: str, end: str
    ) -> list[Person]:  # Pietro
        started_from = self.getActivitiesStartedAfter(self, start)
        activities_in_timeframe = []
        for activity in started_from:
            if activity.getendDate() <= end:
                activities_in_timeframe.append(activity)

        acqisitions_in_timeframe = []
        for activity in activities_in_timeframe:
            if isinstance(activity, Acquisition):
                acqisitions_in_timeframe.append(activity)

        objects = []
        for acquisition in acqisitions_in_timeframe:
            objects.append(acquisition.refersTo())

        authors = []
        for object in objects:
            authors.append(object.getAuthors())

        return authors
