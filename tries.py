from pandas import DataFrame, read_sql
from handler import *
from sqlite3 import connect
import pandas as pd
from mashup import BasicMashup, AdvancedMashup
from cultural_objects import *

# Prima di eseguire i test verifica di avere nei database i dati aggiornati

metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl("http://192.168.1.197:9999/blazegraph/") # verifica che sia il tuo url

process_qh = ProcessDataQueryHandler()
process_qh.setDbPathOrUrl("relational.db") # verifica che sia il tuo path

mashup = AdvancedMashup()

with open("tests_output.exe", mode="w", encoding="utf-8") as file:
    file.write("TEST DEI METODI BasicMashup-AdvancedMashup\n\n\n")
    
    file.write("Add e Clean test\n\n")

    file.write(f"Add metadata handler: {mashup.addMetadataHandler(metadata_qh)}\n")
    file.write(f"Add process handler: {mashup.addProcessHandler(process_qh)}\n")
    file.write(f"Clean metadata handlers: {mashup.cleanMetadataHandlers()}\n")
    file.write(f"Clean process handlers: {mashup.cleanProcessHandlers()}\n")


    mashup.addMetadataHandler(metadata_qh)
    mashup.addProcessHandler(process_qh)

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\nmetodi getAllXxx test\n\n")

    file.write(f"Numero totale di attività: {len(mashup.getAllActivities())}\n")
    file.write(f"Numero totale di autori: {len(mashup.getAllPeople())}\n")
    file.write(f"Numero totale di oggetti culturali: {len(mashup.getAllCulturalHeritageObjects())}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetAuthorsOfCulturalHeritageObject test\n\n")

    auths_1 = mashup.getAuthorsOfCulturalHeritageObject("1")
    auths_2 = mashup.getAuthorsOfCulturalHeritageObject("2")
    auths_28 = mashup.getAuthorsOfCulturalHeritageObject("28")
    lista1 = [f"{auth}, id: {auth.getId()}, nome: {auth.getName()}" for auth in auths_1]
    lista2 = [f"{auth}, id: {auth.getId()}, nome: {auth.getName()}" for auth in auths_2]
    lista28 = [f"{auth}, id: {auth.getId()}, nome: {auth.getName()}" for auth in auths_28]
    file.write(f"Autori dell'oggetto 1: {lista1}\n")
    file.write(f"Autori dell'oggetto 2: {lista2}\n")
    file.write(f"Autori dell'oggetto 28: {lista28}\n")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetCulturalHeritageObjectsAuthoredBy test\nInput: VIAF:100219162 (id di Plinius Secundus, Gaius)\n")

    plinius_objs = mashup.getCulturalHeritageObjectsAuthoredBy("VIAF:100219162")
    for obj in plinius_objs:
        file.write(f"type: {obj},\nid: {obj.getId()},\ntitle: {obj.getTitle()},\ndate: {obj.getDate()},\nowner: {obj.getOwner()},\nplace: {obj.getPlace()},\nauthors: {obj.getAuthors()}\n\n")
    file.write(f"Numero di oggetti fatti da Plinius: {len(plinius_objs)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetActivitiesByResponsibleInstitution test\nInput: couNCiL\n\n")

    council_acts = mashup.getActivitiesByResponsibleInstitution("couNCiL")
    for act in council_acts:
        file.write(f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getstartDate()},\nend: {act.getendDate()}\n\n")
    file.write(f"Numero di attività fatte dall'istituto Council: {len(council_acts)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetActivitiesByResponsiblePerson test\nInput: DOE\n\n")

    doe_acts = mashup.getActivitiesByResponsiblePerson("DOE")
    for act in doe_acts:
        file.write(f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getstartDate()},\nend: {act.getendDate()}\n\n")
    file.write(f"Numero di attività svolte da Doe: {len(doe_acts)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetActivitiesUsingTool test\nInput: panasOnIC\n\n")

    panasonic_acts = mashup.getActivitiesUsingTool("panasOnIC")
    for act in panasonic_acts:
        file.write(f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getstartDate()},\nend: {act.getendDate()}\n\n")
    file.write(f"Numero di attività realizzate con Panasonic: {len(panasonic_acts)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetActivitiesStartedAfter test\nInput: 2023-11-15\n\n")

    acts_started_post_2022 = mashup.getActivitiesStartedAfter("2023-11-15")
    for act in acts_started_post_2022:
        file.write(f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getstartDate()},\nend: {act.getendDate()}\n\n")
    file.write(f"Numero di attività iniziate dopo il 2023-11-15: {len(acts_started_post_2022)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetActivitiesEndedBefore test\nInput: 2022-12-31\n\n")

    acts_ended_before_2022 = mashup.getActivitiesEndedBefore("2022-12-31")
    for act in acts_ended_before_2022:
        file.write(f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getstartDate()},\nend: {act.getendDate()}\n\n")
    file.write(f"Numero di attività finitie prima del 2022-12-31: {len(acts_ended_before_2022)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetAcquisitionsByTechnique test\nInput: SCANNer\n\n")

    scanner_acquisition = mashup.getAcquisitionsByTechnique("SCANNer")
    for acq in scanner_acquisition:
        file.write(f"technique: {acq.getTechnique()},\ninstitute: {acq.getResponsibleInstitute()},\nobject: {acq.refersTo()},\nresponsible person: {acq.getResponsiblePerson()},\ntools: {acq.getTools()},\nstart: {acq.getstartDate()},\nend: {acq.getendDate()}\n\n")
    file.write(f"Numero di acquisizioni fatte con scanner: {len(scanner_acquisition)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetActivitiesOnObjectsAuthoredBy test\nInput: DiscORIDES\n\n")

    acts_on_discorides_objs = mashup.getActivitiesOnObjectsAuthoredBy("DiscORIDES")
    for act in acts_on_discorides_objs:
        file.write(f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getstartDate()},\nend: {act.getendDate()}\n\n")
    file.write(f"Numero di attività fatte sugli oggetti fatti da Discorides: {len(acts_on_discorides_objs)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetObjectsHandledByResponsibleInstitution test\nInput: heritAGE\n\n")

    heritage_objs = mashup.getObjectsHandledByResponsibleInstitution("heritAGE")
    for obj in heritage_objs:
        file.write(f"type: {obj},\nid: {obj.getId()},\ntitle: {obj.getTitle()},\ndate: {obj.getDate()},\nowner: {obj.getOwner()},\nplace: {obj.getPlace()},\nauthors: {obj.getAuthors()}\n\n")
    file.write(f"Numero di oggetti dell'istituto Heritage: {len(heritage_objs)}")

    file.write("\n----------------------------------------------------------------------------------")
    file.write("\ngetAuthorsOfObjectsAcquiredInTimeFrame test\nInput: 2023-05, 2023-06\n\n")

    obj_auths_acq_between_2021_2022 = mashup.getAuthorsOfObjectsAcquiredInTimeFrame("2023-05", "2023-06")
    n_auths = 0 # Il conto verrà aggiornato solo se si avranno autori, le liste di autori vuote non vengono contate
    for auths in obj_auths_acq_between_2021_2022:
        if isinstance(auths, list):
            for auth in auths:
                file.write(f"{auth}, id: {auth.getId()}, nome: {auth.getName()}\n")
            if auths:
                n_auths += 1
        else:
            file.write(f"{auths}, id: {auths.getId()}, nome: {auths.getName()}\n")
            n_auths += 1
    file.write(f"\nNumero di autori di oggetti acquisiti tra 2023-05 e 2023-06: {n_auths}")
print("!!! Verifica i risultati sul file tests_output.exe !!!")