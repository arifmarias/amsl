import streamlit as st
import bcrypt
from database.operations import DatabaseOperations
from datetime import datetime

class AuthenticationManager:
    """Handle user authentication and session management"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables"""
        # Initialize session variables with persistence
        session_vars = {
            'authenticated': False,
            'user_id': None,
            'username': None,
            'user_role': None,
            'user_full_name': None,
            'login_time': None,
            'session_initialized': True
        }
        
        for var, default_value in session_vars.items():
            if var not in st.session_state:
                st.session_state[var] = default_value
    
    @staticmethod
    def login_user(username: str, password: str):
        """Authenticate user and set session"""
        db_ops = DatabaseOperations()
        try:
            user = db_ops.authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.user_role = user.role
                st.session_state.user_full_name = user.full_name
                st.session_state.login_time = datetime.now()
                return True, "Login successful!"
            else:
                return False, "Invalid username or password"
        except Exception as e:
            return False, f"Login error: {str(e)}"
        finally:
            db_ops.close()
    
    @staticmethod
    def logout_user():
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.user_full_name = None
        st.session_state.login_time = None
        st.rerun()
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_current_user():
        """Get current user information"""
        if AuthenticationManager.is_authenticated():
            return {
                'id': st.session_state.user_id,
                'username': st.session_state.username,
                'role': st.session_state.user_role,
                'full_name': st.session_state.user_full_name,
                'login_time': st.session_state.login_time
            }
        return None
    
    @staticmethod
    def has_role(required_role):
        """Check if current user has required role"""
        if not AuthenticationManager.is_authenticated():
            return False
        
        user_role = st.session_state.user_role
        
        # Role hierarchy: admin > user > finance
        role_hierarchy = {
            'admin': 3,
            'user': 2,
            'finance': 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    @staticmethod
    def require_auth(func):
        """Decorator to require authentication"""
        def wrapper(*args, **kwargs):
            if not AuthenticationManager.is_authenticated():
                AuthenticationManager.show_login_page()
                return
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def require_role(required_role):
        """Decorator to require specific role"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not AuthenticationManager.is_authenticated():
                    AuthenticationManager.show_login_page()
                    return
                if not AuthenticationManager.has_role(required_role):
                    st.error(f"Access denied. Required role: {required_role}")
                    return
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def show_login_page():
        """Display login page"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🔐 Login to Project Management System</h1>
            <p>Please enter your credentials to access the system</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.container():
                st.markdown("""
                <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 10px; border: 1px solid #dee2e6;">
                """, unsafe_allow_html=True)
                
                with st.form("login_form"):
                    st.markdown("### 👤 User Login")
                    
                    username = st.text_input(
                        "Username",
                        placeholder="Enter your username",
                        help="Default admin username: admin"
                    )
                    
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        help="Default admin password: admin123"
                    )
                    
                    submit_button = st.form_submit_button(
                        "🚀 Login",
                        use_container_width=True
                    )
                    
                    if submit_button:
                        if username and password:
                            with st.spinner("Authenticating..."):
                                success, message = AuthenticationManager.login_user(username, password)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        else:
                            st.warning("Please enter both username and password")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Default credentials info
                st.info("""
                **Default Admin Credentials:**
                - Username: `admin`
                - Password: `admin123`
                """)
                
                # System info
                st.markdown("---")
                st.markdown("""
                <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
                    <p>🔒 Secure authentication with bcrypt encryption</p>
                    <p>📊 Project Management System v1.0.0</p>
                </div>
                """, unsafe_allow_html=True)

def show_user_info_sidebar():
    """Show user information in sidebar"""
    if AuthenticationManager.is_authenticated():
        user = AuthenticationManager.get_current_user()
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 User Info")
            
            # User details in a nice format
            st.markdown(f"""
            **Name:** {user['full_name']}  
            **Username:** {user['username']}  
            **Role:** {user['role'].title()}  
            **Login Time:** {user['login_time'].strftime('%H:%M:%S')}
            """)
            
            # Role badge
            role_colors = {
                'admin': '🔴',
                'user': '🟢', 
                'finance': '🟡'
            }
            role_color = role_colors.get(user['role'], '⚪')
            st.markdown(f"{role_color} **{user['role'].upper()}** ACCESS")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                AuthenticationManager.logout_user()

def create_new_user_form():
    """Admin form to create new users"""
    if not AuthenticationManager.has_role('admin'):
        st.error("Access denied. Admin access required.")
        return
    
    st.subheader("➕ Create New User")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", help="Unique username for the user")
            full_name = st.text_input("Full Name*", help="User's full name")
            role = st.selectbox("Role*", ["user", "finance", "admin"], help="User access level")
        
        with col2:
            email = st.text_input("Email*", help="User's email address")
            password = st.text_input("Password*", type="password", help="User's password")
            confirm_password = st.text_input("Confirm Password*", type="password")
        
        submit = st.form_submit_button("🎯 Create User")
        
        if submit:
            # Validation
            if not all([username, full_name, email, password, confirm_password]):
                st.error("All fields are required!")
                return
            
            if password != confirm_password:
                st.error("Passwords don't match!")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters!")
                return
            
            # Create user
            db_ops = DatabaseOperations()
            try:
                user = db_ops.create_user(username, password, role, full_name, email)
                st.success(f"✅ User '{username}' created successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to create user: {str(e)}")
            finally:
                db_ops.close()

def show_user_management():
    """Show user management interface"""
    if not AuthenticationManager.has_role('admin'):
        st.error("Access denied. Admin access required.")
        return
    
    st.title("👥 User Management")
    
    # Create new user section
    with st.expander("➕ Create New User", expanded=False):
        create_new_user_form()
    
    # List existing users
    st.subheader("📋 Existing Users")
    
    db_ops = DatabaseOperations()
    try:
        users = db_ops.get_all_users()
        
        if users:
            for user in users:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{user.full_name}** ({user.username})")
                
                with col2:
                    st.write(f"📧 {user.email}")
                
                with col3:
                    role_colors = {'admin': '🔴', 'user': '🟢', 'finance': '🟡'}
                    role_color = role_colors.get(user.role, '⚪')
                    st.write(f"{role_color} {user.role.upper()}")
                
                with col4:
                    if user.username != 'admin':  # Don't allow deleting admin
                        if st.button("🗑️", key=f"delete_{user.id}", help="Delete user"):
                            # Would implement delete functionality here
                            st.warning("Delete functionality will be added in later steps")
                
                st.markdown("---")
        else:
            st.info("No users found.")
            
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
    finally:
        db_ops.close()