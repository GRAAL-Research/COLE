import logging

from src.tasks_custom.qfrblimp import qfrblimp
from src.tasks_custom.qfrcola import qfrcola
from src.tasks_custom.sickfr import sickfr
from src.tasks_custom.gqnli import gqnli
from src.tasks_custom.allocine import allocine
from src.tasks_custom.fquad import fquad
from src.tasks_custom.piaf import piaf
from src.tasks_custom.opus_parcus import opus_parcus
from src.tasks_custom.sts22 import sts22
from src.tasks_custom.paws_x import paws_x
from src.tasks_custom.xnli import xnli

BASE_TASKS = [
    "allocine",
    "paws_x",
    "fquad",
    "gqnli",
    "piaf",
    "sickfr",
    "xnli",
    "qfrcola",
    "qfrblimp",
    "sts22",
]

TASKS_TABLE = [
    qfrcola,
    sickfr,
    gqnli,
    allocine,
    fquad,
    paws_x,
    piaf,
    sts22,
    xnli,
    qfrblimp,
    opus_parcus,
]
logging.info(f"Imported custom tasks.")
