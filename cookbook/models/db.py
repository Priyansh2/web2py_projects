from gluon.contrib.appconfig import AppConfig

myconf = AppConfig(reload=True)

response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

db = DAL('sqlite://storage.sqlite')

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

db.define_table(auth.settings.table_user_name,
                Field('first_name', length=128, default=''),
                Field('last_name', length=128, default=''),
                Field('username', length=128, default='',unique=True),
                Field('email', length=128, default='', unique=True),
                Field('password', 'password', length=512,readable=False, label='Password'),
                Field('registration_key', length=512,writable=False, readable=False, default=''),
                Field('reset_password_key', length=512,writable=False, readable=False, default=''),
                Field('registration_id', length=512,writable=False, readable=False, default=''))

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.requires = \
IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.last_name.requires = \
IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.password.requires = [IS_STRONG(min=8,upper=1,lower=1,special=1), CRYPT()]
custom_auth_table.username.requires = [IS_NOT_EMPTY(),IS_NOT_IN_DB(db,custom_auth_table.username)]
custom_auth_table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email),IS_NOT_IN_DB(db, custom_auth_table.email)]
auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table


## create all tables needed by auth if not custom tables
auth.define_tables(username=True)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

db.define_table('image',
                Field('title',unique=True),
                Field('author'),
                Field('date','date'),
                Field('email'),
                Field('description', 'text'),
                Field('file','upload'),format='%(title)s'
               )

db.image.title.requires = IS_NOT_IN_DB(db, db.image.title)
db.image.description.requires = IS_NOT_EMPTY()
db.image.date.requires = IS_NOT_EMPTY()
db.image.author.requires = IS_NOT_EMPTY()
db.image.email.requires = IS_EMAIL() and IS_NOT_EMPTY()
db.image.email.requires = IS_IMAGE()

db.define_table('post',
                Field('recipe', 'reference image'),
                Field('visitor'),
                Field('email'),
                Field('comment', 'text'))

db.post.recipe.requires = IS_IN_DB(db, db.image.id, '%(title)s')
db.post.visitor.requires = IS_NOT_EMPTY()
db.post.email.requires = IS_EMAIL()
db.post.comment.requires = IS_NOT_EMPTY()
db.post.recipe.writable = db.post.recipe.readable = False
