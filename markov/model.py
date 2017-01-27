import markovify
import exceptions
import threading
import logging
import random


class Model(object):

    MAX_OVERLAP_RATIO = 0.2
    MAX_OVERLAP_TOTAL = 10
    DEFAULT_TRIES = 500

    def __init__(self, logger):
        self.log = logging.getLogger(__name__)

        self.logger = logger
        self.get_model()

    def get_model(self, prefix=None):
        self.log.debug("Getting model text...")

        # pulls values from db
        text = self.logger.get_text()

        try:
            self.log.debug("Generating model...")

            # generate model
            self.model = markovify.NewlineText("\n".join(text), state_size=2)

            self.log.debug("Generated model successfully.")
            self.log.debug("[MODEL ID]" + str(id(self.model)))

        except:
            self.log.debug("Model generation failed.")
            pass

        finally:
            # create thread to recreate model perodically.
            self.log.debug("Spawning model timer...")

            thread = threading.Timer(120, self.get_model)
            thread.start()

            self.log.debug("...Thread spawned.")

    def generate_message(self, msg, seedtoggle):
        self.log.debug("generating message")

        # Takes a seed message (if one) and generates message
        if seedtoggle is True:

            seedlist = msg.split()
            seedword = seedlist.index(random.choice(seedlist))
            seed = ' '.join(seedlist[seedword:seedword+2])
            message = self.model.make_sentence_with_start(beginning=seed)

        else:
            message = self.model.make_sentence()

        return message
