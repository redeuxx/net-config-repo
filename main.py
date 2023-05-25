import get_config
import my_secrets


def main():
    get_config.get_config(my_secrets.USERNAME, my_secrets.PASSWORD)


if __name__ == "__main__":
    main()
