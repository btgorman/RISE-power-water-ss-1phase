# Copyright 2017 Brandon T. Gorman

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# BUILT USING PYTHON 3.6.0

import numpy as np
import subprocess
import sys

number_of_sims = 501

power_load_lb = 0.3388
power_load_ub = 1.0

plf_array = np.linspace(power_load_lb, power_load_ub, number_of_sims)

for i in range(0, len(plf_array)):
	if (i+1)%10 == 0:
		print(i+1)

	pid = subprocess.call('python power_only_n1.py {}'.format(plf_array[i]), shell=True)