from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, HiddenField, DateField, FloatField
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange
from datetime import datetime
from app.models import Composition, Order, Dish, Menu, DishCategory, \
    Market, Place, Unit, Vendor, OrderState, Ingredient, WaiterAct


class FindForm(FlaskForm):
    s = StringField('Поиск', validators=[Optional()])
    submit = SubmitField('Найти')


class FindSelForm(FindForm):
    sel = SelectField('Фильтр', validators=[Optional()])
    submit = SubmitField('ок')


class FindTimeForm(FindForm):
    start = DateField('От:', format='%Y-%m-%d', validators=[Optional()])
    until = DateField('До:', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Найти')


class PlaceForm(FlaskForm):
    label = IntegerField('Номер стола', validators=[NumberRange(0)])
    capacity = IntegerField('Вместимость', validators=[NumberRange(1)])
    add = SubmitField('Сохранить')

    def validate_label(self, label):
        place = Place.query.filter_by(place_label=label.data).first()
        if place is not None:
            raise ValidationError('Этот столик уже есть')


class AddForm(FlaskForm):
    item = HiddenField('item')
    label = StringField('Ввести', validators=[DataRequired()])
    add = SubmitField('Добавить')

    def validate_label(self, label):
        if self.item.data == 'unit':
            i = Unit.query.filter_by(unit_label=label.data).first()
        if self.item.data == 'vendor':
            i = Vendor.query.filter_by(vendor_label=label.data).first()
        if self.item.data == 'category':
            i = DishCategory.query.filter_by(dish_category_label=label.data).first()
        if self.item.data == 'state':
            i = OrderState.query.filter_by(order_state_label=label.data).first()
        if i is not None:
            raise ValidationError(f'этот {self.item.data} уже существует.')


class IngrForm(FlaskForm):
    label = StringField('Ингредиент', validators=[DataRequired()])
    unit = SelectField('ЕИ', validators=[DataRequired()])
    add = SubmitField('Добавить')

    def validate_label(self, label):
        ingr = Ingredient.query.filter_by(ingr_label=label.data).first()
        if ingr is not None:
            raise ValidationError('уже существует.')


class EditIngrForm(IngrForm):
    old = HiddenField('label')

    def validate_label(self, label):
        if self.old.data != label.data:
            ingr = Ingredient.query.filter_by(ingr_label=label.data).first()
            if ingr is not None:
                raise ValidationError('уже существует.')


class DishForm(FlaskForm):
    label = StringField('Блюдо', validators=[DataRequired()])
    cat = SelectField('Категория', validators=[DataRequired()])
    add = SubmitField('Добавить')

    def validate_label(self, label):
        dish = Dish.query.filter_by(dish_label=label.data).first()
        if dish is not None:
            raise ValidationError('уже существует.')


class EditDishForm(DishForm):
    old = HiddenField('label')

    def validate_label(self, label):
        if self.old.data != label.data:
            dish = Dish.query.filter_by(dish_label=label.data).first()
            if dish is not None:
                raise ValidationError('уже существует.')


class MarketForm(FlaskForm):
    ingr = SelectField('Ингредиент', validators=[DataRequired()])
    vendor = SelectField('от поставщика', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Добавить')

    def validate_ingr(self, ingr):
        offer = Market.query.filter_by(ingr_id=ingr.data, vendor_id=self.vendor.data).first()
        if offer is not None:
            raise ValidationError('уже существует')


class EditPriceForm(FlaskForm):
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Добавить')


class WaybillForm(FlaskForm):
    ingr = SelectField('Ингредиент', validators=[DataRequired()])
    vendor = SelectField('от', validators=[DataRequired()])
    supplier = SelectField('Приемщик', validators=[DataRequired()])
    waybill_val = FloatField('Количество', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Добавить')


class WaiterActForm(FlaskForm):
    waiter = SelectField('Официант', validators=[DataRequired()])
    place = SelectField('Стол', validators=[DataRequired()])
    add = SubmitField('Добавить')

    def validate_place(self, place):
        p = WaiterAct.query.filter_by(works_at=datetime.today().date(),
                                      place_id=place.data,
                                      user_id=self.waiter.data).first()
        if p is not None:
            raise ValidationError('уже существует.')


class MenuForm(FlaskForm):
    dish = SelectField('Блюдо', validators=[DataRequired()])
    price = FloatField('цена', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Добавить')

    def validate_dish(self, dish):
        m = Menu.query.filter_by(created_at=datetime.today().date(),
                                 dish_id=dish.data).first()
        if m is not None:
            raise ValidationError('уже существует.')


class CompForm(FlaskForm):
    dish = SelectField('Блюдо', validators=[DataRequired()])
    ingr = SelectField('Ингредиент', validators=[DataRequired()])
    comp_val = FloatField('Количество', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Добавить')

    def validate_ingr(self, ingr):
        row = Composition.query.filter_by(ingr_id=ingr.data, dish_id=self.dish.data).first()
        if row is not None:
            raise ValidationError('уже существует')


class EditValForm(FlaskForm):
    val = FloatField('Количество', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Save')


class EditPosForm(FlaskForm):
    val = IntegerField('Количество', validators=[DataRequired(), NumberRange(1)])
    add = SubmitField('Save')


class OrderForm(FlaskForm):
    code = IntegerField('Код заказа', validators=[DataRequired(), NumberRange(0)])
    waiter = SelectField('Официант', validators=[DataRequired()])
    place = SelectField('Столик', validators=[DataRequired()])
    add = SubmitField('Заказать')

    def validate_code(self, code):
        order = Order.query.filter_by(order_code=code.data, ordered_at=datetime.today().date()).first()
        if order is not None:
            raise ValidationError('уже существует такой код')


class EditOrderForm(FlaskForm):
    old = HiddenField('old')
    code = IntegerField('Код заказа', validators=[DataRequired(), NumberRange(0)])
    add = SubmitField('Заказать')

    def validate_code(self, code):
        if code.data != self.old.data:
            order = Order.query.filter_by(order_code=code.data, ordered_at=datetime.today().date()).first()
            if order is not None:
                raise ValidationError('уже существует такой код')


class AddPosForm(FlaskForm):
    order = SelectField('ID заказа', validators=[DataRequired()])
    dish = SelectField('Блюдо', validators=[DataRequired()])
    val = IntegerField('Количество', validators=[DataRequired(), NumberRange(1)])
    add = SubmitField('Добавить')


class FilterForm(FlaskForm):
    unit = SelectField('Единицы', validators=[DataRequired()])
    val = FloatField('Не меньше чем', validators=[DataRequired(), NumberRange(0)])
    submit1 = SubmitField('Найти')