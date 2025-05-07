from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Vehicle Model
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    price_per_day = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)

# Reservation Model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    customer_name = db.Column(db.String(100))

# Homee route
@app.route('/')
def home():
    return render_template('index.html')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        admin_key = request.form.get('admin_key')
        is_admin = admin_key == '3724'

        new_user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login - Allows both users & admins to log in"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')

            if user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))

        flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')


# Dashboard route for users
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    vehicles = Vehicle.query.filter_by(available=True).all()
    return render_template('dashboard.html', vehicles=vehicles)


# Reservation route
@app.route('/reserve/<int:vehicle_id>', methods=['GET', 'POST'])
def reserve(vehicle_id):
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle or not vehicle.available:
        flash('Vehicle not available for reservation.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        num_days = (end_date_obj - start_date_obj).days
        total_cost = num_days * vehicle.price_per_day

        new_reservation = Reservation(
            user_id=session['user_id'],
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost
        )
        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Vehicle reserved successfully! Total Cost: ${total_cost}', 'success')
        
        return redirect(url_for('payment', reservation_id=new_reservation.id))

    return render_template('reserve.html', vehicle=vehicle)


# My reservations route
@app.route('/my_reservations')
def my_reservations():
    """Shows all reservations for the logged-in user."""
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_reservations.html', reservations=reservations)


# Cancel reservation route
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    """Allows users to cancel their reservation."""
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    reservation = Reservation.query.get(reservation_id)
    if reservation and reservation.user_id == session['user_id']:
        vehicle = Vehicle.query.get(reservation.vehicle_id)
        if vehicle:
            vehicle.available = True  # Mark the vehicle as available again
        db.session.delete(reservation)
        db.session.commit()
        flash('Reservation canceled successfully!', 'success')

    return redirect(url_for('my_reservations'))


# Modify reservation route
@app.route('/modify_reservation/<int:reservation_id>', methods=['GET', 'POST'])
def modify_reservation(reservation_id):
    """Allows users to modify reservation dates."""
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    reservation = Reservation.query.get(reservation_id)
    if not reservation or reservation.user_id != session['user_id']:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('my_reservations'))

    if request.method == 'POST':
        new_start_date = request.form['start_date']
        new_end_date = request.form['end_date']
        
        # Convert dates and recalculate cost
        start_date_obj = datetime.strptime(new_start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(new_end_date, '%Y-%m-%d')
        num_days = (end_date_obj - start_date_obj).days
        vehicle = Vehicle.query.get(reservation.vehicle_id)
        total_cost = num_days * vehicle.price_per_day

        # Update reservation details
        reservation.start_date = new_start_date
        reservation.end_date = new_end_date
        reservation.total_cost = total_cost
        db.session.commit()

        flash('Reservation updated successfully!', 'success')
        return redirect(url_for('my_reservations'))

    return render_template('modify_reservation.html', reservation=reservation)


# Payment route
@app.route('/payment/<int:reservation_id>', methods=['GET', 'POST'])
def payment(reservation_id):
    """Redirects to a payment page after confirming a reservation."""
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    reservation = Reservation.query.get(reservation_id)
    
    if not reservation or reservation.user_id != session['user_id']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    # Fetch the vehicle's price and calculate total cost
    vehicle = Vehicle.query.get(reservation.vehicle_id)
    start_date_obj = datetime.strptime(reservation.start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(reservation.end_date, '%Y-%m-%d')
    num_days = (end_date_obj - start_date_obj).days
    total_cost = num_days * vehicle.price_per_day

    if request.method == 'POST':
        # Simulate payment processing
        card_number = request.form['card_number']
        expiration_date = request.form['expiration_date']
        ccv = request.form['ccv']
        card_name = request.form['card_name']

        if not (card_number and expiration_date and ccv and card_name):
            flash('Please fill in all payment details.', 'danger')
            return redirect(url_for('payment', reservation_id=reservation_id))

        # Mark reservation as paid
        customer_name = request.form['customer_name']
        reservation.customer_name = customer_name
        reservation.paid = True
        db.session.commit()

        flash('Payment successful! Your reservation is confirmed.', 'success')
        return redirect(url_for('my_reservations'))

    return render_template('payment.html', reservation=reservation, total_cost=total_cost)


# Admin route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    vehicles = Vehicle.query.all()
    reservations = db.session.query(Reservation, Vehicle).join(Vehicle, Reservation.vehicle_id == Vehicle.id).all()
    
    return render_template('admin.html', vehicles=vehicles, reservations=reservations)


# Admin modify reservation route
@app.route('/admin/modify_reservation/<int:reservation_id>', methods=['GET', 'POST'])
def admin_modify_reservation(reservation_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    reservation = Reservation.query.get_or_404(reservation_id)

    if request.method == 'POST':
        reservation.start_date = request.form['start_date']
        reservation.end_date = request.form['end_date']
        reservation.customer_name = request.form['customer_name']

        # Recalculate cost
        start_date_obj = datetime.strptime(reservation.start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(reservation.end_date, '%Y-%m-%d')
        days = (end_date_obj - start_date_obj).days
        vehicle = Vehicle.query.get(reservation.vehicle_id)
        reservation.total_cost = days * vehicle.price_per_day

        db.session.commit()
        flash('Reservation updated successfully!', 'success')
        return redirect(url_for('admin'))

    return render_template('modify_reservation.html', reservation=reservation)



# Add vehicle route
@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('admin'))

    vehicle_type = request.form['vehicle_type']
    price_per_day = int(request.form['price_per_day'])
    new_vehicle = Vehicle(type=vehicle_type, price_per_day=price_per_day, available=True)
    db.session.add(new_vehicle)
    db.session.commit()
    flash(f'Vehicle "{vehicle_type}" added successfully!', 'success')
    return redirect(url_for('admin'))


# Delete vehicle route
@app.route('/delete_vehicle/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('admin'))

    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        db.session.delete(vehicle)
        db.session.commit()
        flash('Vehicle removed successfully!', 'success')
    return redirect(url_for('admin'))


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# Run flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)