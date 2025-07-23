import streamlit as st
import pandas as pd
from datetime import datetime
from database.operations import DatabaseOperations
from modules.auth import AuthenticationManager

def show_settings():
    """Main settings page"""
    
    st.title("⚙️ System Settings")
    
    user = AuthenticationManager.get_current_user()
    
    # Settings tabs based on user role
    if user['role'] == 'admin':
        tab1, tab2, tab3, tab4 = st.tabs(["🏢 Companies", "📋 Task Descriptions", "👥 Users", "🔧 System"])
        
        with tab1:
            show_company_management()
        
        with tab2:
            show_task_management()
        
        with tab3:
            show_user_management_settings()
        
        with tab4:
            show_system_settings()
    
    elif user['role'] == 'user':
        tab1, tab2 = st.tabs(["🏢 Companies", "👤 Profile"])
        
        with tab1:
            show_company_management()
        
        with tab2:
            show_user_profile()
    
    else:  # finance user
        tab1 = st.tabs(["👤 Profile"])[0]
        
        with tab1:
            show_user_profile()

def show_company_management():
    """Enhanced company management interface"""
    st.subheader("🏢 Company Management")
    
    # Handle edit company if requested
    if st.session_state.get('edit_company_id'):
        show_edit_company_form(st.session_state.edit_company_id)
        return
    
    # Statistics section
    show_company_statistics()
    
    # Add new company section
    with st.expander("➕ Add New Company", expanded=False):
        show_add_company_form()
    
    # Company list with enhanced features
    show_company_list()

def show_company_statistics():
    """Show company statistics"""
    db_ops = DatabaseOperations()
    try:
        companies = db_ops.get_all_companies()
        customers = [c for c in companies if c.company_type == 'customer']
        suppliers = [c for c in companies if c.company_type == 'supplier']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Companies", len(companies))
        
        with col2:
            st.metric("Customers", len(customers))
        
        with col3:
            st.metric("Suppliers", len(suppliers))
        
        with col4:
            # Count companies with complete info (phone, email, contact person)
            complete_info = sum(1 for c in companies if c.phone and c.email and c.contact_person)
            st.metric("Complete Profiles", complete_info)
        
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")
    finally:
        db_ops.close()

