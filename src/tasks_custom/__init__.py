import logging

from src.tasks_custom.qfrblimp import frblimp
from src.tasks_custom.qfrcola import frcola
from src.tasks_custom.sickfr import sickfr
from src.tasks_custom.gqnli import gqnli
from src.tasks_custom.allocine import allocine
from src.tasks_custom.fquad import fquad
from src.tasks_custom.piaf import piaf
from src.tasks_custom.opus_parcus import opus_parcus
from src.tasks_custom.sts22 import sts22
from src.tasks_custom.paws_x import paws_x
from src.tasks_custom.xnli import xnli

TASKS_TABLE = [
    frcola,
    sickfr,
    gqnli,
    allocine,
    fquad,
    paws_x,
    piaf,
    sts22,
    xnli,
    frblimp,
    opus_parcus,
]
logging.info(f"Imported custom tasks.")

REPO_ID = "COLLE-Graal/ColleGraal"
