import os

from Benchmarks import AllocineBench, Paws_xBench, FquadBench, Opus_parcusBench, GqnliBench, FrblimpBench, \
    PiafBench, SickfrBench, XnliBench

DATASETS = ["Allocine", "paws_x", "fquad", "opus_parcus", "gqnli", "multiblimp", "piaf", "sickfr", "Xnli"]
def create_from_file(file):
    filename = os.path.splitext(os.path.basename(file.name))[0]
    print(filename)  # → 'file'
    match filename :
        case "Allocine":
            return AllocineBench()
        case "paws_x":
            return Paws_xBench()
        case "fquad":
            return FquadBench()
        case "opus_parcus":
            return Opus_parcusBench()
        case "gqnli":
            return GqnliBench()
        case "multiblimp":
            return FrblimpBench()
        case "piaf":
            return PiafBench()
        case "sickfr":
            return SickfrBench()
        case "Xnli":
            return XnliBench()