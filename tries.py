from pandas import DataFrame, read_sql
from handler import *
from sqlite3 import connect
import pandas as pd
from mashup import BasicMashup, AdvancedMashup
from cultural_objects import *

# Prima di eseguire i test verifica di avere nei database i dati aggiornati

metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl(
    "http://192.168.158.53:9999/blazegraph/"
)  # verifica che sia il tuo url

process_qh = ProcessDataQueryHandler()
process_qh.setDbPathOrUrl("relational.db")  # verifica che sia il tuo path

mashup = AdvancedMashup()

with open("tests_output.txt", mode="w", encoding="utf-8") as file:
    file.write("TEST DEI METODI BasicMashup-AdvancedMashup\n\n\n")

    file.write("Add e Clean test  -->\n\n")

    file.write(f"Add metadata handler: {mashup.addMetadataHandler(metadata_qh)}\n")
    file.write(f"Add process handler: {mashup.addProcessHandler(process_qh)}\n")
    file.write(f"Clean metadata handlers: {mashup.cleanMetadataHandlers()}\n")
    file.write(f"Clean process handlers: {mashup.cleanProcessHandlers()}\n")

    mashup.addMetadataHandler(metadata_qh)
    mashup.addProcessHandler(process_qh)

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- metodi getAllXxx test -->\n\n")

    file.write(f"Numero totale di attività: {len(mashup.getAllActivities())}\n")
    file.write(f"Numero totale di autori: {len(mashup.getAllPeople())}\n")
    file.write(
        f"Numero totale di oggetti culturali: {len(mashup.getAllCulturalHeritageObjects())}"
    )

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getAuthorsOfCulturalHeritageObject test -->\n\n")

    auths_1 = mashup.getAuthorsOfCulturalHeritageObject("1")
    auths_2 = mashup.getAuthorsOfCulturalHeritageObject("2")
    auths_28 = mashup.getAuthorsOfCulturalHeritageObject("28")
    lista1 = [f"{auth}, id: {auth.getId()}, nome: {auth.getName()}" for auth in auths_1]
    lista2 = [f"{auth}, id: {auth.getId()}, nome: {auth.getName()}" for auth in auths_2]
    lista28 = [
        f"{auth}, id: {auth.getId()}, nome: {auth.getName()}" for auth in auths_28
    ]
    file.write(f"Autori dell'oggetto 1: {lista1}\n")
    file.write(f"Autori dell'oggetto 2: {lista2}\n")
    file.write(f"Autori dell'oggetto 28: {lista28}\n")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write(
        "\n<-- getCulturalHeritageObjectsAuthoredBy test  -->\nInput: VIAF:100219162 (id di Plinius Secundus, Gaius)\n\n"
    )

    plinius_objs = mashup.getCulturalHeritageObjectsAuthoredBy("VIAF:100219162")
    for obj in plinius_objs:
        file.write(
            f"type: {obj},\nid: {obj.getId()},\ntitle: {obj.getTitle()},\ndate: {obj.getDate()},\nowner: {obj.getOwner()},\nplace: {obj.getPlace()},\nauthors: {obj.getAuthors()}\n\n"
        )
    file.write(f"Numero di oggetti fatti da Plinius: {len(plinius_objs)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write(
        "\n<-- getActivitiesByResponsibleInstitution test  -->\nInput: couNCiL\n\n"
    )

    council_acts = mashup.getActivitiesByResponsibleInstitution("couNCiL")
    for act in council_acts:
        file.write(
            f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getStartDate()},\nend: {act.getEndDate()}\n\n"
        )
    file.write(f"Numero di attività fatte dall'istituto Council: {len(council_acts)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getActivitiesByResponsiblePerson test  -->\nInput: DOE\n\n")

    doe_acts = mashup.getActivitiesByResponsiblePerson("DOE")
    for act in doe_acts:
        file.write(
            f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getStartDate()},\nend: {act.getEndDate()}\n\n"
        )
    file.write(f"Numero di attività svolte da Doe: {len(doe_acts)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getActivitiesUsingTool test  -->\nInput: panasOnIC\n\n")

    panasonic_acts = mashup.getActivitiesUsingTool("panasOnIC")
    for act in panasonic_acts:
        file.write(
            f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getStartDate()},\nend: {act.getEndDate()}\n\n"
        )
    file.write(f"Numero di attività realizzate con Panasonic: {len(panasonic_acts)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getActivitiesStartedAfter test  -->\nInput: 2023-11-15\n\n")

    acts_started_post_2022 = mashup.getActivitiesStartedAfter("2023-11-15")
    for act in acts_started_post_2022:
        file.write(
            f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getStartDate()},\nend: {act.getEndDate()}\n\n"
        )
    file.write(
        f"Numero di attività iniziate dopo il 2023-11-15: {len(acts_started_post_2022)}"
    )

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getActivitiesEndedBefore test  -->\nInput: 2022-12-31\n\n")

    acts_ended_before_2022 = mashup.getActivitiesEndedBefore("2022-12-31")
    for act in acts_ended_before_2022:
        file.write(
            f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getStartDate()},\nend: {act.getEndDate()}\n\n"
        )
    file.write(
        f"Numero di attività finitie prima del 2022-12-31: {len(acts_ended_before_2022)}"
    )

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getAcquisitionsByTechnique test  -->\nInput: SCANNer\n\n")

    scanner_acquisition = mashup.getAcquisitionsByTechnique("SCANNer")
    for acq in scanner_acquisition:
        file.write(
            f"technique: {acq.getTechnique()},\ninstitute: {acq.getResponsibleInstitute()},\nobject: {acq.refersTo()},\nresponsible person: {acq.getResponsiblePerson()},\ntools: {acq.getTools()},\nstart: {acq.getStartDate()},\nend: {acq.getEndDate()}\n\n"
        )
    file.write(f"Numero di acquisizioni fatte con scanner: {len(scanner_acquisition)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write(
        "\n<-- getActivitiesOnObjectsAuthoredBy test  -->\nInput: DiscORIDES\n\n"
    )

    acts_on_discorides_objs = mashup.getActivitiesOnObjectsAuthoredBy("DiscORIDES")
    for act in acts_on_discorides_objs:
        file.write(
            f"type: {act},\ninstitute: {act.getResponsibleInstitute()},\nobject: {act.refersTo()},\nresponsible person: {act.getResponsiblePerson()},\ntools: {act.getTools()},\nstart: {act.getStartDate()},\nend: {act.getEndDate()}\n\n"
        )
    file.write(
        f"Numero di attività fatte sugli oggetti fatti da Discorides: {len(acts_on_discorides_objs)}"
    )

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write("\n<-- getObjectsHandledByResponsiblePerson test  -->\nInput: jAnE\n\n")

    pers_heritage_objs = mashup.getObjectsHandledByResponsiblePerson("jAnE")
    for obj in pers_heritage_objs:
        file.write(
            f"type: {obj},\nid: {obj.getId()},\ntitle: {obj.getTitle()},\ndate: {obj.getDate()},\nowner: {obj.getOwner()},\nplace: {obj.getPlace()},\nauthors: {obj.getAuthors()}\n\n"
        )
    file.write(f"Numero di oggetti gestiti da Jane: {len(pers_heritage_objs)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write(
        "\n<-- getObjectsHandledByResponsibleInstitution test  -->\nInput: heritAGE\n\n"
    )

    inst_heritage_objs = mashup.getObjectsHandledByResponsibleInstitution("heritAGE")
    for obj in inst_heritage_objs:
        file.write(
            f"type: {obj},\nid: {obj.getId()},\ntitle: {obj.getTitle()},\ndate: {obj.getDate()},\nowner: {obj.getOwner()},\nplace: {obj.getPlace()},\nauthors: {obj.getAuthors()}\n\n"
        )
    file.write(f"Numero di oggetti dell'istituto Heritage: {len(inst_heritage_objs)}")

    file.write(
        "\n\n----------------------------------------------------------------------------------\n"
    )
    file.write(
        "\n<-- getAuthorsOfObjectsAcquiredInTimeFrame test  -->\nInput: 2023-05, 2023-06\n\n"
    )

    obj_auths_acq_between_2021_2022 = mashup.getAuthorsOfObjectsAcquiredInTimeFrame(
        "2023-05", "2023-06"
    )
    for auth in obj_auths_acq_between_2021_2022:
        file.write(f"{auth}, id: {auth.getId()}, nome: {auth.getName()}\n")
    file.write(
        f"\nNumero di autori di oggetti acquisiti tra 2023-05 e 2023-06: {len(obj_auths_acq_between_2021_2022)}"
    )
print("!!! Verifica i risultati sul file tests_output.txt !!!")
