# shut up useless SA warning:
import warnings; 
warnings.filterwarnings('ignore', 'Unicode type received non-unicode bind param value.')
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', category=SAWarning)

import pkg_resources

__version__ = pkg_resources.require("grano")[0].version
