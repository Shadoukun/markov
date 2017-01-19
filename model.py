import markovify
import database
import exceptions
import threading
import logging
import ConfigParser
import random

MAX_OVERLAP_RATIO = 0.2
MAX_OVERLAP_TOTAL = 10
DEFAULT_TRIES = 500


class Model(object):

    def __init__(self, config):
        self.log = logging.getLogger(__name__)

        self.config = config
        self.r = database.db_connection()
        self.dbLog = database.MessageLogger()

        self.get_model()

    def get_model(self, prefix=None):
        # pulls values from s-keys and generates MarkovEase model
        self.log.debug("Getting model text...")
        text = self.dbLog.get_text()

        self.log.debug("Generating model...")

        try:
            self.model = markovify.NewlineText("\n".join(text), state_size=2)
            self.log.debug("Generated model successfully.")
            self.log.debug("[MODEL ID]" + str(id(self.model)))

        except:
            raise exceptions.ModelException("Model generation failed.")

        self.log.debug("Spawning model timer...")
        thread = threading.Timer(120, self.get_model)
        thread.start()
        self.log.debug("...Thread spawned.")

    def generate_message(self, msg):
        self.log.debug("generate message")

        # Takes a seed message (if one) and generates message
        seed_enabled = self.config.get('markov', 'seed')

        if seed_enabled is "on":

            try:
                seedlist = self.word_split(msg)
                seedword = random.choice(seedlist)
                seed = seedlist[seedword+1]
                message = self.model.make_sentence_with_start(beginning=seed)
            except:
                raise exceptions.ModelException("failed seed")
                message = self.model.make_sentence()

            finally:
                return message

        else:
            message = self.model.make_sentence()
            return message
