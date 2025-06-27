from src.lightEval.frblimp import frblimp
from src.lightEval.frcola import frcola_task
from sickfr import sickfr
from gqnli import gqnli
from allocine import allocine
from fquad import fquad
from piaf import piaf
from src.lightEval.opus_parcus import opus_parcus
from sts22 import sts22
from paws_x import paws_x
from xnli import xnli
print("imported custom tasks")
TASKS_TABLE = [frcola_task, sickfr, gqnli, allocine, fquad, paws_x, piaf, sts22, xnli, frblimp, opus_parcus]
