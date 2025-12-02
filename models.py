"""
Database models for user authentication and project management
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    company = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user')  # user, admin
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    """Project model for tracking validation projects"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, in_review, approved, executed

    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # URS information
    urs_filename = db.Column(db.String(255))
    urs_text = db.Column(db.Text)

    # Template information
    template_filename = db.Column(db.String(255))

    # Generated content
    test_steps = db.Column(db.Text)  # JSON string

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = db.relationship('ProjectVersion', backref='project', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='ProjectVersion.version_number.desc()')

    def __repr__(self):
        return f'<Project {self.name}>'

    def get_latest_version(self):
        """Get the most recent version"""
        return self.versions.first()

    def create_version(self, test_steps, notes=''):
        """Create a new version of the project"""
        version_num = self.versions.count() + 1
        version = ProjectVersion(
            project_id=self.id,
            version_number=version_num,
            test_steps=test_steps,
            notes=notes
        )
        db.session.add(version)
        return version


class ProjectVersion(db.Model):
    """Version history for projects"""
    __tablename__ = 'project_versions'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    test_steps = db.Column(db.Text)  # JSON string
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(120))

    def __repr__(self):
        return f'<ProjectVersion {self.project_id} v{self.version_number}>'


class Template(db.Model):
    """Template library for test scripts"""
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # IQ, OQ, PQ, UAT, Regression
    is_builtin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))

    # Owner (null for built-in templates)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Template {self.name}>'


def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_demo_user()
        create_builtin_templates()


def create_demo_user():
    """Create demo user if it doesn't exist"""
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
        demo_user.set_password('demo123')  # Simple password for demo
        db.session.add(demo_user)
        db.session.commit()
        print("✓ Demo user created: demo@testscriptgen.com / demo123")


def create_builtin_templates():
    """Create built-in template entries"""
    builtin_templates = [
        {
            'name': 'Standard IQ Test Script',
            'description': 'Installation Qualification test script template',
            'category': 'IQ',
            'filename': 'builtin_iq_template.docx'
        },
        {
            'name': 'Standard OQ Test Script',
            'description': 'Operational Qualification test script template',
            'category': 'OQ',
            'filename': 'builtin_oq_template.docx'
        },
        {
            'name': 'Standard PQ Test Script',
            'description': 'Performance Qualification test script template',
            'category': 'PQ',
            'filename': 'builtin_pq_template.docx'
        },
        {
            'name': 'UAT Test Script',
            'description': 'User Acceptance Testing template',
            'category': 'UAT',
            'filename': 'builtin_uat_template.docx'
        },
    ]

    for template_data in builtin_templates:
        existing = Template.query.filter_by(filename=template_data['filename']).first()
        if not existing:
            template = Template(
                name=template_data['name'],
                description=template_data['description'],
                category=template_data['category'],
                filename=template_data['filename'],
                is_builtin=True,
                is_active=True
            )
            db.session.add(template)

    db.session.commit()
