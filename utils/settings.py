from os import path
APP_ROOT = path.dirname(path.abspath(__file__))[: -6]  #ommit this directory "/utils"
APP_STORIES = path.join(APP_ROOT, "stories")
APP_STATIC = path.join(APP_ROOT, "static")
APP_JOURNALS = path.join(APP_STATIC, "journals")
APP_BACKUPS = path.join(APP_STATIC, "backups")
APP_LOGS = path.join(APP_STATIC, "logs")
APP_MONGO = path.join(APP_ROOT, "db")
APP_START_MONGO = path.join(APP_MONGO, "start_mongodb.command")
