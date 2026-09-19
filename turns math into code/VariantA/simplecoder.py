import sys
import autowire
from engine import run_engine
from lattice import run_lattice

if __name__ == "__main__":
    selected = sys.argv[1] if len(sys.argv) > 1 else ""
    print(run_engine(selected))
    print(run_lattice(size=5, ticks=200))