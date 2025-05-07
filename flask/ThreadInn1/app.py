from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

import requests  # Make sure this import is at the top

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()

    required = ['name', 'desc', 'price', 'image']
    if not data or not all(key in data for key in required):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        new_product = Products(
            name=data['name'],
            desc=data['desc'],
            price=int(data['price']),
            image=data['image']
        )
        db.session.add(new_product)
        db.session.commit()

        #Django
        try:
            django_response = requests.post(
                "http://localhost:8000/api/add-product/",  # Change to your Django URL in production
                json={
                    "name": data['name'],
                    "desc": data['desc'],
                    "price": data['price'],
                    "image": f"/static/images/{data['image']}",  # If image is served statically
                    "category": data.get('category', 'men')  # Default category fallback
                },
                timeout=5
            )
            print("Django sync status:", django_response.status_code)
        except Exception as sync_error:
            print("Error syncing with Django:", str(sync_error))

        return jsonify(new_product.to_dict()), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Old Products Model (Commented out for reference)
# class Products(db.Model):
#     __tablename__ = "Products"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     desc = db.Column(db.String(200), nullable=False)
#     price = db.Column(db.Integer, nullable=False)
#     image = db.Column(db.String(200), nullable=False)

#     def __init__(self, name, desc, price, image):
#         self.name = name
#         self.desc = desc
#         self.price = price
#         self.image = image

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "desc": self.desc,
#             "price": self.price,
#             "image": self.image
#         }

# New Products Model with category field
class Products(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)

    def __init__(self, name, desc, price, image):
        self.name = name
        self.desc = desc
        self.price = price
        self.image = image

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "price": self.price,
            "image": f"/static/images/{self.image}"
        }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                # Return JSON if it's an API request
                if request.path.startswith('/api/'):
                    return jsonify({"error": "Unauthorized"}), 403
                flash("Unauthorized access!", "danger")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return decorated_view
    return decorator



@app.route('/')
def home():
    users_list = User.query.all()
    return render_template('index.html', user=current_user)


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return render_template("admin_dashboard.html", user=current_user)
    return render_template("user_dashboard.html", user=current_user)

@app.route('/men')
def men():
    products = Products.query.all()
    return render_template('men.html', products=products, total_price=total_price)

def total_price():
    cart = session.get('cart', [])
    return sum(item['price'] * item['quantity'] for item in cart)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Products.query.get_or_404(product_id)
    if 'cart' not in session:
        session['cart'] = []
    cart = session['cart']
    for item in cart:
        if item['id'] == product.id:
            item['quantity'] += 1
            break
    else:
        cart.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'quantity': 1
        })
    session.modified = True
    return redirect(url_for('men'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
    return redirect(url_for('men'))

@app.route('/purchase')
def purchase():
    return render_template('purchase.html')

@app.route("/role", methods=["GET", "POST"])
def role():
    if request.method == "POST":
        role = request.form.get("role")
        if role and current_user.email.endswith('@threadinn.com'):
            current_user.role = role
            db.session.commit()
            flash(f"Role updated to {role}!", "success")
            return redirect(url_for('home'))
        flash("Error in updating role. Please try again.", "danger")
    return render_template('role.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("register.html")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash("Login successful!", "success")
            if "@threadinn.com" in email:
                return redirect(url_for('role'))
            else:
                return redirect(url_for("home"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("register.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, role="user")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        if "@threadinn.com" in email:
            return redirect(url_for("role"))
        else:
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    session.pop('_flashes', None)
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("register"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/admin")
@role_required("admin")
def admin():
    return render_template("admin.html", user=current_user)




# @app.route("/admin/products/add", methods=["GET", "POST"])
# @role_required("admin")
# def add_product():
#     if request.method == "POST":
#         data = request.form
#         product = Products(
#             name=data['name'], 
#             desc=data['desc'], 
#             price=data['price'], 
#             image=data['image']
#         )
#         db.session.add(product)
#         db.session.commit()
#         flash("Product added successfully!", "success")
#         print("Product created:", product)

#         return redirect(url_for("admin_products"))
#     return render_template("add_product.html")

# @app.route("/admin/products/edit/<int:id>", methods=["GET", "POST"])
# @role_required("admin")
# def update_product(id):
#     product = Products.query.get_or_404(id)
#     if request.method == "POST":
#         data = request.form
#         product.name = data['name']
#         product.desc = data['desc']
#         product.price = data['price']
#         product.image = data['image']
#         db.session.commit()
#         flash("Product updated successfully!", "success")
#         return redirect(url_for("admin_products"))
#     return render_template("update_product.html", product=product)



@app.route('/admin/products')
# @role_required('admin')
def admin_products():
    products = Products.query.all()  # Fetch all products from the database
    return render_template("admin_products.html", products=products)

@app.route('/admin/products/<int:product_id>', methods=['GET'])
@role_required('admin')
def view_product(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('view_product.html', product=product)





# ------------- Product API ---------------------






@app.route('/api/products/', methods=['GET'])
def get_all_products():
    category = request.args.get('category')
    if category:
        products = Products.query.filter_by(category=category).all()
    else:
        products = Products.query.all()
    return jsonify([product.to_dict() for product in products])


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_single_product(product_id):
    product = Products.query.get_or_404(product_id) 
    return jsonify(product.to_dict())


# @app.route('/api/products', methods=['POST'])
# def add_product():
#     data = request.get_json()

#     required = ['name', 'desc', 'price', 'image']
#     if not data or not all(key in data for key in required):
#         return jsonify({'error': 'Missing required fields'}), 400

#     try:
#         new_product = Products(
#             name=data['name'],
#             desc=data['desc'],
#             price=int(data['price']),
#             image=data['image']
#         )
#         db.session.add(new_product)
#         db.session.commit()
#         return jsonify(new_product.to_dict()), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Products.query.get_or_404(product_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'name' in data:
        product.name = data['name']
    if 'desc' in data:
        product.desc = data['desc']
    if 'price' in data:
        try:
            product.price = int(data['price'])
        except ValueError:
            return jsonify({'error': 'Price must be an integer'}), 400
    if 'image' in data:
        product.image = data['image']

    db.session.commit()
    return jsonify(product.to_dict())


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Products.query.first():
            sample_products = [
                Products("Men's T-Shirt", "Comfortable cotton t-shirt", 29.99, "tshirt1.jpg"),
                Products("Men's Jeans", "Classic blue jeans", 49.99, "jeans1.jpg"),
                Products("Men's Jacket", "Stylish leather jacket", 89.99, "jacket1.jpg"),
                Products("Women's Dress", "Elegant summer dress", 59.99, "dress1.jpg"),
                Products("Kids' Shoes", "Comfortable sneakers", 39.99, "shoes1.jpg")
            ]
            db.session.add_all(sample_products)
            db.session.commit()
    app.run(debug=True, port=7000)