from alembic.config import CommandLine


def main():
    CommandLine().main(argv=["-c", "alembic.ini", "upgrade", "head"])


if __name__ == "__main__":
    main()