def show_add_company_form():
    """Enhanced add company form"""
    # Clear form if just submitted
    if st.session_state.get('company_form_submitted', False):
        st.session_state.company_form_submitted = False
        st.rerun()
        
    with st.form("add_company_form", clear_on_submit=True):
        st.markdown("### 🏢 Company Information")
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name *", 
                placeholder="Enter company name",
                help="Official company name"
            )
            company_type = st.selectbox(
                "Company Type *", 
                ["customer", "supplier"],
                help="Select whether this is a customer or supplier"
            )
            phone = st.text_input(
                "Phone", 
                placeholder="+880-1XXXXXXXXX",
                help="Company phone number"
            )
            website = st.text_input(
                "Website", 
                placeholder="https://company.com",
                help="Company website (optional)"
            )
        
        with col2:
            email = st.text_input(
                "Email", 
                placeholder="contact@company.com",
                help="Company email address"
            )
            contact_person = st.text_input(
                "Contact Person", 
                placeholder="John Doe",
                help="Primary contact person name"
            )
            designation = st.text_input(
                "Designation", 
                placeholder="Manager",
                help="Contact person's designation"
            )
            tax_id = st.text_input(
                "Tax ID / TIN", 
                placeholder="123456789",
                help="Company tax identification number"
            )
        
        # Address information
        st.markdown("### 📍 Address Information")
        address = st.text_area(
            "Address", 
            placeholder="Street address, City, Postal Code",
            help="Complete company address"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City", placeholder="Dhaka")
        with col2:
            postal_code = st.text_input("Postal Code", placeholder="1200")
        
        # Additional information
        st.markdown("### 📝 Additional Information")
        notes = st.text_area(
            "Notes", 
            placeholder="Any additional notes about this company",
            help="Internal notes (optional)"
        )
        
        # Submit button
        submitted = st.form_submit_button("🏢 Add Company", use_container_width=True)
        
        if submitted:
            # Enhanced validation
            if not company_name or not company_type:
                st.error("Company name and type are required!")
                return
            
            # Email validation
            if email and '@' not in email:
                st.error("Please enter a valid email address!")
                return
            
            # Website validation
            if website and not (website.startswith('http://') or website.startswith('https://')):
                website = 'https://' + website
            
            db_ops = DatabaseOperations()
            try:
                # Create enhanced company record
                company = db_ops.create_enhanced_company(
                    name=company_name,
                    company_type=company_type,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    phone=phone,
                    email=email,
                    website=website,
                    contact_person=contact_person,
                    designation=designation,
                    tax_id=tax_id,
                    notes=notes
                )
                st.success(f"✅ Company '{company_name}' added successfully!")
                st.balloons()
                st.session_state.company_form_submitted = True
                st.rerun()
            except Exception as e:
                st.error(f"Error adding company: {str(e)}")
            finally:
                db_ops.close()

def show_company_list():
    """Enhanced company listing with search, filter, and actions"""
    st.subheader("📋 Company Directory")
    
    db_ops = DatabaseOperations()
    try:
        companies = db_ops.get_all_companies()
        
        if not companies:
            st.info("📭 No companies found. Add your first company above.")
            return
        
        # Enhanced filter options
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            type_filter = st.selectbox("Filter by Type", ["All", "customer", "supplier"])
        
        with col2:
            search_term = st.text_input("Search Companies", placeholder="Search by name, email, or contact")
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Name", "Type", "Date Added", "Contact Person"])
        
        with col4:
            view_mode = st.selectbox("View Mode", ["Card View", "Table View"])
        
        # Filter and sort companies
        filtered_companies = filter_and_sort_companies(companies, type_filter, search_term, sort_by)
        
        if not filtered_companies:
            st.info("No companies match your search criteria.")
            return
        
        # Display companies based on view mode
        if view_mode == "Card View":
            show_companies_card_view(filtered_companies)
        else:
            show_companies_table_view(filtered_companies)
            
    except Exception as e:
        st.error(f"Error loading companies: {str(e)}")
    finally:
        db_ops.close()

def filter_and_sort_companies(companies, type_filter, search_term, sort_by):
    """Filter and sort companies based on criteria"""
    filtered = companies
    
    # Filter by type
    if type_filter != "All":
        filtered = [c for c in filtered if c.company_type == type_filter]
    
    # Search filter
    if search_term:
        search_lower = search_term.lower()
        filtered = [c for c in filtered if 
                   search_lower in c.name.lower() or
                   (c.email and search_lower in c.email.lower()) or
                   (c.contact_person and search_lower in c.contact_person.lower())]
    
    # Sort
    if sort_by == "Name":
        filtered.sort(key=lambda x: x.name.lower())
    elif sort_by == "Type":
        filtered.sort(key=lambda x: x.company_type)
    elif sort_by == "Date Added":
        filtered.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "Contact Person":
        filtered.sort(key=lambda x: x.contact_person or "")
    
    return filtered

def show_companies_card_view(companies):
    """Display companies in card view"""
    cols_per_row = 2
    for i in range(0, len(companies), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, company in enumerate(companies[i:i+cols_per_row]):
            with cols[j]:
                show_company_card(company)

def show_company_card(company):
    """Display individual company card"""
    # Card styling
    type_icon = "🏢" if company.company_type == "customer" else "🏭"
    type_color = "#28a745" if company.company_type == "customer" else "#007bff"
    
    st.markdown(f"""
    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; background-color: #f8f9fa;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0; color: {type_color};">{type_icon} {company.name}</h4>
            <span style="background-color: {type_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">
                {company.company_type.upper()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Company details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if company.contact_person:
            st.markdown(f"👤 **Contact:** {company.contact_person}")
            if company.designation:
                st.markdown(f"📋 **Position:** {company.designation}")
        
        if company.phone:
            st.markdown(f"📞 **Phone:** {company.phone}")
        
        if company.email:
            st.markdown(f"📧 **Email:** {company.email}")
        
        if hasattr(company, 'website') and company.website:
            st.markdown(f"🌐 **Website:** {company.website}")
    
    with col2:
        # Action buttons
        col_edit, col_delete = st.columns(2)
        
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_card_{company.id}", use_container_width=True):
                st.session_state.edit_company_id = company.id
                st.rerun()
        
        with col_delete:
            if st.button("🗑️ Delete", key=f"delete_card_{company.id}", use_container_width=True):
                st.session_state.delete_company_id = company.id
                st.rerun()
    
    # Address (if available)
    if company.address:
        st.markdown(f"📍 **Address:** {company.address}")
    
    # Handle delete confirmation
    if st.session_state.get('delete_company_id') == company.id:
        if st.button(f"⚠️ Confirm Delete '{company.name}'?", key=f"confirm_delete_{company.id}"):
            delete_company(company.id)

def show_companies_table_view(companies):
    """Display companies in table view"""
    # Prepare data for table
    table_data = []
    for company in companies:
        table_data.append({
            'ID': company.id,
            'Name': company.name,
            'Type': company.company_type.title(),
            'Contact Person': company.contact_person or 'N/A',
            'Phone': company.phone or 'N/A',
            'Email': company.email or 'N/A',
            'Date Added': company.created_at.strftime('%Y-%m-%d') if company.created_at else 'N/A'
        })
    
    df = pd.DataFrame(table_data)
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Type": st.column_config.TextColumn("Type", help="Company type"),
            "Date Added": st.column_config.TextColumn("Date Added", help="Date company was added")
        }
    )
    
    # Action section for table view
    st.subheader("📝 Company Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_company = st.selectbox(
            "Select Company:",
            options=[(c.id, c.name) for c in companies],
            format_func=lambda x: f"#{x[0]} - {x[1]}"
        )
    
    with col2:
        if st.button("✏️ Edit Company", use_container_width=True):
            st.session_state.edit_company_id = selected_company[0]
            st.rerun()
    
    with col3:
        if st.button("🗑️ Delete Company", use_container_width=True):
            st.session_state.delete_company_id = selected_company[0]
            st.rerun()
    
    # Handle delete confirmation for table view
    if st.session_state.get('delete_company_id'):
        company_to_delete = next((c for c in companies if c.id == st.session_state.delete_company_id), None)
        if company_to_delete:
            st.warning(f"⚠️ Are you sure you want to delete '{company_to_delete.name}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", key="confirm_table_delete"):
                    delete_company(st.session_state.delete_company_id)
            with col2:
                if st.button("❌ Cancel", key="cancel_table_delete"):
                    del st.session_state.delete_company_id
                    st.rerun()

def show_edit_company_form(company_id):
    """Show edit company form"""
    st.subheader("✏️ Edit Company")
    
    # Back button
    if st.button("⬅️ Back to Company List"):
        del st.session_state.edit_company_id
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        company = db_ops.get_company_by_id(company_id)
        
        if not company:
            st.error("Company not found!")
            return
        
        with st.form("edit_company_form"):
            st.markdown(f"### Editing: {company.name}")
            
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name *", value=company.name)
                company_type = st.selectbox(
                    "Company Type *", 
                    ["customer", "supplier"],
                    index=0 if company.company_type == "customer" else 1
                )
                phone = st.text_input("Phone", value=company.phone or "")
                website = st.text_input("Website", value=getattr(company, 'website', '') or "")
            
            with col2:
                email = st.text_input("Email", value=company.email or "")
                contact_person = st.text_input("Contact Person", value=company.contact_person or "")
                designation = st.text_input("Designation", value=company.designation or "")
                tax_id = st.text_input("Tax ID", value=getattr(company, 'tax_id', '') or "")
            
            # Address
            address = st.text_area("Address", value=company.address or "")
            
            col1, col2 = st.columns(2)
            with col1:
                city = st.text_input("City", value=getattr(company, 'city', '') or "")
            with col2:
                postal_code = st.text_input("Postal Code", value=getattr(company, 'postal_code', '') or "")
            
            notes = st.text_area("Notes", value=getattr(company, 'notes', '') or "")
            
            # Submit button
            submitted = st.form_submit_button("💾 Update Company", use_container_width=True)
            
            if submitted:
                if not company_name or not company_type:
                    st.error("Company name and type are required!")
                    return
                
                try:
                    # Update company
                    updated = db_ops.update_company(
                        company_id=company_id,
                        name=company_name,
                        company_type=company_type,
                        address=address,
                        city=city,
                        postal_code=postal_code,
                        phone=phone,
                        email=email,
                        website=website,
                        contact_person=contact_person,
                        designation=designation,
                        tax_id=tax_id,
                        notes=notes
                    )
                    
                    if updated:
                        st.success(f"✅ Company '{company_name}' updated successfully!")
                        st.balloons()
                        del st.session_state.edit_company_id
                        st.rerun()
                    else:
                        st.error("Failed to update company!")
                        
                except Exception as e:
                    st.error(f"Error updating company: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading company: {str(e)}")
    finally:
        db_ops.close()

def delete_company(company_id):
    """Delete a company"""
    db_ops = DatabaseOperations()
    try:
        # Check if company is used in any projects
        projects_using_company = db_ops.get_projects_by_company(company_id)
        
        if projects_using_company:
            st.error(f"Cannot delete company! It's used in {len(projects_using_company)} project(s).")
            return
        
        # Delete company
        if db_ops.delete_company(company_id):
            st.success("✅ Company deleted successfully!")
            # Clear delete state
            if 'delete_company_id' in st.session_state:
                del st.session_state.delete_company_id
            st.rerun()
        else:
            st.error("Failed to delete company!")
            
    except Exception as e:
        st.error(f"Error deleting company: {str(e)}")
    finally:
        db_ops.close()

# Enhanced Task Management (similar pattern)
def show_task_management():
    """Enhanced task description management"""
    st.subheader("📋 Task Description Management")
    
    # Handle edit task if requested
    if st.session_state.get('edit_task_id'):
        show_edit_task_form(st.session_state.edit_task_id)
        return
    
    # Task statistics
    show_task_statistics()
    
    # Add new task description
    with st.expander("➕ Add New Task Description", expanded=False):
        show_add_task_form()
    
    # Task list
    show_task_list()

def show_task_statistics():
    """Show task statistics"""
    db_ops = DatabaseOperations()
    try:
        tasks = db_ops.get_all_task_descriptions_with_percentage()
        active_tasks = [t for t in tasks if t.is_active]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Tasks", len(tasks))
        
        with col2:
            st.metric("Active Tasks", len(active_tasks))
        
        with col3:
            st.metric("Inactive Tasks", len(tasks) - len(active_tasks))
        
    except Exception as e:
        st.error(f"Error loading task statistics: {str(e)}")
    finally:
        db_ops.close()

def show_add_task_form():
    """Enhanced add task form"""
    if st.session_state.get('task_form_submitted', False):
        st.session_state.task_form_submitted = False
        st.rerun()
        
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input(
            "Task Name *", 
            placeholder="Enter task name",
            help="Descriptive name for the task"
        )
        description = st.text_area(
            "Description", 
            placeholder="Detailed task description",
            help="What does this task involve?"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            default_percentage = st.number_input(
                "Default Profit %", 
                min_value=0.0, 
                max_value=100.0, 
                value=0.0,
                step=0.1,
                help="Default profit percentage for this task"
            )
        
        with col2:
            is_active = st.checkbox("Active", value=True, help="Is this task currently active?")
        
        submit = st.form_submit_button("📋 Add Task", use_container_width=True)
        
        if submit:
            if not task_name:
                st.error("Task name is required!")
            else:
                db_ops = DatabaseOperations()
                try:
                    # Store percentage info in description for now (better approach)
                    enhanced_description = description
                    if default_percentage > 0:
                        enhanced_description = f"{description}\nDefault: {default_percentage}%" if description else f"Default: {default_percentage}%"
                    
                    task = db_ops.create_task_description(
                        task_name=task_name, 
                        description=enhanced_description
                    )
                    task.is_active = is_active
                    db_ops.db.commit()
                    
                    st.success(f"✅ Task '{task_name}' added successfully with {default_percentage}% default profit!")
                    st.session_state.task_form_submitted = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {str(e)}")
                finally:
                    db_ops.close()

def show_task_list():
    """Enhanced task listing with proper percentage display"""
    st.subheader("📋 Task Directory")
    
    db_ops = DatabaseOperations()
    try:
        tasks = db_ops.get_all_task_descriptions_with_percentage()
        
        if not tasks:
            st.info("📭 No task descriptions found. Add your first task above.")
            return
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col2:
            search_term = st.text_input("Search Tasks", placeholder="Search by name or description")
        
        # Filter tasks
        filtered_tasks = tasks
        if status_filter == "Active":
            filtered_tasks = [t for t in filtered_tasks if t.is_active]
        elif status_filter == "Inactive":
            filtered_tasks = [t for t in filtered_tasks if not t.is_active]
        
        if search_term:
            search_lower = search_term.lower()
            filtered_tasks = [t for t in filtered_tasks if 
                            search_lower in t.task_name.lower() or
                            (hasattr(t, 'clean_description') and t.clean_description and search_lower in t.clean_description.lower())]
        
        # Display tasks with proper formatting
        for task in filtered_tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    status_icon = "🟢" if task.is_active else "🔴"
                    st.markdown(f"**{status_icon} {task.task_name}**")
                    # Show clean description without percentage info
                    clean_desc = getattr(task, 'clean_description', task.description or "")
                    if clean_desc and clean_desc.strip():
                        display_desc = clean_desc[:100] + "..." if len(clean_desc) > 100 else clean_desc
                        st.caption(display_desc)
                
                with col2:
                    default_pct = getattr(task, 'default_percentage', 0.0)
                    st.metric("Default Profit", f"{default_pct}%")
                    st.write(f"**Status:** {'Active' if task.is_active else 'Inactive'}")
                
                with col3:
                    if st.button("✏️", key=f"edit_task_{task.id}", help="Edit task"):
                        st.session_state.edit_task_id = task.id
                        st.rerun()
                
                with col4:
                    if st.button("🗑️", key=f"delete_task_{task.id}", help="Delete task"):
                        st.session_state.delete_task_id = task.id
                        st.rerun()
                
                st.markdown("---")
        
        # Handle delete confirmation
        if st.session_state.get('delete_task_id'):
            task_to_delete = next((t for t in tasks if t.id == st.session_state.delete_task_id), None)
            if task_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete '{task_to_delete.task_name}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", key="confirm_task_delete"):
                        delete_task(st.session_state.delete_task_id)
                with col2:
                    if st.button("❌ Cancel", key="cancel_task_delete"):
                        del st.session_state.delete_task_id
                        st.rerun()
            
    except Exception as e:
        st.error(f"Error loading tasks: {str(e)}")
    finally:
        db_ops.close()

def show_edit_task_form(task_id):
    """Show edit task form with proper percentage handling"""
    st.subheader("✏️ Edit Task Description")
    
    if st.button("⬅️ Back to Task List"):
        del st.session_state.edit_task_id
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        # Get task with percentage info
        all_tasks = db_ops.get_all_task_descriptions_with_percentage()
        task = next((t for t in all_tasks if t.id == task_id), None)
        
        if not task:
            st.error("Task not found!")
            return
        
        with st.form("edit_task_form"):
            st.markdown(f"### Editing: {task.task_name}")
            
            task_name = st.text_input("Task Name *", value=task.task_name)
            
            # Use clean description without percentage
            clean_desc = getattr(task, 'clean_description', task.description or "")
            description = st.text_area("Description", value=clean_desc)
            
            col1, col2 = st.columns(2)
            with col1:
                current_percentage = getattr(task, 'default_percentage', 0.0)
                default_percentage = st.number_input(
                    "Default Profit %", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=current_percentage,
                    step=0.1
                )
            
            with col2:
                is_active = st.checkbox("Active", value=task.is_active)
            
            submitted = st.form_submit_button("💾 Update Task", use_container_width=True)
            
            if submitted:
                if not task_name:
                    st.error("Task name is required!")
                    return
                
                try:
                    # Create enhanced description with percentage
                    enhanced_description = description
                    if default_percentage > 0:
                        enhanced_description = f"{description}\nDefault: {default_percentage}%" if description else f"Default: {default_percentage}%"
                    
                    # Update task
                    task_obj = db_ops.get_task_description_by_id(task_id)
                    if task_obj:
                        task_obj.task_name = task_name
                        task_obj.description = enhanced_description
                        task_obj.is_active = is_active
                        task_obj.updated_at = datetime.utcnow()
                        
                        db_ops.db.commit()
                        
                        st.success(f"✅ Task '{task_name}' updated successfully with {default_percentage}% default profit!")
                        del st.session_state.edit_task_id
                        st.rerun()
                    else:
                        st.error("Failed to update task!")
                        
                except Exception as e:
                    st.error(f"Error updating task: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading task: {str(e)}")
    finally:
        db_ops.close()

def delete_task(task_id):
    """Delete a task"""
    db_ops = DatabaseOperations()
    try:
        # Check if task is used in any profit sharing configs
        configs_using_task = db_ops.get_profit_configs_by_task(task_id)
        
        if configs_using_task:
            st.error(f"Cannot delete task! It's used in {len(configs_using_task)} profit sharing configuration(s).")
            return
        
        if db_ops.delete_task_description(task_id):
            st.success("✅ Task deleted successfully!")
            if 'delete_task_id' in st.session_state:
                del st.session_state.delete_task_id
            st.rerun()
        else:
            st.error("Failed to delete task!")
            
    except Exception as e:
        st.error(f"Error deleting task: {str(e)}")
    finally:
        db_ops.close()

# Keep existing functions
def show_user_management_settings():
    """User management for admin"""
    from modules.auth import show_user_management
    show_user_management()

def show_system_settings():
    """System-wide settings"""
    st.subheader("🔧 System Settings")
    
def show_system_settings():
    """System-wide settings"""
    st.subheader("🔧 System Settings")
    
    # Database section
    st.markdown("### 🗄️ Database")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Test Database Connection"):
            from database.connection import test_connection
            if test_connection():
                st.success("✅ Database connection successful!")
            else:
                st.error("❌ Database connection failed!")
    
    with col2:
        if st.button("📊 Database Statistics"):
            db_ops = DatabaseOperations()
            try:
                stats = db_ops.get_project_statistics()
                st.info(f"""
                **Database Statistics:**
                - Total Projects: {stats['total_projects']}
                - Active Projects: {stats['active_projects']}
                - Total Revenue: ৳{stats['total_revenue']:,.2f}
                """)
            except Exception as e:
                st.error(f"Error loading statistics: {str(e)}")
            finally:
                db_ops.close()
    
    # Backup section
    st.markdown("### 💾 Backup & Restore")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Create Backup"):
            st.info("Backup functionality will be implemented in later phases.")
    
    with col2:
        if st.button("📥 Restore Backup"):
            st.info("Restore functionality will be implemented in later phases.")
    
    # System information
    st.markdown("### ℹ️ System Information")
    import os
    
    st.info(f"""
    **Application Version:** v1.0.0  
    **Database Size:** {os.path.getsize('project_management.db') if os.path.exists('project_management.db') else 0} bytes  
    **Python Version:** {st.session_state.get('python_version', 'Unknown')}  
    **Streamlit Version:** {st.__version__}
    """)

def show_user_profile():
    """User profile settings"""
    st.subheader("👤 User Profile")
    
    user = AuthenticationManager.get_current_user()
    
    # Display current user info
    st.markdown("### 📋 Current Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Full Name:** {user['full_name']}  
        **Username:** {user['username']}  
        **Role:** {user['role'].title()}  
        **User ID:** #{user['id']}
        """)
    
    with col2:
        st.info(f"""
        **Login Time:** {user['login_time'].strftime('%Y-%m-%d %H:%M:%S')}  
        **Session Status:** Active  
        **Access Level:** {'Full Access' if user['role'] == 'admin' else 'Limited Access'}
        """)
    
    # Change password section
    st.markdown("### 🔒 Change Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("🔐 Change Password")
        
        if submit:
            if not all([current_password, new_password, confirm_password]):
                st.error("All fields are required!")
            elif new_password != confirm_password:
                st.error("New passwords don't match!")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters!")
            else:
                # Verify current password
                db_ops = DatabaseOperations()
                try:
                    if db_ops.authenticate_user(user['username'], current_password):
                        st.info("Password change functionality will be implemented in later steps.")
                        # In full implementation: update password in database
                    else:
                        st.error("Current password is incorrect!")
                except Exception as e:
                    st.error(f"Error changing password: {str(e)}")
                finally:
                    db_ops.close()
    
    # User preferences
    st.markdown("### ⚙️ Preferences")
    with st.form("preferences_form"):
        email_notifications = st.checkbox("Email Notifications", value=True)
        dashboard_refresh = st.selectbox("Dashboard Auto-refresh", ["Never", "Every 30 seconds", "Every minute", "Every 5 minutes"])
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        
        save_prefs = st.form_submit_button("💾 Save Preferences")
        
        if save_prefs:
            st.success("✅ Preferences saved! (Feature will be fully implemented in later steps)")
    
    # Session information
    st.markdown("### 🔄 Session Information")
    st.info(f"""
    **Current Session:** Active since {user['login_time'].strftime('%H:%M:%S')}  
    **Session Duration:** {(st.session_state.get('current_time', user['login_time']) - user['login_time']).seconds // 60} minutes  
    **Last Activity:** Just now
    """)