from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aos_meta_tool_adapter.api import (
    adapt_in,
    adapt_out,
    emit_runtime_config,
    init_registry,
    inspect_reference,
    list_registry,
    register_callable,
    register_local,
    register_wheel,
    registry_manifest,
    resolve_tool,
    run_chain,
    run_tool,
    tool_status,
    validate_registry,
)
from aos_meta_tool_adapter.utils.json import read_json


def _print(obj: object) -> None:
    sys.stdout.write(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='aos-tools', description='AoS Meta Tool Adapter CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('inspect-reference')

    init_reg = sub.add_parser('init-registry')
    init_reg.add_argument('--out', required=True)

    registry = sub.add_parser('registry')
    registry.add_argument('--registry-path')
    registry_sub = registry.add_subparsers(dest='registry_command', required=True)
    registry_sub.add_parser('list')
    registry_sub.add_parser('validate')
    registry_sub.add_parser('manifest')
    resolve = registry_sub.add_parser('resolve')
    resolve.add_argument('tool_id')

    register = sub.add_parser('register')
    register_sub = register.add_subparsers(dest='register_command', required=True)
    reg_wheel = register_sub.add_parser('wheel')
    reg_wheel.add_argument('--registry-path', required=True)
    reg_wheel.add_argument('--tool-id', required=True)
    reg_wheel.add_argument('--package', required=True)
    reg_wheel.add_argument('--entrypoint')
    reg_wheel.add_argument('--tool-name')

    reg_local = register_sub.add_parser('local')
    reg_local.add_argument('--registry-path', required=True)
    reg_local.add_argument('--tool-id', required=True)
    reg_local.add_argument('--path', required=True)
    reg_local.add_argument('--command')
    reg_local.add_argument('--tool-name')

    reg_callable = register_sub.add_parser('callable')
    reg_callable.add_argument('--registry-path', required=True)
    reg_callable.add_argument('--tool-id', required=True)
    reg_callable.add_argument('--callable', required=True)
    reg_callable.add_argument('--tool-name')

    tools = sub.add_parser('tools')
    tools.add_argument('--registry-path')
    tools_sub = tools.add_subparsers(dest='tools_command', required=True)
    tools_sub.add_parser('status')

    emit = sub.add_parser('emit-config')
    emit.add_argument('--out', required=True)

    run = sub.add_parser('run')
    run.add_argument('tool_id')
    run.add_argument('--input', required=True)
    run.add_argument('--out', required=True)
    run.add_argument('--allow-stub', action='store_true')
    run.add_argument('--registry-path')

    chain = sub.add_parser('chain')
    chain.add_argument('tool_ids', help='Comma-separated tool ids')
    chain.add_argument('--input', required=True)
    chain.add_argument('--out', required=True)
    chain.add_argument('--allow-stub', action='store_true')
    chain.add_argument('--registry-path')

    env = sub.add_parser('envelope')
    env.add_argument('--registry-path')
    env_sub = env.add_subparsers(dest='env_command', required=True)
    env_in = env_sub.add_parser('adapt-in')
    env_in.add_argument('tool_id')
    env_in.add_argument('--input', required=True)
    env_out = env_sub.add_parser('adapt-out')
    env_out.add_argument('tool_id')
    env_out.add_argument('--input', required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == 'inspect-reference':
        _print(inspect_reference())
        return 0
    if args.command == 'init-registry':
        _print(init_registry(args.out))
        return 0
    if args.command == 'registry':
        if args.registry_command == 'list':
            _print(list_registry(args.registry_path))
            return 0
        if args.registry_command == 'validate':
            result = validate_registry(args.registry_path)
            _print(result)
            return 0 if result.get('ok') else 1
        if args.registry_command == 'manifest':
            _print(registry_manifest(args.registry_path))
            return 0
        if args.registry_command == 'resolve':
            _print(resolve_tool(args.tool_id, args.registry_path))
            return 0
    if args.command == 'register':
        if args.register_command == 'wheel':
            _print(register_wheel(args.registry_path, tool_id=args.tool_id, package_name=args.package, entrypoint=args.entrypoint, tool_name=args.tool_name))
            return 0
        if args.register_command == 'local':
            _print(register_local(args.registry_path, tool_id=args.tool_id, local_path=args.path, command_template=args.command, tool_name=args.tool_name))
            return 0
        if args.register_command == 'callable':
            _print(register_callable(args.registry_path, tool_id=args.tool_id, callable_path=args.callable, tool_name=args.tool_name))
            return 0
    if args.command == 'tools' and args.tools_command == 'status':
        _print(tool_status(args.registry_path))
        return 0
    if args.command == 'emit-config':
        _print(emit_runtime_config(args.out))
        return 0
    if args.command == 'run':
        _print(run_tool(args.tool_id, args.input, args.out, allow_stub=args.allow_stub, registry_path=args.registry_path))
        return 0
    if args.command == 'chain':
        _print(run_chain([part.strip() for part in args.tool_ids.split(',') if part.strip()], args.input, args.out, allow_stub=args.allow_stub, registry_path=args.registry_path))
        return 0
    if args.command == 'envelope':
        if args.env_command == 'adapt-in':
            _print(adapt_in(args.tool_id, read_json(Path(args.input)), args.registry_path))
            return 0
        if args.env_command == 'adapt-out':
            _print(adapt_out(args.tool_id, read_json(Path(args.input)), args.registry_path))
            return 0
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
