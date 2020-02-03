#!/usr/bin/env python3

import json

import attr
from attr.validators import instance_of, optional
from flask import Flask, request

import common
from common import S1Instance, S2Instance

app = Flask(__name__)


@attr.s
class RegistryState:
    s1_instances = attr.ib(validator=optional(instance_of(dict)), default=attr.Factory(dict))
    s2_instance = attr.ib(validator=optional(instance_of(S1Instance)), default=None)


STATE = RegistryState()


@app.route('/stage_1', methods=['GET'])
def get_stage_1():
    return json.dumps(list(attr.asdict(i) for i in STATE.s1_instances.values()))


@app.route('/stage_1', methods=['POST'])
def post_stage_1():
    instance = S1Instance.from_dict(request.args)
    STATE.s1_instances[instance.id] = instance
    return "OK"


@app.route('/stage_1', methods=['DELETE'])
def delete_stage_1():
    instance = S1Instance.from_dict(request.args)
    STATE.s1_instances.pop(instance.id)
    return "OK"


@app.route('/stage_2', methods=['GET'])
def get_stage_2():
    return json.dumps(attr.asdict(STATE.s2_instance) if STATE.s2_instance else None)


@app.route('/stage_2', methods=['POST'])
def post_stage_2():
    instance = S2Instance.from_dict(request.args)
    STATE.s2_instance = instance
    return ""


@app.route('/stage_2', methods=['DELETE'])
def delete_stage_2():
    STATE.s2_instance = None
    return "OK"


if __name__ == '__main__':
    app.run(host='localhost', port=common.DefaultPorts.SERVICE_REGISTRY, debug=True)
