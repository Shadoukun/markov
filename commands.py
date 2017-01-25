class Commands(object):

    def __init__(self):

        self.commands = {"!chattiness": self.set_chattiness,
                         "!seed": self.setSeed}

    def set_chattiness(self, msg):
        command, value = msg.split()
        oldvalue = self.config.chattiness
        self.config.chattiness = value

        response = 'Chattiness changed from {ov} to {nv}'.format(ov=oldvalue, nv=value)
        self.msg(self.factory.channel, response)

    def setSeed(self, msg):
        command, value = msg.split()

        if value is "True" or "False":
            self.config.seed = value

            if value is "True":
                self.msg(self.factory.channel, "Seed: on")

            if value is "False":
                self.msg(self.factory.channel, "Seed: off")
