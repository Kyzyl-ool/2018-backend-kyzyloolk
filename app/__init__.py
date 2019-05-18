import boto3
import config
from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_cors import CORS
from cent import Client
from .flask_celery import make_celery
from flask_mail import Mail


app = Flask(__name__)

app.config.update(
    broker_url=config.REDIS_URL,
    result_backend=config.REDIS_URL
)

celery = make_celery(app)



app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['ADMINS'] = config.ADMINS

mail = Mail(app)

CORS(app, supports_credentials=True)
jsonrpc = JSONRPC(app, config.API_URI)
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


boto3_session = boto3.session.Session()
s3_client = boto3_session.client(
	service_name='s3',
	endpoint_url='http://hb.bizmrg.com',
	aws_access_key_id=config.AWS_ACCESS_KEY_ID,
	aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)


# initialize client instance.
cent_client = Client(config.CENTRIFUGO_URL, api_key=config.CENTRIFUGO_API_KEY, timeout=1)

# app.conf.task_routes = {'feed.tasks.import_feed': {'queue':'feeds'}}
# app.conf.task_routes = {'feed.tasks.*': {'queue': 'feeds'}}
# app.conf.task_routes = ([
#     ('feed.tasks.*', {'queue': 'feeds'}),
#     ('web.tasks.*', {'queue': 'web'}),
#     (re.compile(r'(video|image)\.tasks\..*'), {'queue': 'media'}),
# ],)



from .views import *