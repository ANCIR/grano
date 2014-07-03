import pkg_resources

# namespace package
pkg_resources.declare_namespace(__name__)

# shut up useless SA warning:
import warnings;
warnings.filterwarnings('ignore', 'Unicode type received non-unicode bind param value.')
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', category=SAWarning)
