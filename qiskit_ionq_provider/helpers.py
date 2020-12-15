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
Helper methods for mapping a qobj (:mod:`Qiskit Quantum Objects <qiskit.qobj>`)
to IonQ REST API compatible values.
"""

import json

from qiskit.circuit import controlledgate as q_cgates
from qiskit.circuit.library import standard_gates as q_gates

from . import exceptions


def qiskit_circ_to_ionq_circ(circ):
    """Build a circuit in IonQ's instruction format from qiskit instructions.

    .. ATTENTION:: This function ignores the following compiler directives:

       * ``barrier``

    .. ATTENTION::
       The following instructions are currently **unsupported**:

       * ``reset``
       * ``u1``
       * ``u2``
       * ``u3``
       * ``cu1``
       * ``cu2``
       * ``cu3``

    Parameters:
        circ (:class:`QuantumCircuit <qiskit.circuit.QuantumCircuit>`): A quantum circuit.

    Raises:
        IonQGateError: If an unsupported instruction is supplied.

    Returns:
        list[dict]: A list of instructions in a converted dict format.
        int: The number of measurements.
        dict: The measurement map from qubit number to classical bit number.
    """
    compiler_directives = ["barrier"]
    unsupported_instructions = [
        "reset",
        "u1",
        "u2",
        "u3",
        "cu1",
        "cu2",
        "cu3",
    ]
    circuit = []
    num_meas = 0
    meas_map = {}
    for instruction, qargs, cargs in circ.data:
        # Don't process compiler directives.
        instruction_name = instruction.name
        if instruction_name in compiler_directives:
            continue

        # Don't process measurement instructions.
        if instruction_name == "measure":
            meas_map[int(qargs[0].index)] = cargs[0].index
            num_meas += 1
            continue

        # Raise out for instructions we don't support.
        if instruction_name in unsupported_instructions:
            raise exceptions.IonQGateError(instruction_name)

        # Process the instruction and convert.
        rotation = {}
        if any(instruction.params):
            # The float is here to cast Qiskit ParameterExpressions to numbers
            rotation = {"rotation": float(instruction.params[0])}

        # Default conversion is simple, just gate & target.
        converted = {"gate": instruction_name, "targets": [qargs[0].index]}

        # Make sure swap uses all qargs.
        if isinstance(instruction, q_gates.SwapGate):
            converted["targets"] = [qargs[0].index, qargs[1].index]
        # If this is a controlled gate, make sure to set control qubits.
        elif isinstance(instruction, q_cgates.ControlledGate):
            gate = instruction_name[1:]
            controls = [qargs[0].index]
            targets = [qargs[1].index]
            # If this is a "double" control, we use two control qubits.
            if gate[0] == "c":
                gate = gate[1:]
                controls = [qargs[0].index, qargs[1].index]
                targets = [qargs[2].index]
            elif gate == "swap":
                # If this is a cswap, we have two targets:
                targets = [qargs[-2].index, qargs[-1].index]

            # Update converted gate values.
            converted.update(
                {
                    "gate": gate,
                    "controls": controls,
                    "targets": targets,
                }
            )

        circuit.append({**converted, **rotation})

    return circuit, num_meas, meas_map


def qiskit_to_ionq(circuit, backend_name, passed_args=None):
    """Convert a Qiskit circuit to a IonQ compatible dict.

    Parameters:
        circuit (:class:`qiskit.circuit.QuantumCircuit`): A Qiskit quantum circuit.
        backend_name (str): Backend name.
        passed_args (dict): Dictionary containing additional passed arguments, eg. shots.

    Returns:
        dict: A dict with IonQ API compatible values.
    """
    passed_args = passed_args or {}
    ionq_circ, num_meas, meas_map = qiskit_circ_to_ionq_circ(circuit)

    ionq_json = {
        "lang": "json",
        "target": backend_name[5:],
        "shots": passed_args["shots"],
        "body": {
            "qubits": circuit.num_qubits,
            "circuit": ionq_circ,
        },
        # store a couple of things we'll need later for result formatting
        "metadata": {
            "shots": str(passed_args["shots"]),
            "output_map": json.dumps(meas_map),
            "header": json.dumps({"memory_slots": circuit.num_clbits}),
        },
    }
    return json.dumps(ionq_json)


__all__ = ["qiskit_to_ionq", "qiskit_circ_to_ionq_circ"]
