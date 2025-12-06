

import sys
from lexer import Lexer
from parser import Parser, ParserError
from interpreter import Interpreter, RuntimeErrorPV

import time
import os
import shutil 

def print_logo():
    skull = r"""
         ██████████████           ██████╗ ██╗   ██╗
     ████░░░░░░░░░░░░░░████       ╚════██╗██║   ██║
   ██░░░░░░░░░░░░░░░░░░░░░░██       █████╔╝██║   ██║
  ██░░░░░░░░░░░░░░░░░░░░░░░░██      ██╔══╝ ██║   ██║
 ██░░░░░░░░░░░░░░░░░░░░░░░░░░██     ███████╗╚██████╔╝
 ██░░░░░░░░░░██████░░░░░░░░░░██     ╚══════╝ ╚═════╝ 
██░░░░░░░░░██░░░░░░██░░░░░░░░░██        PV LANG
██░░░░░░░░██░░████░░██░░░░░░░░██
██░░░░░░░░██░░████░░██░░░░░░░░██
██░░░░░░░░░██░░░░░░██░░░░░░░░██
 ██░░░░░░░░░████████░░░░░░░░██
 ██░░░░░░░░░░░░░░░░░░░░░░░░░██
  ██░░░░░░░░░░░░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░░░░░░░░██
     ████░░░░░░░░░░░░░░████
         ██████████████
    """

    BLUE = "\033[94m"
    RESET = "\033[0m"
    INDENT = " " * 20

    for _ in range(5):
        os.system("cls")          # Clear screen completely
        print(INDENT + BLUE + skull + RESET)
        time.sleep(0.25)

        os.system("cls")          # Clear again
        time.sleep(0.25)

    os.system("cls")              # FINAL CLEAR – skull disappears



def run_pv_code(source_code: str, interpreter: Interpreter = None):
    lexer = Lexer(source_code)
    tokens = lexer.generate_tokens()

    parser = Parser(tokens)
    try:
        program = parser.parse()
    except ParserError as e:
        print("Syntax Error:", e)
        return

    if interpreter is None:
        interpreter = Interpreter()

    try:
        interpreter.run(program)
    except RuntimeErrorPV as e:
        print("Runtime Error:", e)

def repl():
    print_logo()
    print("PV REPL mode. Type 'exit;' or 'quit;' to leave.")
    interp = Interpreter()
    while True:
        try:
            line = input("pv> ")
        except EOFError:
            break
        if not line.strip():
            continue
        if line.strip().lower() in ("exit", "exit;", "quit", "quit;"):
            break
        # require semicolon at end for statements like let/print
        try:
            run_pv_code(line, interpreter=interp)
        except KeyboardInterrupt:
            print()
            continue

def main():
    # Show logo only once
    first_run_flag = "pv_first_run.flag"

    if not os.path.exists(first_run_flag):
        print_logo()  # Show skull animation
        with open(first_run_flag, "w") as f:
            f.write("shown")
    else:
        pass  # Skip logo after first run

    # No file → REPL
    if len(sys.argv) == 1:
        repl()
        return

    # Run file
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not filename.endswith(".pv"):
            print("Error: file must have .pv extension")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"File not found: {filename}")
            return

        run_pv_code(source)
        return

    print("Usage:")
    print("  python main.py            # REPL mode")
    print("  python main.py file.pv    # run PV file")


if __name__ == "__main__":
    main()
