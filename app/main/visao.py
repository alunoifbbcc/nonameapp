from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement

class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select

@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (
         element.name,
         compiler.process(element.select, literal_binds=True)
         )

# create view
from app.models import Topic
from datetime import datetime, deltatime
from app import db
engine = db.engine
createview = CreateView('active_topics', Topic.query.filter_by(last_modified > )(datetime.utcnow() - deltatime(days=30)))
engine.execute(createview)

# reflect view and print result
v = Table('viewname', metadata, autoload=True)

for r in engine.execute(v.select()):
    print r
