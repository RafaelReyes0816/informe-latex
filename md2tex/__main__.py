import sys


def main():
    if "--cli" in sys.argv:
        from md2tex.cli import main as cli_main
        cli_main()
    else:
        from md2tex.gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
