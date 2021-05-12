import re
import numpy as np
import os
pjoin = os.path.join
from hepdata_lib import Submission
from signal_templates import make_signal_template_tables
from yield_tables import make_yield_tables
def main():
    sub = Submission()
    # make_signal_template_tables(sub)
    make_yield_tables(sub)
    sub.create_files('./output')

if __name__ == "__main__":
    main()