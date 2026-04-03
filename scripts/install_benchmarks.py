#!/usr/bin/env python3
import argparse
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO_ROOT / "benchmarks" / "templates"


PICKER_CONFIG = {
    "XS": {"dut_class": "DUTSimTop", "bench_steps": 300000, "warmup_steps": 1000},
    "rocket": {"dut_class": "DUTSimTop", "bench_steps": 300000, "warmup_steps": 1000},
    "coupledL2": {"dut_class": "DUTTestTop", "bench_steps": 300000, "warmup_steps": 1000},
}

MULTILANG_CONFIG = {
    "XS": {
        "top_name": "SimTop",
        "module_name": "UT_SimTop",
        "dut_class_py": "DUTSimTop",
        "dut_class_cpp": "UTSimTop",
        "java_class": "UT_SimTop",
        "java_package": "com.ut",
        "java_main": "com.ut.example",
        "go_import": "UT_SimTop",
        "go_class": "UT_SimTop",
        "verilator_class": "VSimTop",
        "root_class": "VSimTop___024root",
        "top_prefix": "SimTop_top__DOT__",
        "bench_steps": 5000,
        "warmup_steps": 1000,
    },
    "rocket": {
        "top_name": "SimTop",
        "module_name": "UT_SimTop",
        "dut_class_py": "DUTSimTop",
        "dut_class_cpp": "UTSimTop",
        "java_class": "UT_SimTop",
        "java_package": "com.ut.SimTop",
        "java_main": "com.ut.SimTop.example",
        "go_import": "UT_SimTop",
        "go_class": "UT_SimTop",
        "verilator_class": "VSimTop",
        "root_class": "VSimTop___024root",
        "top_prefix": "SimTop_top__DOT__",
        "bench_steps": 2000000,
        "warmup_steps": 1000,
    },
    "coupledL2": {
        "top_name": "TestTop",
        "module_name": "UT_TestTop",
        "dut_class_py": "DUTTestTop",
        "dut_class_cpp": "UTTestTop",
        "java_class": "UT_TestTop",
        "java_package": "com.ut.TestTop",
        "java_main": "com.ut.TestTop.example",
        "go_import": "UT_TestTop",
        "go_class": "UT_TestTop",
        "verilator_class": "VTestTop",
        "root_class": "VTestTop___024root",
        "top_prefix": "TestTop_top__DOT__",
        "bench_steps": 2200000,
        "warmup_steps": 1000,
    },
}


def render_template(path, replacements):
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def write_file(path, content, create_parent=False):
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.exists():
        print(f"skipped {path} (parent missing)")
        return
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path}")


def patch_build_makefile_no_test(path):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    patched = text.replace("all: test clean", "all: compile clean")
    if patched != text:
        path.write_text(patched, encoding="utf-8")
        print(f"patched {path}")


def install_picker(root, dut, variants):
    cfg = PICKER_CONFIG[dut]
    destinations = {
        "python-dpi": root / "dpi_python" / "example.py",
        "python-vpi": root / "vpi_python" / "example.py",
        "python-mem_direct": root / "mem_python" / "example.py",
    }
    template = TEMPLATE_DIR / "picker_python.py.tpl"
    content = render_template(
        template,
        {
            "DUT_CLASS": cfg["dut_class"],
            "BENCH_STEPS": str(cfg["bench_steps"]),
            "WARMUP_STEPS": str(cfg["warmup_steps"]),
        },
    )
    for variant in variants:
        dest = destinations[variant]
        write_file(dest, content)
        variant_root = dest.parent
        for mk in variant_root.rglob("Makefile"):
            patch_build_makefile_no_test(mk)
    mem_makefile = root / "mem_python" / "mem_direct" / "Makefile"
    if "python-mem_direct" in variants and mem_makefile.exists():
        text = mem_makefile.read_text(encoding="utf-8")
        patched = text.replace(
            "LDLIBS += -lpthread -lz",
            "LDLIBS += -lpthread -lz -L/usr/local/lib -lxspcomm",
        )
        if patched != text:
            mem_makefile.write_text(patched, encoding="utf-8")
            print(f"patched {mem_makefile}")


