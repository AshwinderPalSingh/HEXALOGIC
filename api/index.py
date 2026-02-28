import re

from flask import Flask, make_response, render_template, request

from core.controller import Controller
from core.util import fill_memory

CLEAR_TOKEN = "batman"
app = Flask(__name__, static_folder="static")
controller = Controller()

app.jinja_env.globals.update(zip=zip)

AT89C51_SFRS = [
    ("P0", "0x80"),
    ("SP", "0x81"),
    ("DPL", "0x82"),
    ("DPH", "0x83"),
    ("PCON", "0x87"),
    ("TCON", "0x88"),
    ("TMOD", "0x89"),
    ("TL0", "0x8A"),
    ("TL1", "0x8B"),
    ("TH0", "0x8C"),
    ("TH1", "0x8D"),
    ("P1", "0x90"),
    ("SCON", "0x98"),
    ("SBUF", "0x99"),
    ("P2", "0xA0"),
    ("IE", "0xA8"),
    ("P3", "0xB0"),
    ("IP", "0xB8"),
    ("PSW", "0xD0"),
    ("ACC", "0xE0"),
    ("B", "0xF0"),
]


def _hex8(value):
    return f"0x{int(str(value), 16) & 0xFF:02X}"


def _get_ram_and_rom():
    _memory_ram, _memory_rom = None, None
    _ram = fill_memory(controller.op.memory_ram, 256).sort()
    if _ram:
        _ram = list(_ram.items())
        _memory_ram = [_ram[x : x + 16] for x in range(0, len(_ram), 16)]

    _rom = fill_memory(controller.op.memory_rom, 256).sort()
    if _rom:
        _rom = list(_rom.items())
        _memory_rom = [_rom[x : x + 16] for x in range(0, len(_rom), 16)]

    return _memory_ram, _memory_rom


def _extract_error_line(message):
    match = re.search(r"(?:Runtime line|Line)\s+(\d+)", str(message))
    if not match:
        return None
    return int(match.group(1))


def _error_response(exc):
    msg = str(exc)
    return make_response({"error": msg, "line": _extract_error_line(msg)}, 400)


def _get_sfr_watch():
    rows = []
    for name, addr in AT89C51_SFRS:
        value = controller.op.memory_ram.read(addr)
        rows.append(
            {
                "name": name,
                "addr": f"0x{int(addr, 16):02X}",
                "value": _hex8(value),
                "bits": format(int(str(value), 16), "08b"),
            }
        )
    return rows


def _get_stack_preview(depth=10):
    sp = int(str(controller.op.memory_read("SP")), 16)
    rows = []
    for addr in range(sp, sp - depth, -1):
        if addr <= 0x07:
            break
        value = controller.op.memory_ram.read(format(addr, "#06x"))
        rows.append(
            {
                "address": f"0x{addr:02X}",
                "value": _hex8(value),
            }
        )
    return rows


def _get_sim_state():
    next_source_line = None
    if controller._run_idx < len(controller.callstack):
        _, _, _, kwargs = controller.callstack[controller._run_idx]
        next_source_line = kwargs.get("_source_line")
    return {
        "run_index": controller._run_idx,
        "instruction_count": len(controller.callstack),
        "ready": controller.ready,
        "next_source_line": next_source_line,
    }


def _get_assembler_rows():
    rows = []
    for idx, (source, opcode_bytes) in enumerate(controller.op._assembler.items()):
        source_line = None
        if idx < len(controller.callstack):
            _, _, _, kwargs = controller.callstack[idx]
            source_line = kwargs.get("_source_line")
        rows.append(
            {
                "index": idx,
                "source": source,
                "opcode": opcode_bytes,
                "source_line": source_line,
            }
        )
    return rows


def _render_payload(active_index=None, step=None):
    ram, rom = _get_ram_and_rom()
    payload = {
        "registers_flags": render_template(
            "render_registers_flags.html",
            registers=controller.op.super_memory._registers_todict(),
            flags=controller.op.super_memory.PSW.flags(),
            general_purpose_registers=controller.op.super_memory._general_purpose_registers,
            sfr_watch=_get_sfr_watch(),
            stack_preview=_get_stack_preview(),
            sim_state=_get_sim_state(),
        ),
        "memory": render_template("render_memory.html", ram=ram, rom=rom),
        "assembler": render_template(
            "render_assembler.html",
            assembler_rows=_get_assembler_rows(),
            active_index=active_index,
        ),
        "state": _get_sim_state(),
    }
    if step is not None:
        payload["step"] = step
    return payload


@app.route("/reset", methods=["POST"])
def reset():
    global controller
    controller.reset()
    return _render_payload()


@app.route("/assemble", methods=["POST"])
def assemble():
    global controller
    commands = request.get_json(silent=True) or {}
    source_code = commands.get("code")
    flags = commands.get("flags", {})

    if source_code is None:
        return make_response({"error": "Code not found", "line": None}, 400)

    try:
        controller.reset_callstack()
        controller.set_flags(flags)
        controller.parse_all(source_code)
        return _render_payload()
    except Exception as e:
        return _error_response(e)


@app.route("/run", methods=["POST"])
def run():
    global controller
    if controller.ready:
        try:
            step = controller.run()
            return _render_payload(active_index=step.get("executed_index"), step=step)
        except Exception as e:
            return _error_response(e)
    return make_response({"error": "Controller not ready", "line": None}, 400)


@app.route("/run-once", methods=["POST"])
def step():
    global controller
    if controller.ready:
        try:
            step_data = controller.run_once()
            return _render_payload(active_index=step_data.get("executed_index"), step=step_data)
        except Exception as e:
            return _error_response(e)
    return make_response({"error": "Controller not ready", "line": None}, 400)


@app.route("/memory-edit", methods=["POST"])
def update_memory():
    global controller
    mem_data = request.get_json(silent=True)
    if mem_data:
        try:
            for memloc, memvalue in mem_data:
                controller.op.memory_ram.write(memloc, memvalue)
            return _render_payload(active_index=controller._run_idx)
        except Exception as e:
            return _error_response(e)
    return make_response({"error": "Controller not ready", "line": None}, 400)


@app.route("/", methods=["GET"])
def main():
    global controller
    controller = Controller()
    ram, rom = _get_ram_and_rom()
    return render_template(
        "index.html",
        ram=ram,
        rom=rom,
        registers=controller.op.super_memory._registers_todict(),
        general_purpose_registers=controller.op.super_memory._general_purpose_registers,
        flags=controller.op.super_memory.PSW.flags(),
        sfr_watch=_get_sfr_watch(),
        stack_preview=_get_stack_preview(),
        sim_state=_get_sim_state(),
        assembler_rows=_get_assembler_rows(),
        active_index=None,
    )
