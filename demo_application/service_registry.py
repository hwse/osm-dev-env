#!/usr/bin/env python3

import json

import attr
from attr.validators import instance_of, optional
from flask import Flask, request

app = Flask(__name__)


@attr.s(frozen=True)
class S1Instance:
    id = attr.ib(converter=int, validator=instance_of(int))
    host = attr.ib(validator=instance_of(str))
    port = attr.ib(converter=int, validator=instance_of(int))


@attr.s(frozen=True)
class S2Instance:
    host = attr.ib(validator=instance_of(str))
    port = attr.ib(converter=int, validator=instance_of(int))


@attr.s
class RegistryState:
    s1_instances = attr.ib(validator=optional(instance_of(dict)), default=attr.Factory(dict))
    s2_instance = attr.ib(validator=optional(instance_of(S1Instance)), default=None)


STATE = RegistryState()


@app.route('/stage_1', methods=['GET'])
def get_stage_1():
    return json.dumps(list(attr.asdict(i) for i in STATE.s1_instances.values()))


@app.route('/stage_1', methods=['POST'])
def put_stage_1():
    host_id = request.args.get('id')
    host = request.args.get('host')
    port = request.args.get('port')
    instance = S1Instance(host_id, host, port)
    STATE.s1_instances[instance.id] = instance
    return ""


@app.route('/stage_2', methods=['GET'])
def get_stage_2():
    return json.dumps(attr.asdict(STATE.s2_instance) if STATE.s2_instance else None)


@app.route('/stage_2', methods=['POST'])
def put_stage_2():
    host = request.args.get('host')
    port = request.args.get('port')
    instance = S2Instance(host, port)
    STATE.s2_instance = instance
    return ""


if __name__ == '__main__':
    app.run(debug=True)
