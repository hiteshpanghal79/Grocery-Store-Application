from flask import Flask, request, render_template, redirect, url_for
from flask import current_app as app
import sqlalchemy
from sqlalchemy.sql import func
from application.models import User, Category, Products, Orders
from application.database import db
from datetime import date

@app.route("/", methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('userlogin.html')
    else:
        u_name = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get('usertype')
        login_validation = User.query.filter(User.username == u_name, User.password == password, User.role == role).first()
        # redirection to admin or user dashboard on login
        if login_validation != None:
            usertype = request.form.get("usertype")
            if usertype == "admin":
                return redirect(url_for("admin_dashboard", admin_id = login_validation.user_id))
            else:
                return redirect(url_for("user_dashboard", user_id = login_validation.user_id))
        else:
            return render_template("wrong_details.html")

#for new registrations
@app.route("/new_registration", methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('create_user.html')
    else:
        usertype = request.form.get("usertype")
        fname = request.form.get("full_name")
        email = request.form.get("emailID")
        address = request.form.get("address")
        username = request.form.get("username")
        password = request.form.get("pass")
        
        registration_add_query = User(full_name = fname, email = email, role = usertype, address = address, username = username, password = password)
        db.session.add(registration_add_query)
        db.session.commit()

        return redirect("/")

@app.route("/admin/<admin_id>", methods=['GET','POST'])
def admin_dashboard(admin_id):
    category_search_query = Category.query.filter(Category.admin_id == admin_id).all()
    return render_template("admin_inventory.html", category = category_search_query, adm_id = admin_id)

#For view admin profile
@app.route("/admin/<admin_id>/profile", methods=['GET','POST'])
def admin_profile(admin_id):
    adm_data = User.query.filter(User.user_id == admin_id).first()
    return render_template("admin_profile.html", user_data = adm_data)

#To add categories for admin 
@app.route("/admin/<admin_id>/add_category", methods=['GET', 'POST'])
def add_category(admin_id):
    if request.method == 'GET':
        return render_template("add_category.html")
    else:
        category_name = request.form.get("category_name")
        category_description = request.form.get("category_description")
        
        category_add_query = Category(category_name = category_name, description = category_description, admin_id = admin_id)
        db.session.add(category_add_query)
        db.session.commit()

        return redirect(url_for("admin_dashboard", admin_id = admin_id))

#To update a category
@app.route("/admin/<adm_id>/<cat_id>/update_category", methods = ['GET', 'POST'])
def update_category(adm_id, cat_id):
    if request.method == 'GET':
        category_search = Category.query.filter(Category.category_id == cat_id).first()
        cat_name = category_search.category_name
        cat_desc = category_search.description
        return render_template('update_category.html', name = cat_name, description = cat_desc)
    else:
        category_search = Category.query.filter(Category.category_id == cat_id).first()
        new_name = request.form.get("new_name")
        new_description = request.form.get('new_description')

        category_search.category_name = new_name
        category_search.description = new_description

        db.session.commit()

        return redirect(url_for("admin_dashboard", admin_id = adm_id))

#To delete a category
@app.route("/admin/<adm_id>/<cat_id>/delete_category", methods=['GET', 'POST'])
def delete_category(adm_id, cat_id):
    category_search_query = Category.query.filter(Category.category_id == cat_id).first()
    category_product_query = Products.query.filter(Products.category_id == cat_id).all()
    orders_query = Orders.query.all()
    for p in category_product_query:
        for o in orders_query:
            if o.product_id == p.product_id:
                db.session.delete(o)
        db.session.delete(p)
    db.session.commit()

    db.session.delete(category_search_query)
    db.session.commit()

    return redirect(url_for("admin_dashboard", admin_id = adm_id))


#To view products in a category
@app.route("/admin/<admin_id>/<category_id>", methods=['GET', 'POST'])
def view_products(admin_id, category_id):
    product_search_query = Products.query.filter(Products.category_id == category_id).all()
    return render_template("show_products.html", products = product_search_query, category_id = category_id, adm_id = admin_id)

#To add products in a category
@app.route("/admin/<admin_id>/<category_id>/add_product", methods=['GET','POST'])
def add_product(admin_id, category_id):
    if request.method == 'GET':
        return render_template("add_product.html")
    else:
        p_name = request.form.get("p_name")
        p_price = request.form.get("p_price")
        p_unit = request.form.get("p_unit")
        p_mfg = request.form.get("p_mfg")
        p_exp = request.form.get("p_exp")
        p_quantity = request.form.get("p_quantity")
        image = request.files['image']

        product_add_query = Products(product_name = p_name, unit = p_unit, rate_per_unit = p_price, mfg_date = p_mfg, exp_date = p_exp, total_quantity = p_quantity, category_id = category_id)
        db.session.add(product_add_query)
        db.session.commit()

        lastAdded = Products.query.order_by(Products.product_id.desc()).first()
        id = str(lastAdded.product_id)
        image.filename=id+".jpeg"
        image.save("static/" + image.filename)

        return redirect(url_for("admin_dashboard", admin_id = admin_id))
    
#To update a product
@app.route("/admin/<adm_id>/<pro_id>/update", methods=['GET', 'POST'])
def update_product(adm_id, pro_id):
    if request.method == 'GET':
        product_search_query = Products.query.filter(Products.product_id == pro_id).first()
        return render_template("update_product.html", pro_id = product_search_query.product_id, pro_name = product_search_query.product_name, pro_mfg = product_search_query.mfg_date, pro_exp = product_search_query.exp_date, pro_quantity = product_search_query.total_quantity, pro_rate = product_search_query.rate_per_unit)
    else:
        p_name = request.form.get("p_name")
        p_unit = request.form.get("p_unit")
        p_rate = request.form.get("p_rate")
        p_mfg = request.form.get("p_mfg")
        p_exp = request.form.get("p_exp")
        p_quantity = request.form.get("p_quantity")
        image=request.files['image']

        product_search_query = Products.query.filter(Products.product_id == pro_id).first()

        product_search_query.product_name = p_name.lower()
        product_search_query.rate_per_unit = p_rate
        product_search_query.unit = p_unit
        product_search_query.mfg_date = p_mfg
        product_search_query.exp_date = p_exp
        product_search_query.total_quantity = p_quantity

        db.session.commit()
        if(image.filename != ""):
            image.filename=str(pro_id)+".jpeg"
            image.save('static/'+image.filename)
        return redirect(url_for('view_products', admin_id = adm_id, category_id = product_search_query.category_id))

#To delete a product
@app.route("/admin/<adm_id>/<pro_id>/delete_product", methods=['GET', 'POST'])
def delete_product(adm_id, pro_id):
    if request.method == 'GET':
        product_search_from_orders = Orders.query.filter(Orders.product_id == pro_id).all()
        if product_search_from_orders:
            for p in product_search_from_orders:
                db.session.delete(p)
            db.session.commit()

        product_search_query = Products.query.filter(Products.product_id == pro_id).first()
        db.session.delete(product_search_query)
        db.session.commit()

        return redirect(url_for("view_products", admin_id = adm_id, category_id = product_search_query.category_id))

#After login by the user
@app.route("/user/<user_id>", methods=['GET', 'POST'])
def user_dashboard(user_id):
    product_search = Products.query.order_by(Products.product_id.desc()).limit(5)
    return render_template("user_dashboard.html", products = product_search, user_id = user_id)

#For the user cart
@app.route("/user/<user_id>/cart", methods=['GET', 'POST'])
def user_cart(user_id):
    order_search = Orders.query.filter(Orders.user_id == user_id, Orders.is_active == True).all()
    total  = 0
    product_details = {}
    for order in order_search:
        product = Products.query.filter(Products.product_id == order.product_id).first()
        product_details[order.product_id] = product
        total += order.total_price
    
    prev = Orders.query.filter(Orders.user_id == user_id, Orders.is_active == False).all()
    prev_orders = {}
    for order in prev:
        product = Products.query.filter(Products.product_id == order.product_id).first()
        prev_orders[order.product_id] = product

    return render_template("user_cart.html", u_id = user_id, orders = order_search, product_details = product_details, total_price = total, prev_orders = prev, prev_orders_details = prev_orders)

#To view user Profile
@app.route("/user/<user_id>/profile", methods=['GET'])
def user_profile(user_id):
    user_data = User.query.filter(User.user_id == user_id).first()
    return render_template("user_profile.html", user_data = user_data)

#For searching a product
@app.route("/user/<user_id>/search", methods=['GET', 'POST'])
def search_product(user_id):
    search_for = request.form.get("search")
    product_search_query = Products.query.filter(Products.product_name.like("%"+search_for+"%")).all()
    p = product_search_query

    if not p:
        c = Category.query.filter(Category.description.like("%"+search_for+"%")).first()
        if c:
            product_search_query = Products.query.filter(Products.category_id == c.category_id).all()
            for pro in product_search_query:
                if pro not in p:
                        p.append(pro)
    return render_template('search_results.html', u_id = user_id, product = search_for, result = p)

# To Buy a product
@app.route("/user/<user_id>/<product_id>/buy", methods=['GET','POST'])
def buy_product(user_id, product_id):
    if request.method == 'GET':
        product_data = Products.query.filter(Products.product_id == product_id).first()
        return render_template('buy_product.html', name=product_data.product_name, quantity = product_data.total_quantity, user_id = user_id)
    else:
        quantity = request.form.get('quantity_ordered')
        product_data = Products.query.filter(Products.product_id == product_id).first()

        order_add_query = Orders(user_id = user_id, product_id = product_id, quantity_ordered = int(quantity), total_price = (int(quantity)*product_data.rate_per_unit), is_active = False, order_date=date.today())
        db.session.add(order_add_query)
        db.session.commit()

        product_data.total_quantity = product_data.total_quantity - int(quantity)
        db.session.commit()
        
        return  render_template("order_success.html", user_id = user_id)
        

# #To Add a product to cart
@app.route("/user/<user_id>/<product_id>/add_to_cart", methods = ['GET', 'POST'])
def add_to_cart(user_id, product_id):
    if request.method == 'GET': 
        product_data = Products.query.filter(Products.product_id == product_id).first()
        return render_template("order.html", name = product_data.product_name, quantity = product_data.total_quantity, user_id = user_id)
    else:
        quantity = request.form.get("quantity_ordered")
        exist_cart = Orders.query.filter(Orders.product_id==product_id, Orders.is_active == 1).first()
        product_data = Products.query.filter(Products.product_id == product_id).first()
        if not exist_cart:

            order_add_query = Orders(user_id = user_id, product_id = product_id, quantity_ordered = int(quantity), total_price = (int(quantity)*product_data.rate_per_unit), is_active = True, order_date=date.today())
            db.session.add(order_add_query)

            product_data.total_quantity = product_data.total_quantity - int(quantity)
            db.session.commit()
            
            return redirect(url_for("user_cart", user_id = user_id))
        else:
            exist_cart.quantity_ordered= exist_cart.quantity_ordered + int(quantity)
            product_data.total_quantity = product_data.total_quantity - int(quantity)
            db.session.commit()

            return redirect(url_for("user_cart", user_id = user_id))

#To place order from cart
@app.route("/user/<user_id>/place_order", methods=['GET'])
def placeOrder(user_id):
    order_search = Orders.query.filter(Orders.user_id == user_id, Orders.is_active == 1).all()
    for o in order_search:
        o.is_active = 0
    db.session.commit()
    
    return render_template("order_success.html", user_id = user_id)

#To delete from cart
@app.route("/user/<user_id>/<order_id>/deleteFromCart", methods=['GET', 'POST'])
def deleteFromCart(user_id, order_id):
    order_search = Orders.query.filter(Orders.order_id == order_id).first()
    q = order_search.quantity_ordered
    p_id = order_search.product_id
    pro = Products.query.filter(Products.product_id == p_id).first()
    pro.total_quantity += q
    db.session.delete(order_search)
    db.session.commit()

    return redirect(url_for("user_cart", user_id = user_id))