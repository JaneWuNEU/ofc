"""The dataset generator.

Classes:

 * `GeneratorState`: representation of the generator's checkpointed state (a namedtuple)

Methods:

 * `generate`: main method to generate the dataset, handling failures and interruptions by signals to return its state
 * `generate_one`: run one iteration of the dataset generation, i.e. prepare and invoke one action and store the data

Constant:

 * `TRACEPOINT_MAX_WAIT_ERROR`: maximum error in waiting before the next trace point

Exceptions:

 * `GeneratorException`
"""
from collections import Generator, namedtuple
from datetime import timedelta
from random import Random

from . import functions
from .database import FaaSLoadDatabaseException
from .injection import InjectionTracePoint

INPUT_EXTENSIONS = {
    'image': 'jpg',
    'audio': 'wav',
    'video': 'avi',
}

GeneratedInjectionTraceState = namedtuple('GeneratedInjectionTraceState', ['user', 'function', 'rng', 'next_input'])


class GeneratedInjectionTrace(Generator):
    def __init__(self, user, function, inter_invoc_time, last_input_id, rng_seed=None):
        self.user = user
        self.function = function
        self.inter_invoc_time = inter_invoc_time
        self.last_input_id = last_input_id

        self.rng = Random(rng_seed)
        self.next_input_id = 1

        self.input_extension = INPUT_EXTENSIONS[function.input_kind]
        self.params_to_generate = [param for param in self.function.parameters if param['name'] != 'object']

    def send(self, _):
        if self.next_input_id > self.last_input_id:
            raise StopIteration

        try:
            params = {param['name']: self._prepare_parameter(param) for param in self.params_to_generate}
            params['object'] = str(self.next_input_id) + '.' + self.input_extension
            params['incont'] = self.function.input_kind
            params['outcont'] = self.user + '-out'
        except (KeyError, ValueError) as err:
            raise GenerationException(
                f'failed preparing parameters for run {self.next_input_id} of {self.function.name} trace '
                f'of user {self.user}'
            ) from err

        self.next_input_id += 1

        return InjectionTracePoint(timedelta(seconds=self.inter_invoc_time), params)

    def throw(self, *args):
        # must be implemented because declared abstract, but I just redirect it to the existing super() implementation
        super().throw(*args)

    def get_state(self):
        return GeneratedInjectionTraceState(self.user, self.function, self.rng.getstate(), self.next_input_id)

    def set_state(self, state):
        self.rng.setstate(state.rng)
        self.next_input_id = state.next_input

    def _prepare_parameter(self, param):
        if param['type'] == 'range_float':
            value = self.rng.uniform(param['min'], param['max'])
        elif param['type'] == 'range_int':
            value = self.rng.randint(param['min'], param['max'])
        elif param['type'] == 'ensemble':
            value = self.rng.choice(param['values'])
        else:
            raise ValueError(f'unknown parameter type "{param["type"]}"')

        return value


def build_traces(db, gen_cfg, state=None):
    if state:
        traces = []
        for trace_state in [st.trace_state for st in state]:
            trace = GeneratedInjectionTrace(
                user=trace_state.user,
                function=trace_state.function,
                inter_invoc_time=gen_cfg.interinvocationtime,
                last_input_id=gen_cfg.nbinputs[trace_state.function.input_kind]
            )
            trace.set_state(trace_state)
            traces.append(trace)
    else:
        try:
            funcs = db.select_functions()
        except FaaSLoadDatabaseException as err:
            raise GenerationException('failed fetching list of functions from database') from err

        traces = [GeneratedInjectionTrace(
            user=f'user-{functions.basename(func.name)}',
            function=func,
            inter_invoc_time=gen_cfg.interinvocationtime,
            last_input_id=gen_cfg.nbinputs[func.input_kind],
            rng_seed=gen_cfg.seed,
        ) for func in funcs]

    return traces


class GenerationException(Exception):
    pass
