import logging
import logging.config
from teams_logger import Office365CardFormatter

teams_webhook_url: str = ''

config = {
    'version' : 1,
    'disable_existing_loggers' : False,
    'formatters' : {
        'simple' : {
            'format' : '%(asctime)s - %(name)s - %(levelname)s: \n\t%(messsage)s'
        },
        'teamscard' : {
            '()' : Office365CardFormatter,
            'facts' : ['asctime', 'name', 'levelname', 'lineno'],
        },
    },
    'handlers' : {
        'console' : {
            'class' : 'logging.StreamHandler',
            'level' : 'INFO',
            'formatter' : 'simple',
            'stream' : 'ext://sys.stdout',
        },
        'logfile' : {
            'class' : 'logging.FileHandler',
            'filename' : 'info.log',
            'mode' : 'a',
            'level' : 'INFO',
            'formatter' : 'simple',
        },
        'msteams' : {
            'level' : logging.INFO,
            'class' : 'teams_logger.TeamsQueueHandler',
            'url' : teams_webhook_url,
            'formatter' : 'teamscard',
        },
    },
    'loggers' : {
        __name__ : {
            'handlers' : ['msteams'],
            'level' : logging.DEBUG,
        }
    },
}

def make_logger() -> logging.Logger:
    logging.config.dictConfig(config)
    log = logging.getLogger()
    return log