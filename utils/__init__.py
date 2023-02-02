from .StorageHandler import StorageHandler

from .SystemVariable import *

from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_msearch import Search
from flask_login import LoginManager
from flask_uploads import IMAGES, UploadSet

db= SQLAlchemy()
bcrypt= Bcrypt()
search= Search()

login_manager= LoginManager()

photos= UploadSet('photos',IMAGES)