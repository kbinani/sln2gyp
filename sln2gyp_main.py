#!/usr/bin/env python

import sln2gyp
import sys

solution_file = sys.argv[1]
solution = sln2gyp.Solution(solution_file)
generator = sln2gyp.Generator()
generator.generate_gyp(solution)
