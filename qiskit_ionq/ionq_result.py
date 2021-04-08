# -*- coding: utf-8 -*-
# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# Copyright 2020 IonQ, Inc. (www.ionq.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
IonQ result implementation that extends to allow for retrieval of probabilities.
"""

from qiskit.exceptions import QiskitError
from qiskit.result import Result
from qiskit.result.counts import Counts
from . import exceptions


class IonQResult(Result):
    def __init__(
        self,
        backend_name,
        backend_version,
        qobj_id,
        job_id,
        success,
        results,
        date=None,
        status=None,
        header=None,
        **kwargs
    ):
        super().__init__(
            backend_name,
            backend_version,
            qobj_id,
            job_id,
            success,
            results,
            date=date,
            status=status,
            header=header,
            **kwargs,
        )

    def get_probabilities(self, experiment=None):
        if experiment is None:
            exp_keys = range(len(self.results))
        else:
            exp_keys = [experiment]

        dict_list = []
        for key in exp_keys:
            exp = self._get_experiment(key)
            try:
                header = exp.header.to_dict()
            except (AttributeError, QiskitError):  # header is not available
                header = None

            if "probabilities" in self.data(key).keys():
                if header:
                    counts_header = {
                        k: v
                        for k, v in header.items()
                        if k in {"time_taken", "creg_sizes", "memory_slots"}
                    }
                else:
                    counts_header = {}
                dict_list.append(Counts(self.data(key)["probabilities"], **counts_header))
            else:
                raise exceptions.IonQJobError(
                    'No probabilities for experiment "{}"'.format(repr(key))
                )

        # Return first item of dict_list if size is 1
        if len(dict_list) == 1:
            return dict_list[0]
        else:
            return dict_list
