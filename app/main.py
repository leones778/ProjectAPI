from flask import Flask

from app.core.config import Config

app = Flask("consumables_app")
app.config.from_object(Config)

from app.api.auth.handlers import *  # noqa
from app.api.consumable.handlers import *  # noqa
from app.api.consumable_category.handlers import *  # noqa
