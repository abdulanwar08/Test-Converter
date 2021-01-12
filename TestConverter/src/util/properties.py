from util.mylogs import Logger
from jproperties import Properties

#load the properties file into our Properties object
LOG = Logger()
def getconfigprop():
    try:
        LOG.info("Read config.properties file")
        config = Properties()
        with open('config.properties', 'rb') as config_file:
            config.load(config_file)
            return config
    except Exception as e:
        LOG.error("File config.properties is missing")
        LOG.error(e)