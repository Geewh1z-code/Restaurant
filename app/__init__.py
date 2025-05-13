from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect


app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:BIOL108125@localhost:3306/app_test'
db = SQLAlchemy(app)

app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = '123454321'

bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'auth.login'

from app.home import bp as home_bp

app.register_blueprint(home_bp)

from app.auth import bp as auth_bp

app.register_blueprint(auth_bp, url_prefix='/auth')

from app.admin import bp as admin_bp

app.register_blueprint(admin_bp, url_prefix='/admin')

from app.main.places import bp as place_bp

app.register_blueprint(place_bp, url_prefix='/place')

from app.main.units import bp as unit_bp

app.register_blueprint(unit_bp, url_prefix='/units')

from app.main.vendors import bp as vendor_bp

app.register_blueprint(vendor_bp, url_prefix='/vendors')

from app.main.dish_ctg import bp as dctg_bp

app.register_blueprint(dctg_bp, url_prefix='/category')

from app.main.order_states import bp as state_bp

app.register_blueprint(state_bp, url_prefix='/states')

from app.main.ingredients import bp as ingr_bp

app.register_blueprint(ingr_bp, url_prefix='/ingredients')

from app.main.market import bp as market_bp

app.register_blueprint(market_bp, url_prefix='/market')

from app.main.waybills import bp as waybill_bp

app.register_blueprint(waybill_bp, url_prefix='/waybills')

from app.main.waiter_acts import bp as waiter_bp

app.register_blueprint(waiter_bp, url_prefix='/waiters')

from app.main.dishes import bp as dish_bp

app.register_blueprint(dish_bp, url_prefix='/dishes')

from app.main.menu import bp as menu_bp

app.register_blueprint(menu_bp, url_prefix='/menu')

from app.main.compositions import bp as comp_bp

app.register_blueprint(comp_bp, url_prefix='/compositions')

from app.main.orders import bp as order_bp

app.register_blueprint(order_bp, url_prefix='/orders')

from app.main.positions import bp as pos_bp

app.register_blueprint(pos_bp, url_prefix='/positions')

from app.main.store import bp as store_bp

app.register_blueprint(store_bp, url_prefix='/store')


def crt():
    roles = {'admin': 'admin',
             'waiter': 'waiter',
             'cook': 'cook',
             'supplier': 'supplier'}
    try:
        for r in roles.items():
            new_role = models.Role(role_label=r[0], role_descr=r[1])
            db.session.add(new_role)
        db.session.commit()
    except:
        pass

    try:
        role1 = models.Role.query.get(1)
        user1 = models.User(username='a', email='admin@example.com')
        user1.set_password('a')
        user1.roles = [role1, ]
        db.session.add(user1)

        role2 = models.Role.query.get(2)
        user2 = models.User(username='w', email='w@example.com')
        user2.set_password('w')
        user2.roles = [role2, ]
        db.session.add(user2)

        role3 = models.Role.query.get(3)
        user3 = models.User(username='c', email='c@example.com')
        user3.set_password('c')
        user3.roles = [role3, ]
        db.session.add(user3)

        role4 = models.Role.query.get(4)
        user4 = models.User(username='s', email='s@example.com')
        user4.set_password('s')
        user4.roles = [role4, ]
        db.session.add(user4)
        db.session.commit()
        print('roles and users added')
    except:
        pass


debug = True
debug = False
if debug:
    from app import models

    db.create_all()
    print('DB Created')
    crt()
else:
    from app import models
