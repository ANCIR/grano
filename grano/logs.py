import logging

logging.basicConfig(level=logging.DEBUG)


# shut up useless SA warning:
import warnings
warnings.filterwarnings('ignore',
                        'Unicode type received non-unicode bind param value.')
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', category=SAWarning)

# specific loggers
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.WARNING)

stevedore_log = logging.getLogger("stevedore")
stevedore_log.setLevel(logging.WARNING)
