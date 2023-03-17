# ------------------ IMPORTS ------------------


from render.engine import Engine


# ------------------ GLOBAL VARIABLES ------------------


NEAT_CONFIG_PATH = "ai/config.txt"
RAY_CAST = True
MAX_SIMULATIONS = 1000


# ------------------ MAIN FUNCTION ------------------


def main() -> None:
    window = Engine(NEAT_CONFIG_PATH, RAY_CAST, MAX_SIMULATIONS)
    window.run()


# ------------------ MAIN CALL ------------------


if __name__ == "__main__":
    main()
