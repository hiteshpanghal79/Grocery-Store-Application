from .database import db


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)

    username = db.Column(db.String, nullable = False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

class Category(db.Model):
    __tablename__ = "category"
    category_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    category_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

class Products(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    product_name = db.Column(db.String, nullable=False)
    unit = db.Column(db.String, nullable=False)
    rate_per_unit = db.Column(db.Integer, nullable=False)
    mfg_date = db.Column(db.String, nullable=False)
    exp_date = db.Column(db.String, nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"), nullable=False)

class Orders(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.String, nullable = False)
    order_date = db.Column(db.String, nullable = False)