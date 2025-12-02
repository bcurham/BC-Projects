"""
Authentication routes and utilities
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        company = request.form.get('company', '').strip()

        # Validation
        errors = []

        if not email or '@' not in email:
            errors.append('Valid email is required')

        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')

        if password != confirm_password:
            errors.append('Passwords do not match')

        # Check if user exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')

        if User.query.filter_by(username=username).first():
            errors.append('Username already taken')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')

        # Create new user
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            company=company,
            role='user'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('landing'))


@auth_bp.route('/demo')
def demo_login():
    """Quick demo login - bypasses authentication"""
    # Find or create demo user
    demo_user = User.query.filter_by(email='demo@testscriptgen.com').first()

    if not demo_user:
        demo_user = User(
            email='demo@testscriptgen.com',
            username='demo_user',
            full_name='Demo User',
            company='Demo Company',
            is_demo=True,
            role='user'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()

    # Log in demo user
    login_user(demo_user)
    demo_user.last_login = datetime.utcnow()
    db.session.commit()

    flash('Welcome to Demo Mode! Explore all features freely.', 'success')
    return redirect(url_for('dashboard'))
