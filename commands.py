import os


class Commands(object):

    def __init__(self):

        self.commands = {"!chattiness": self.set_chattiness,
                         "!seed": self.setSeed}

    def set_chattiness(self, msg):
        command, value = msg.split()
        oldvalue = self.config.get("markov", "chattiness")

        self.config.set("markov", "chattiness", value)
        self.chattiness = float(value)
        with open(os.getcwd() + "/settings.ini", "wb") as configfile:
            self.config.write(configfile)



        response = 'Chattiness changed from {ov} to {nv} '.format(ov=oldvalue, nv=value)
        self.msg(self.channel, response)

    def setSeed(self, msg):
        command, value = msg.split()

        if value is "on" or "off":
            self.config.set('markov', 'seed', value)
            with open(os.getcwd() + "/settings.ini", "wb") as configfile:
                self.config.write(configfile)
            self.msg(self.channel, "seed toggle")
