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

import subprocess
import sys
import numpy as np

power_load_lb = 0.3388
power_load_ub = 1.0
power_sims = 3

water_demand_lb = 0.372453
water_demand_ub = 2.984
water_sims = 35

# plf_array = np.linspace(power_load_lb, power_load_ub, power_sims)
# wdf_array = np.linspace(water_demand_lb, water_demand_ub, water_sims)

plf_array = np.linspace(0.7, 0.9, power_sims)
wdf_array = np.linspace(1.2, 2.8, water_sims)

for pidx in range(0, power_sims):
	for widx in range(0, water_sims):
		if wdf_array[widx] >= 2.18:
			pid = subprocess.call('python main_analysis.py {} {}'.format(plf_array[pidx], wdf_array[widx]), shell=True)