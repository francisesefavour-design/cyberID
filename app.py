from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyber-tech-secret-key-2024-secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ADMIN_EMAIL = "ceo@gmail.com"
ADMIN_PASSWORD = "let.begin"

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    progress = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'progress': self.progress,
            'verified': self.verified,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def public_view():
    members = Member.query.all()
    return render_template('public.html', members=members)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome back, CEO!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    members = Member.query.all()
    return render_template('admin.html', members=members)

@app.route('/api/members', methods=['POST'])
@admin_required
def add_member():
    data = request.get_json()
    new_member = Member(
        member_id=data.get('member_id'),
        full_name=data.get('full_name'),
        phone_number=data.get('phone_number'),
        email=data.get('email'),
        progress=data.get('progress', 0),
        verified=data.get('verified', False),
        status=data.get('status', 'active')
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'success': True, 'member': new_member.to_dict()})

@app.route('/api/members/<int:member_id>', methods=['PUT'])
@admin_required
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    member.member_id = data.get('member_id', member.member_id)
    member.full_name = data.get('full_name', member.full_name)
    member.phone_number = data.get('phone_number', member.phone_number)
    member.email = data.get('email', member.email)
    member.progress = data.get('progress', member.progress)
    member.verified = data.get('verified', member.verified)
    member.status = data.get('status', member.status)
    db.session.commit()
    return jsonify({'success': True, 'member': member.to_dict()})

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
@admin_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'success': True})

def init_db():
    with app.app_context():
        db.create_all()
        if Member.query.count() == 0:
            sample_members = [
                Member(member_id='CT-001', full_name='Olokpa Divine', phone_number='+234 801 234 5678', email='divine@cyber.tech', progress=80, verified=True, status='active'),
                Member(member_id='CT-002', full_name='Big Ron', phone_number='+234 802 345 6789', email='ron@cyber.tech', progress=72, verified=True, status='active'),
                Member(member_id='CT-003', full_name='Fåbyøùñg', phone_number='+234 803 456 7890', email='fabyoung@cyber.tech', progress=38, verified=False, status='pending'),
                Member(member_id='CT-004', full_name='Ada', phone_number='+234 804 567 8901', email='ada@cyber.tech', progress=12, verified=True, status='inactive'),
                Member(member_id='CT-005', full_name='Samir', phone_number='+234 805 678 9012', email='samir@cyber.tech', progress=94, verified=True, status='active'),
            ]
            db.session.bulk_save_objects(sample_members)
            db.session.commit()
            print("✓ Database initialized with sample data")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
