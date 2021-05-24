#!/usr/bin/env python3
import re
import numpy as np
import os
pjoin = os.path.join
from hepdata_lib import Submission
from signal_templates import make_signal_template_tables
from yield_tables import make_yield_tables
from likelihood_tables import make_likelihood_tables
from cutflows import cutflow
from limits import limits
from ak8_tag import ak8_tag
def main():
    sub = Submission()
    make_signal_template_tables(sub)
    make_yield_tables(sub)
    sub.add_additional_resource(
        description="Generator configuration files for signal sample generation.",
        location="./input/generator_cards.tgz",
        copy_file=True
    )
    make_likelihood_tables(sub)
    cutflow(sub)
    limits(sub)
    ak8_tag(sub)
    sub.create_files('./output')

if __name__ == "__main__":
    main()