def install_multilang(root, dut, variants):
    cfg = MULTILANG_CONFIG[dut]
    destinations = {
        "python": (
            TEMPLATE_DIR / "multilang_python.py.tpl",
            [
                root / "dpi_python" / "python" / "example.py",
                root / "dpi_python" / "example.py",
            ],
            {
                "MODULE_NAME": cfg["module_name"],
                "TOP_NAME": cfg["top_name"],
                "DUT_CLASS": cfg["dut_class_py"],
                "BENCH_STEPS": str(cfg["bench_steps"]),
                "WARMUP_STEPS": str(cfg["warmup_steps"]),
            },
        ),
        "cpp": (
            TEMPLATE_DIR / "multilang_cpp.cpp.tpl",
            [
                root / "dpi_cpp" / "cpp" / "example.cpp",
                root / "dpi_cpp" / f"UT_{cfg['top_name']}" / "example.cpp",
            ],
            {
                "HEADER_NAME": f"{cfg['module_name']}.hpp",
                "DUT_CLASS": cfg["dut_class_cpp"],
                "BENCH_STEPS": str(cfg["bench_steps"]),
                "WARMUP_STEPS": str(cfg["warmup_steps"]),
            },
        ),
        "java": (
            TEMPLATE_DIR / "multilang_java.java.tpl",
            [
                root / "dpi_java" / "java" / "example.java",
                root / "dpi_java" / "example.java",
            ],
            {
                "JAVA_CLASS": cfg["java_class"],
                "JAVA_PACKAGE": cfg["java_package"],
                "BENCH_STEPS": str(cfg["bench_steps"]),
                "WARMUP_STEPS": str(cfg["warmup_steps"]),
            },
        ),
        "golang": (
            TEMPLATE_DIR / "multilang_golang.go.tpl",
            [
                root / "dpi_golang" / "golang" / "example.go",
                root / "dpi_golang" / "example.go",
            ],
            {
                "GO_IMPORT": cfg["go_import"],
                "GO_CLASS": cfg["go_class"],
                "BENCH_STEPS": str(cfg["bench_steps"]),
                "WARMUP_STEPS": str(cfg["warmup_steps"]),
            },
        ),
        "raw-verilator": (
            TEMPLATE_DIR / "multilang_raw_verilator.cpp.tpl",
            [root / "dpi_cpp" / f"UT_{cfg['top_name']}raw" / "example.cpp"],
            {
                "VERILATOR_CLASS": cfg["verilator_class"],
                "ROOT_CLASS": cfg["root_class"],
                "TOP_PREFIX": cfg["top_prefix"],
                "BENCH_STEPS": str(cfg["bench_steps"]),
                "WARMUP_STEPS": str(cfg["warmup_steps"]),
            },
        ),
    }
    for variant in variants:
        template, dests, replacements = destinations[variant]
        content = render_template(template, replacements)
        for dest in dests:
            write_file(dest, content, create_parent=(variant == "raw-verilator"))
    if "raw-verilator" in variants:
        raw_root = root / "dpi_cpp" / f"UT_{cfg['top_name']}raw"
        raw_files = {
            raw_root / "Makefile": render_template(
                TEMPLATE_DIR / "multilang_raw_verilator.Makefile.tpl",
                {"TOP_NAME": cfg["top_name"]},
            ),
            raw_root / "CMakeLists.txt": render_template(
                TEMPLATE_DIR / "multilang_raw_verilator.CMakeLists.txt.tpl",
                {"TOP_NAME": cfg["top_name"]},
            ),
        }
        for path, content in raw_files.items():
            write_file(path, content, create_parent=True)
    dut_go = root / "dpi_golang" / "golang" / "dut.go"
    if "golang" in variants and dut_go.exists():
        text = dut_go.read_text(encoding="utf-8")
        patched = text.replace("self.Dut.atClone()", "self.Dut.AtClone()")
        if patched != text:
            dut_go.write_text(patched, encoding="utf-8")
            print(f"patched {dut_go}")
    golang_xspcomm = root / "dpi_golang" / cfg["module_name"] / "golang" / "src" / "xspcomm"
    system_xspcomm = Path("/usr/local/share/picker/golang/src/xspcomm")
    if "golang" in variants and golang_xspcomm.parent.exists() and system_xspcomm.exists():
        if golang_xspcomm.exists():
            shutil.rmtree(golang_xspcomm)
        shutil.copytree(system_xspcomm, golang_xspcomm)
        print(f"synced {golang_xspcomm}")
    java_main = cfg["java_main"]
    for mk in [root / "dpi_java" / "java" / "Makefile", root / "dpi_java" / cfg["module_name"] / "Makefile"]:
        if "java" in variants and mk.exists():
            text = mk.read_text(encoding="utf-8")
            patched = re.sub(r"com\.ut(?:\.[A-Za-z_][A-Za-z0-9_]*)?\.example", java_main, text)
            if patched != text:
                mk.write_text(patched, encoding="utf-8")
                print(f"patched {mk}")

    makefiles_by_variant = {
        "python": [
            root / "dpi_python" / "python" / "Makefile",
            root / "dpi_python" / cfg["module_name"] / "Makefile",
        ],
        "cpp": [
            root / "dpi_cpp" / "cpp" / "Makefile",
            root / "dpi_cpp" / cfg["module_name"] / "Makefile",
        ],
        "java": [
            root / "dpi_java" / "java" / "Makefile",
            root / "dpi_java" / cfg["module_name"] / "Makefile",
        ],
        "golang": [
            root / "dpi_golang" / "golang" / "Makefile",
            root / "dpi_golang" / cfg["module_name"] / "Makefile",
        ],
    }
    for variant in variants:
        for mk in makefiles_by_variant.get(variant, []):
            patch_build_makefile_no_test(mk)


def main():
    parser = argparse.ArgumentParser(description="Install stable benchmark sources into generated directories.")
    parser.add_argument("--mode", choices=["picker", "multilang"], required=True)
    parser.add_argument("--dut", choices=["XS", "rocket", "coupledL2"], required=True)
    parser.add_argument("--root", required=True, help="Experiment directory root where generated outputs exist")
    parser.add_argument("--variant", action="append", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.mode == "picker":
        install_picker(root, args.dut, args.variant)
    else:
        install_multilang(root, args.dut, args.variant)


if __name__ == "__main__":
    main()
