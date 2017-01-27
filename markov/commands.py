class Commands(object):

    def __init__(self):

        self.commands = {"!chattiness": self.set_chattiness,
                         "!seed": self.setSeed}

    def set_chattiness(self, msg):
        command, value = msg.split()
        ov = self.config.chattiness
        self.config.chattiness = value

        response = 'Chattiness changed from {ov} to {nv}'.format(ov=ov, nv=value)
        self.msg(self.config.channel, response)

    def setSeed(self, msg):
        command, value = msg.split()

        self.config.seed = value

        if value == "on":
            self.config.seed = "True"
            self.msg(self.config.channel, "Seed: on")

        if value == "off":
            self.config.seed = "False"
            self.msg(self.config.channel, "Seed: off")
