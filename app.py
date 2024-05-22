from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy import distinct
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'dinuchakedi'  # Change this!   
app.config['SECRET_KEY'] = "dinuchakedi"

# sqlite config
# app.config['SQLALCHEMY_DATABASE_URI'] = 'localhost:5432'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Bind the instance to the 'app.py' Flask application
db = SQLAlchemy(app)

class area(db.Model):
    __tablename__ = 'area' 
    area_id = db.Column(db.Integer, primary_key = True)
    area_name = db.Column(db.String(250))

    def __repr__(self):
    
        return '\n area_id: {0} area_name: {1}'.format(self.area_id, self.area_name)


    def __str__(self):

        return '\n area_id: {0} area_name: {1}'.format(self.area_id, self.area_name)

class position(db.Model):
    __tablename__ = 'position' 
    position_id = db.Column(db.Integer, primary_key = True)
    position_name = db.Column(db.String(250))

    def __repr__(self):
    
        return '\n position_id: {0} position_name:{1}'.format(self.position_id, self.position_name)


    def __str__(self):

        return '\n position_id: {0} position_name: {1}'.format(self.position_id, self.position_name)

class areaposition(db.Model):
    __tablename__ = 'area_position'
    area_position_id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.area_id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.position_id'), nullable=False)

    # Define relationships
    area = db.relationship('area', backref='area_positions')
    position = db.relationship('position', backref='area_positions')

    def __repr__(self):
        return f'areaposition(area_id={self.area_id}, position_id={self.position_id})'

    def __str__(self):
        return f'areaposition(area_id={self.area_id}, position_id={self.position_id})'

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = Users(username=request.form['username'],
                    email=request.form['email'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and user.verify_password(request.form['password']):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

from flask import render_template

@app.route("/area")
@login_required
def show_area():
    areas_data = area.query.order_by(area.area_id).all()  # Corrected to use the 'area' model
    return render_template('area.html', areas_data=areas_data)

@app.route("/position")
@login_required
def show_position():
    positions_data = position.query.order_by(position.position_id).all()  # Query all positions from the database
    return render_template('position.html', positions_data=positions_data)

@app.route("/index")
def index():
    return render_template('index.html')

# area_position areas to display
@app.route('/area_position', methods=['GET'])
def area_position():
    # Fetch distinct areas from the area_position table
    distinct_areas = db.session.query(area.area_id, area.area_name).distinct().all()

    # Render the template with distinct areas
    return render_template('area_position.html', distinct_areas=distinct_areas)


# area_position dropdown
@app.route('/get_positions', methods=['GET'])
def get_positions():
    area_id = request.args.get('area_id')
    if area_id:
        try:
            area_id = int(area_id)  # Convert area_id to integer
        except ValueError:
            return jsonify({'error': 'Invalid area_id provided'})

        # Fetch positions linked to the selected area
        area_positions = areaposition.query.filter_by(area_id=area_id).all()
        # Extract position details from area_positions
        positions = [{'position_id': ap.position_id, 'position_name': ap.position.position_name} for ap in area_positions]
        return jsonify({'positions': positions})
    else:
        return jsonify({'positions': []})  # Return an empty list if no area ID is provided


# admin_area_manage
@app.route('/admin/manage_areas', methods=['GET', 'POST'])
@login_required
def manage_areas():
    if not current_user.is_admin:
        return 'Access Denied', 403

    if request.method == 'POST':
        if 'add_area' in request.form:
            area_name = request.form['area_name']
            new_area = area(area_name=area_name)
            db.session.add(new_area)
            db.session.commit()
            flash('Area added successfully!')
        elif 'delete_area' in request.form:
            area_id = request.form['area_id']
            area_to_delete = area.query.get(area_id)
            db.session.delete(area_to_delete)
            db.session.commit()
            flash('Area deleted successfully!')
        elif 'edit_area' in request.form:
            area_id = request.form['area_id']
            edited_area_name = request.form['edited_area_name']
            area_to_edit = area.query.get(area_id)
            area_to_edit.area_name = edited_area_name
            db.session.commit()
            flash('Area updated successfully!')

    areas = area.query.order_by(area.area_id).all()
    return render_template('manage_areas.html', areas=areas)


# admin_position_manage
@app.route('/admin/manage_positions', methods=['GET', 'POST'])
@login_required
def manage_positions():
    if not current_user.is_admin:
        return 'Access Denied', 403

    if request.method == 'POST':
        if 'add_position' in request.form:
            position_name = request.form['position_name']
            new_position = position(position_name=position_name)
            db.session.add(new_position)
            db.session.commit()
            flash('Position added successfully!')

        elif 'delete_position' in request.form:
            position_id = request.form['position_id']
            position_to_delete = position.query.get(position_id)
            db.session.delete(position_to_delete)
            db.session.commit()
            flash('Position deleted successfully!')

        elif 'edit_position' in request.form:
            position_id = request.form['position_id']
            edited_position_name = request.form['edited_position_name']
            position_to_edit = position.query.get(position_id)
            position_to_edit.position_name = edited_position_name
            db.session.commit()
            flash('Position updated successfully!')

    positions = position.query.order_by(position.position_id).all() 
    return render_template('manage_positions.html', positions=positions)


from sqlalchemy.exc import IntegrityError

@app.route('/admin/manage_area_position', methods=['GET', 'POST'])
@login_required
def manage_area_position():
    if not current_user.is_admin:
        return 'Access Denied', 403
    
    if request.method == 'POST':
        area_id = request.form['area_id']
        position_id = request.form['position_id']
        
        # Check if the area_position combination already exists
        existing_entry = areaposition.query.filter_by(area_id=area_id, position_id=position_id).first()
        if existing_entry:
            flash('Position is already assigned to this area!')
        else:
            area_position = areaposition(area_id=area_id, position_id=position_id)
            db.session.add(area_position)
            try:
                db.session.commit()
                flash('Position assigned to area successfully!')
            except IntegrityError:
                db.session.rollback()
                flash('Error assigning position to area. Please try again.', 'error')

        return redirect(url_for('manage_area_position'))

    areas = area.query.all()
    positions = position.query.all()
    return render_template('manage_area_position.html', areas=areas, positions=positions)

if __name__ == '__main__':
    app.run(debug=True, port=5001)