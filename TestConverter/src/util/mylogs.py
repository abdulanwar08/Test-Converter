import logging
import logging.handlers


        
def Logger():
    logging.basicConfig(level=logging.INFO,
                        format='<%(asctime)s> %(process)d %(filename)s - %(levelname)s : %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S %p',
                        filename='log_info.log',
                        filemode='w')
    return logging.getLogger('my_logger')
