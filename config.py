import ConfigParser
import os

def create_config(path):
    """
    Create a config file
    """
    config = ConfigParser.ConfigParser()
    config.add_section("IRC")
    config.set("IRC", "host", "irc.freenode.net")
    config.set("IRC", "port", "6697")
    config.set("IRC", "nickname", "markov" )
    config.set("IRC", "channel", "#lobby")

    config.add_section("markov")
    config.set("markov", "chattiness", 0.1)
    config.set("markov", "chain_length", 2)
    config.set("markov", "seed", "off")

    config.add_section("permissions")
    config.set("permissions", "auth_users", "")
    config.set("permissions", "ignored_users", "")

    with open(path, "wb") as config_file:
        config.write(config_file)


def get_config(path):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        create_config(path)

    config = ConfigParser.ConfigParser()
    config.read(path)
    return config


def get_setting(path, section, setting):
    """
    Print out a setting
    """
    config = get_config(path)
    value = config.get(section, setting)
    print "{section} {setting} is {value}".format(
        section=section, setting=setting, value=value)
    return value


def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "wb") as config_file:
        config.write(config_file)


def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "wb") as config_file:
        config.write(config_file)


class blah:
    def __init__(self):
        config = get_config(os.getcwd() + "/settings.ini")

        self.__dict__.update([i for s in config.sections() for i in config.items(s)])
        print self.__dict__
        print self.host

#----------------------------------------------------------------------
if __name__ == "__main__":
    blah = blah()
