from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.role_id')))


class Role(db.Model):
    """Role model"""
    role_id = db.Column(db.Integer(), db.Sequence('roles_id_seq'), primary_key=True)
    role_label = db.Column(db.String(80), unique=True)
    role_descr = db.Column(db.String(255))

    def __repr__(self):
        return f'{self.role_label}'

    def to_touple(self):
        return self.role_id, self.role_label


class Waybill(db.Model):
    """ Waybill model"""
    waybill_id = db.Column(db.Integer(), db.Sequence('wb_id_seq'), primary_key=True)
    ingr_id = db.Column(db.Integer(), db.ForeignKey('ingredient.ingr_id'), nullable=False)
    vendor_id = db.Column(db.Integer(), db.ForeignKey('vendor.vendor_id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    waybill_val = db.Column(db.Float(), nullable=False)
    recd_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Накладная {self.waybill_id}>'


class Position(db.Model):
    """ Order positions model"""
    position_id = db.Column(db.Integer(), db.Sequence('position_id_seq'), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    order_id = db.Column(db.Integer(), db.ForeignKey('order.order_id'), nullable=False)
    dish_id = db.Column(db.Integer(), db.ForeignKey('dish.dish_id'), nullable=False)
    position_val = db.Column(db.Integer(), nullable=False)


class Order(db.Model):
    """ Order model"""
    order_id = db.Column(db.Integer(), db.Sequence('order_id_seq'), primary_key=True)
    order_code = db.Column(db.Integer(), nullable=False)
    place_id = db.Column(db.Integer(), db.ForeignKey('place.place_id'), nullable=False)
    order_state_id = db.Column(db.Integer(), db.ForeignKey('order_state.order_state_id'), nullable=False, default=1)
    order_total = db.Column(db.Float(), nullable=False, default=0.0)
    ordered_at = db.Column(db.Date, index=True, default=datetime.today().date())

    positions = db.relationship(Position, backref='order', primaryjoin=order_id == Position.order_id)

    def to_touple(self):
        return self.order_id, f'Заказ #{self.order_id}-{self.order_code}'


class WaiterAct(db.Model):
    """ Waiter act model"""
    waiter_act_id = db.Column(db.Integer(), db.Sequence('wacts_id_seq'), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer(), db.ForeignKey('place.place_id'), nullable=False)
    works_at = db.Column(db.Date, index=True, default=datetime.today().date())

    def __repr__(self):
        return f'<Акт {self.waiter_act_id}>'


class User(UserMixin, db.Model):
    """ User model"""
    id = db.Column(db.Integer, db.Sequence('users_id_seq'), primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_fullname = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    roles = db.relationship(Role, secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    waybills = db.relationship(Waybill, backref='supplier', primaryjoin=id == Waybill.user_id)
    waiter_acts = db.relationship(WaiterAct, backref='waiter', primaryjoin=id == WaiterAct.user_id)
    positions = db.relationship(Position, backref='cook', primaryjoin=id == Position.user_id)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return 'admin' in str(self.roles)

    @property
    def isnt_admin(self):
        return not ('admin' in str(self.roles))

    def has_role(self, role: str):
        return role in str(self.roles) or 'admin' in str(self.roles)

    def to_touple(self):
        return self.id, self.user_fullname

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'roles': str(self.roles),
            'created_at': self.created_at
        }


# Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Store(db.Model):
    """Store model"""
    store_id = db.Column(db.Integer(), db.Sequence('store_id_seq'), primary_key=True)
    ingr_id = db.Column(db.Integer(), db.ForeignKey('ingredient.ingr_id'), nullable=False)
    store_val = db.Column(db.Float, nullable=False, default=0.0)
    counted_at = db.Column(db.Date, index=True, default=datetime.today().date())

    def __repr__(self):
        return f'<Store record {self.store_id}>'


class Composition(db.Model):
    """Composition (ingrs list) model"""
    comp_id = db.Column(db.Integer(), db.Sequence('comp_id_seq'), primary_key=True)
    ingr_id = db.Column(db.Integer(), db.ForeignKey('ingredient.ingr_id'), nullable=False)
    dish_id = db.Column(db.Integer(), db.ForeignKey('dish.dish_id'), nullable=False)
    comp_val = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'Рецепт #{self.comp_id}'


class Market(db.Model):
    """Market"""
    ingr_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingr_id'), primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.vendor_id'), primary_key=True)
    ingr_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Предложение {self.ingr_id}-{self.vendor_id}>'


class Ingredient(db.Model):
    """Ingredients model"""
    ingr_id = db.Column(db.Integer(), db.Sequence('ingr_id_seq'), primary_key=True)
    ingr_label = db.Column(db.String(120), unique=True, nullable=False)
    unit_id = db.Column(db.Integer(), db.ForeignKey('unit.unit_id'), nullable=False)

    market = db.relationship(Market, backref='ingredient', primaryjoin=ingr_id == Market.ingr_id)
    store = db.relationship(Store, backref='ingredient', primaryjoin=ingr_id == Store.ingr_id)
    waybills = db.relationship(Waybill, backref='ingredient', primaryjoin=ingr_id == Waybill.ingr_id)
    composition = db.relationship(Composition, backref='ingr', primaryjoin=ingr_id == Composition.ingr_id)

    def __repr__(self):
        return f'<Ingr {self.ingr_label}>'

    def to_touple(self):
        return (self.ingr_id, f"{self.ingr_label} ({Unit.query.get(self.unit_id)})")


class Unit(db.Model):
    """ Unit model"""
    unit_id = db.Column(db.Integer(), db.Sequence('units_id_seq'), primary_key=True)
    unit_label = db.Column(db.String(16), unique=True, nullable=False)
    ingr = db.relationship(Ingredient, backref='unit', primaryjoin=unit_id == Ingredient.unit_id)

    def __repr__(self):
        return f'{self.unit_label}'

    def to_touple(self):
        return self.unit_id, self.unit_label


class Vendor(db.Model):
    """ Vendor model"""
    vendor_id = db.Column(db.Integer, db.Sequence('vendors_id_seq'), primary_key=True)
    vendor_label = db.Column(db.String(120), unique=True, nullable=False)
    market = db.relationship(Market, backref='vendor', primaryjoin=vendor_id == Market.vendor_id)
    waybills = db.relationship(Waybill, backref='vendor', primaryjoin=vendor_id == Waybill.vendor_id)

    def __repr__(self):
        return f'<Vendor {self.vendor_label}>'

    def to_touple(self):
        return self.vendor_id, self.vendor_label


class OrderState(db.Model):
    """ Order state model"""
    order_state_id = db.Column(db.Integer(), db.Sequence('orst_id_seq'), primary_key=True)
    order_state_label = db.Column(db.String(60), unique=True)

    orders = db.relationship(Order, backref='state', primaryjoin=order_state_id == Order.order_state_id)

    def __repr__(self):
        return f'<State {self.order_state_label}>'

    def to_touple(self):
        return self.order_state_id, self.order_state_label


class Menu(db.Model):
    """ Menu model"""
    menu_id = db.Column(db.Integer(), db.Sequence('menu_id_seq'), primary_key=True)
    dish_id = db.Column(db.Integer(), db.ForeignKey('dish.dish_id'), nullable=False)
    menu_price = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.Date, index=True, default=datetime.today().date())

    def __repr__(self):
        return f'Пункт меню #{self.menu_id}: {self.dish_id} от {self.created_at}'

    def to_touple(self):
        return self.menu_id, self.dish_id


class Dish(db.Model):
    """ Dish model"""
    dish_id = db.Column(db.Integer(), db.Sequence('dish_id_seq'), primary_key=True)
    dish_label = db.Column(db.String(120), unique=True, nullable=False)
    dish_category_id = db.Column(db.Integer, db.ForeignKey('dish_category.dish_category_id'), nullable=False)

    menu = db.relationship(Menu, backref='dish', primaryjoin=dish_id == Menu.dish_id)
    composition = db.relationship(Composition, backref='dish', primaryjoin=dish_id == Composition.dish_id)
    positions = db.relationship(Position, backref='dish', primaryjoin=dish_id == Position.dish_id)

    def __repr__(self):
        return f'Блюдо {self.dish_label}'

    def to_touple(self):
        return self.dish_id, self.dish_label


class DishCategory(db.Model):
    """Category of dish model"""
    dish_category_id = db.Column(db.Integer(), db.Sequence('dishcat_id_seq'), primary_key=True)
    dish_category_label = db.Column(db.String(60), unique=True)

    dishes = db.relationship(Dish, backref='category', primaryjoin=dish_category_id == Dish.dish_category_id)

    def __repr__(self):
        return f'<Категория {self.dish_category_label}>'

    def to_touple(self):
        return self.dish_category_id, self.dish_category_label


class Place(db.Model):
    """Restaurant table model"""
    place_id = db.Column(db.Integer(), db.Sequence('place_id_seq'), primary_key=True)
    place_label = db.Column(db.Integer(), unique=True, nullable=False)
    place_capacity = db.Column(db.Integer())

    order = db.relationship(Order, backref='place', primaryjoin=place_id == Order.place_id)
    waiter = db.relationship(WaiterAct, backref='place', primaryjoin=place_id == WaiterAct.place_id)

    def __repr__(self):
        return f'<Table {self.place_id} ({self.place_capacity} seats)>'

    def to_touple(self):
        return self.place_id, f'Стол #{self.place_label}({self.place_capacity} мест)'
