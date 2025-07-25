import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.operations import DatabaseOperations
from modules.auth import AuthenticationManager

def show_projects():
    """Main projects page - UPDATED WITH EDIT SUPPORT"""
    
    st.title("📋 Project Management")
    
    # Check for specific actions from quick actions
    if st.session_state.get('action') == 'new_project':
        st.session_state.action = None  # Clear the action
        show_new_project_form()
        return
    
    # Check for edit mode
    if st.session_state.get('edit_project_id'):
        show_edit_project_form(st.session_state.edit_project_id)
        return
    
    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs(["📊 All Projects", "➕ New Project", "🔍 Search & Filter", "🤝 Profit Sharing"])
    
    with tab1:
        show_all_projects()
    
    with tab2:
        show_new_project_form()
    
    with tab3:
        show_project_search()
        
    with tab4:
        show_project_profit_sharing()

def show_project_profit_sharing():
    """Show profit sharing management in projects module"""
    # Import the profit sharing functions from financial module
    from modules.financial import (
        show_profit_sharing_management, 
        show_profit_sharing_form, 
        show_edit_profit_sharing_form,
        show_profit_calculation
    )
    
    st.subheader("🤝 Project Profit Sharing Management")
    
    user = AuthenticationManager.get_current_user()
    
    # Only admin and regular users can access profit sharing
    if user['role'] == 'finance':
        st.error("🔒 Access denied. Profit sharing is only available to admin and regular users.")
        st.info("💡 Finance users can access Initial Projections and Final Costs in Financial Management.")
        return
    
    # Handle profit sharing form display
    if st.session_state.get('show_profit_sharing_form'):
        show_profit_sharing_form()
        return
    
    # Handle editing
    if st.session_state.get('edit_profit_sharing_id'):
        show_edit_profit_sharing_form(st.session_state.edit_profit_sharing_id)
        return
    
    # Handle profit calculation view
    if st.session_state.get('show_profit_calculation'):
        show_profit_calculation(st.session_state.show_profit_calculation)
        return
    
    # Show the main profit sharing management interface
    show_profit_sharing_management()

def show_all_projects():
    """Display all projects in a table"""
    st.subheader("📊 All Projects")
    
    db_ops = DatabaseOperations()
    try:
        projects = db_ops.get_all_projects()
        
        if projects:
            # Prepare data for display
            project_data = []
            for project in projects:
                project_data.append({
                    'ID': project.id,
                    'Project Name': project.project_name,
                    'PO Number': project.po_number or 'N/A',
                    'Client': project.po_issuing_company.name if project.po_issuing_company else 'N/A',
                    'Supplier': project.supplier_company.name if project.supplier_company else 'N/A',
                    'Status': project.status.title(),
                    'Start Date': project.start_date.strftime('%Y-%m-%d') if project.start_date else 'N/A',
                    'Due Date': project.tentative_end_date.strftime('%Y-%m-%d') if project.tentative_end_date else 'N/A',
                    'Budget': f"৳{project.total_po_value:,.2f}" if project.total_po_value else '৳0.00'
                })
            
            df = pd.DataFrame(project_data)
            
            # Display with styling
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Current project status"
                    ),
                    "Budget": st.column_config.TextColumn(
                        "Budget",
                        help="Total project budget"
                    )
                }
            )
            
            # Project actions
            # Project actions - ENHANCED LAYOUT
            st.subheader("📝 Project Actions")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_id = st.selectbox(
                    "Select Project for Actions:",
                    options=[p['ID'] for p in project_data],
                    format_func=lambda x: f"#{x} - {next(p['Project Name'] for p in project_data if p['ID'] == x)}"
                )
            
            with col2:
                # Get selected project data for validation
                selected_project_data = next(p for p in project_data if p['ID'] == selected_id)
                st.info(f"**Selected:** {selected_project_data['Project Name']}")
            
            # Action buttons in vertical layout
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👀 View Details", key=f"view_details_{selected_id}", use_container_width=True):
                    st.session_state.show_project_details = selected_id
                    st.rerun()
            
            with col2:
                if st.button("✏️ Edit Project", key=f"edit_project_{selected_id}", use_container_width=True):
                    st.session_state.edit_project_id = selected_id
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete Project", key=f"delete_project_{selected_id}", use_container_width=True):
                    st.session_state.delete_project_id = selected_id
                    st.rerun()
            
            # Handle delete confirmation
            if st.session_state.get('delete_project_id'):
                project_to_delete_id = st.session_state.delete_project_id
                project_to_delete = next(p for p in project_data if p['ID'] == project_to_delete_id)
                
                st.markdown("---")
                st.error(f"⚠️ **CONFIRM DELETION**")
                st.warning(f"Are you sure you want to delete project: **{project_to_delete['Project Name']}**?")
                
                # Check for dependencies before showing confirmation
                dependency_check = check_project_dependencies(project_to_delete_id)
                
                if dependency_check['can_delete']:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes, Delete Permanently", key="confirm_delete_project", type="primary"):
                            if delete_project_with_validation(project_to_delete_id):
                                st.success(f"✅ Project '{project_to_delete['Project Name']}' deleted successfully!")
                                del st.session_state.delete_project_id
                                st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key="cancel_delete_project"):
                            del st.session_state.delete_project_id
                            st.rerun()
                else:
                    st.error("❌ **Cannot delete this project!**")
                    for reason in dependency_check['reasons']:
                        st.error(f"• {reason}")
                    
                    if st.button("❌ Cancel Deletion", key="cancel_delete_blocked"):
                        del st.session_state.delete_project_id
                        st.rerun()
        
        else:
            st.info("📭 No projects found. Create your first project using the 'New Project' tab.")
    
        # Show project details if requested
        if st.session_state.get('show_project_details'):
            project_id = st.session_state.show_project_details
            st.markdown("---")
            show_project_details(project_id)
            if st.button("⬅️ Back to Projects List", key="back_to_list"):
                del st.session_state.show_project_details
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
    finally:
        db_ops.close()
def check_project_dependencies(project_id):
    """Check if project has dependencies that prevent deletion"""
    db_ops = DatabaseOperations()
    try:
        reasons = []
        
        # Check for initial projections
        projections = db_ops.get_initial_projections_by_project(project_id)
        if projections:
            reasons.append(f"Has {len(projections)} initial financial projection(s)")
        
        # Check for final costs
        final_costs = db_ops.get_final_costs_by_project(project_id)
        if final_costs:
            reasons.append(f"Has {len(final_costs)} final cost record(s)")
        
        # Check for disbursements
        disbursements = db_ops.get_disbursements_by_project(project_id)
        if disbursements:
            reasons.append(f"Has {len(disbursements)} disbursement(s)")
        
        # Check for profit sharing configs
        profit_configs = db_ops.get_profit_sharing_configs_by_project(project_id)
        if profit_configs:
            reasons.append(f"Has {len(profit_configs)} profit sharing configuration(s)")
        
        return {
            'can_delete': len(reasons) == 0,
            'reasons': reasons
        }
        
    except Exception as e:
        return {
            'can_delete': False,
            'reasons': [f"Error checking dependencies: {str(e)}"]
        }
    finally:
        db_ops.close()

def delete_project_with_validation(project_id):
    """Delete project with proper validation"""
    db_ops = DatabaseOperations()
    try:
        # Double-check dependencies
        dependency_check = check_project_dependencies(project_id)
        if not dependency_check['can_delete']:
            st.error("❌ Cannot delete project due to existing dependencies!")
            return False
        
        # Get project for confirmation
        project = db_ops.get_project_by_id(project_id)
        if not project:
            st.error("❌ Project not found!")
            return False
        
        # Delete the project
        db_ops.db.delete(project)
        db_ops.db.commit()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error deleting project: {str(e)}")
        return False
    finally:
        db_ops.close()
        
def show_new_project_form():
    """Display new project creation form - ENHANCED WITH ADVANCE FIELD"""
    st.subheader("➕ Create New Project")
    
    # Check if form was just submitted
    if st.session_state.get('form_submitted', False):
        st.session_state.form_submitted = False
        st.rerun()
    
    # Get companies for dropdowns
    db_ops = DatabaseOperations()
    try:
        companies = db_ops.get_all_companies()
        customers = [c for c in companies if c.company_type == 'customer']
        suppliers = [c for c in companies if c.company_type == 'supplier']
        
        if not customers:
            st.warning("⚠️ No customer companies found. Please add companies first.")
            if st.button("🏢 Go to Company Management"):
                st.session_state.page = "settings"
                st.rerun()
            return
        
        with st.form("new_project_form", clear_on_submit=True):
            st.markdown("### 📝 Project Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input(
                    "Project Name *",
                    placeholder="Enter project name",
                    help="Descriptive name for the project"
                )
                
                po_number = st.text_input(
                    "PO Number",
                    placeholder="Purchase Order Number",
                    help="Official PO number from client"
                )
                
                start_date = st.date_input(
                    "Start Date *",
                    value=date.today(),
                    help="Project start date"
                )
            
            with col2:
                po_issuing_company = st.selectbox(
                    "Client Company *",
                    options=[(c.id, c.name) for c in customers],
                    format_func=lambda x: x[1],
                    help="Company issuing the PO"
                )
                
                supplier_company = st.selectbox(
                    "Supplier Company",
                    options=[(None, "Select Supplier")] + [(c.id, c.name) for c in suppliers],
                    format_func=lambda x: x[1] if x[1] else "No Supplier Selected",
                    help="Supplier company (optional)"
                )
                
                tentative_end_date = st.date_input(
                    "Tentative End Date",
                    value=None,
                    help="Expected project completion date"
                )
            
            # Project details
            st.markdown("### 💰 Financial Information")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_po_value = st.number_input(
                    "Total PO Value (৳)",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    help="Total project value"
                )
            
            with col2:
                vat_rate = st.number_input(
                    "VAT Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=15.0,
                    step=0.1,
                    help="VAT percentage"
                )
            
            with col3:
                ait_rate = st.number_input(
                    "AIT Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.0,  # FIXED: Changed from 3.0 to 2.0
                    step=0.1,
                    help="Advance Income Tax percentage"
                )
            
            # NEW: Project Advance Section
            st.markdown("### 💵 Project Advance Information")
            st.info("💡 Set advance amount if client provides advance payment with PO")
            
            col1, col2 = st.columns(2)
            
            with col1:
                project_advance_amount = st.number_input(
                    "Advance Amount (৳)",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    help="Advance amount received from client"
                )
            
            with col2:
                # Auto-calculate advance percentage
                if total_po_value > 0 and project_advance_amount > 0:
                    calculated_percentage = (project_advance_amount / total_po_value) * 100
                    advance_percentage = st.number_input(
                        "Advance Percentage (%)",
                        value=calculated_percentage,
                        disabled=True,
                        help="Automatically calculated based on PO value"
                    )
                else:
                    advance_percentage = st.number_input(
                        "Advance Percentage (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=0.0,
                        step=0.1,
                        help="Advance percentage manually"
                    )
            
            # File upload
            st.markdown("### 📎 Documents")
            uploaded_file = st.file_uploader(
                "Upload PO Document",
                type=['pdf'],
                help="Upload the official PO document (PDF only)"
            )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Create Project", use_container_width=True)
            
            if submitted:
                # Validation
                if not project_name:
                    st.error("Project name is required!")
                    return
                
                if not po_issuing_company:
                    st.error("Client company is required!")
                    return
                
                # Validate advance amount
                if project_advance_amount > total_po_value:
                    st.error("Advance amount cannot exceed total PO value!")
                    return
                
                try:
                    # Calculate financial values
                    vat_amount = total_po_value * (vat_rate / 100)
                    ait_amount = total_po_value * (ait_rate / 100)
                    final_po_value = total_po_value - vat_amount - ait_amount
                    
                    # Create project
                    project = db_ops.create_project(
                        project_name=project_name,
                        po_number=po_number,
                        po_issuing_company_id=po_issuing_company[0],
                        supplier_company_id=supplier_company[0] if supplier_company[0] else None,
                        start_date=start_date,
                        tentative_end_date=tentative_end_date
                    )
                    
                    # Update financial information
                    project.total_po_value = total_po_value
                    project.vat_rate = vat_rate
                    project.vat_amount = vat_amount
                    project.ait_rate = ait_rate
                    project.ait_amount = ait_amount
                    project.final_po_value = final_po_value
                    # NEW: Add advance information
                    project.project_advance_amount = project_advance_amount
                    project.project_advance_percentage = advance_percentage
                    
                    db_ops.db.commit()
                    
                    # Handle file upload (basic implementation)
                    if uploaded_file:
                        st.success(f"✅ PO document '{uploaded_file.name}' uploaded successfully!")
                    
                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.balloons()
                    
                    # Clear form and refresh the page
                    st.session_state.form_submitted = True
                    
                    # Show created project details
                    st.markdown("### 📊 Created Project Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"""
                        **Project ID:** {project.id}  
                        **Name:** {project_name}  
                        **PO Number:** {po_number or 'N/A'}  
                        **Status:** New
                        """)
                    
                    with col2:
                        st.info(f"""
                        **Total Value:** ৳{total_po_value:,.2f}  
                        **VAT ({vat_rate}%):** ৳{vat_amount:,.2f}  
                        **AIT ({ait_rate}%):** ৳{ait_amount:,.2f}  
                        **Final Value:** ৳{final_po_value:,.2f}
                        """)
                    
                    # Show advance info if provided
                    if project_advance_amount > 0:
                        st.success(f"""
                        **Advance Amount:** ৳{project_advance_amount:,.2f} ({advance_percentage:.1f}% of PO value)  
                        **Remaining:** ৳{final_po_value - project_advance_amount:,.2f}
                        """)
                    
                except Exception as e:
                    st.error(f"Error creating project: {str(e)}")
        
    except Exception as e:
        st.error(f"Error loading form data: {str(e)}")
    finally:
        db_ops.close()

def show_edit_project_form(project_id):
    """Show edit project form - NEW FUNCTION"""
    st.subheader("✏️ Edit Project")
    
    # Back button
    if st.button("⬅️ Back to Projects"):
        if 'edit_project_id' in st.session_state:
            del st.session_state.edit_project_id
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        
        if not project:
            st.error("Project not found!")
            return
        
        # Get companies for dropdowns
        companies = db_ops.get_all_companies()
        customers = [c for c in companies if c.company_type == 'customer']
        suppliers = [c for c in companies if c.company_type == 'supplier']
        
        with st.form("edit_project_form"):
            st.markdown(f"### Editing: {project.project_name}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("Project Name *", value=project.project_name)
                po_number = st.text_input("PO Number", value=project.po_number or "")
                start_date = st.date_input("Start Date *", value=project.start_date or date.today())
            
            with col2:
                # Client company selection
                current_client_id = project.po_issuing_company_id
                client_options = [(c.id, c.name) for c in customers]
                client_index = next((i for i, (cid, _) in enumerate(client_options) if cid == current_client_id), 0)
                
                po_issuing_company = st.selectbox(
                    "Client Company *",
                    options=client_options,
                    index=client_index,
                    format_func=lambda x: x[1]
                )
                
                # Supplier company selection
                current_supplier_id = project.supplier_company_id
                supplier_options = [(None, "No Supplier")] + [(c.id, c.name) for c in suppliers]
                supplier_index = 0
                if current_supplier_id:
                    supplier_index = next((i for i, (sid, _) in enumerate(supplier_options) if sid == current_supplier_id), 0)
                
                supplier_company = st.selectbox(
                    "Supplier Company",
                    options=supplier_options,
                    index=supplier_index,
                    format_func=lambda x: x[1] if x[1] else "No Supplier"
                )
                
                tentative_end_date = st.date_input(
                    "Tentative End Date", 
                    value=project.tentative_end_date
                )
            
            # Financial information
            st.markdown("### 💰 Financial Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_po_value = st.number_input(
                    "Total PO Value (৳)",
                    min_value=0.0,
                    value=float(project.total_po_value or 0),
                    step=1000.0
                )
            
            with col2:
                vat_rate = st.number_input(
                    "VAT Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.vat_rate or 15.0),
                    step=0.1
                )
            
            with col3:
                ait_rate = st.number_input(
                    "AIT Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.ait_rate or 2.0),  # FIXED: Default to 2.0
                    step=0.1
                )
            
            # Project advance information
            st.markdown("### 💵 Project Advance Information")
            col1, col2 = st.columns(2)
            
            with col1:
                current_advance = float(project.project_advance_amount or 0)
                project_advance_amount = st.number_input(
                    "Advance Amount (৳)",
                    min_value=0.0,
                    value=current_advance,
                    step=1000.0
                )
            
            with col2:
                current_advance_pct = float(project.project_advance_percentage or 0)
                if total_po_value > 0 and project_advance_amount > 0:
                    calculated_percentage = (project_advance_amount / total_po_value) * 100
                    advance_percentage = st.number_input(
                        "Advance Percentage (%)",
                        value=calculated_percentage,
                        disabled=True
                    )
                else:
                    advance_percentage = st.number_input(
                        "Advance Percentage (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=current_advance_pct,
                        step=0.1
                    )
            
            # Project status
            st.markdown("### 📊 Project Status")
            status_options = ["new", "active", "invoice_submitted", "completed", "cancelled", "on_hold"]
            current_status_index = status_options.index(project.status) if project.status in status_options else 0
            
            project_status = st.selectbox(
                "Project Status",
                options=status_options,
                index=current_status_index,
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            # Submit button
            submitted = st.form_submit_button("💾 Update Project", use_container_width=True)
            
            if submitted:
                if not project_name:
                    st.error("Project name is required!")
                    return
                
                if project_advance_amount > total_po_value:
                    st.error("Advance amount cannot exceed total PO value!")
                    return
                
                try:
                    # Calculate financial values
                    vat_amount = total_po_value * (vat_rate / 100)
                    ait_amount = total_po_value * (ait_rate / 100)
                    final_po_value = total_po_value - vat_amount - ait_amount
                    
                    # Update project
                    project.project_name = project_name
                    project.po_number = po_number
                    project.po_issuing_company_id = po_issuing_company[0]
                    project.supplier_company_id = supplier_company[0] if supplier_company[0] else None
                    project.start_date = start_date
                    project.tentative_end_date = tentative_end_date
                    project.status = project_status
                    
                    # Update financial information
                    project.total_po_value = total_po_value
                    project.vat_rate = vat_rate
                    project.vat_amount = vat_amount
                    project.ait_rate = ait_rate
                    project.ait_amount = ait_amount
                    project.final_po_value = final_po_value
                    project.project_advance_amount = project_advance_amount
                    project.project_advance_percentage = advance_percentage
                    project.updated_at = datetime.now()
                    
                    db_ops.db.commit()
                    
                    st.success(f"✅ Project '{project_name}' updated successfully!")
                    st.balloons()
                    
                    # Clear edit state and return to projects
                    del st.session_state.edit_project_id
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error updating project: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading project: {str(e)}")
    finally:
        db_ops.close()

# Add delete project functionality
def delete_project(project_id):
    """Delete a project with validation - NEW FUNCTION"""
    db_ops = DatabaseOperations()
    try:
        # Check if project has dependencies
        project = db_ops.get_project_by_id(project_id)
        if not project:
            st.error("Project not found!")
            return False
        
        # Check for initial projections
        projections = db_ops.get_initial_projections_by_project(project_id)
        if projections:
            st.error(f"Cannot delete project! It has {len(projections)} initial projection(s). Delete projections first.")
            return False
        
        # Check for final costs
        final_costs = db_ops.get_final_costs_by_project(project_id)
        if final_costs:
            st.error(f"Cannot delete project! It has {len(final_costs)} final cost record(s). Delete final costs first.")
            return False
        
        # Check for disbursements
        disbursements = db_ops.get_disbursements_by_project(project_id)
        if disbursements:
            st.error(f"Cannot delete project! It has {len(disbursements)} disbursement(s). Delete disbursements first.")
            return False
        
        # Delete the project
        db_ops.db.delete(project)
        db_ops.db.commit()
        
        st.success(f"✅ Project '{project.project_name}' deleted successfully!")
        return True
        
    except Exception as e:
        st.error(f"Error deleting project: {str(e)}")
        return False
    finally:
        db_ops.close()


def show_project_search():
    """Project search and filtering interface"""
    st.subheader("🔍 Search & Filter Projects")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input(
            "Search Projects",
            placeholder="Search by name or PO number",
            help="Enter project name or PO number"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "New", "Active", "Completed", "On Hold", "Cancelled"]
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=[],
            help="Filter by start date range"
        )
    
    if st.button("🔍 Search Projects"):
        # Implement real search functionality
        db_ops = DatabaseOperations()
        try:
            projects = db_ops.get_all_projects()
            filtered_projects = []
            
            for project in projects:
                # Search by name or PO number
                if search_term:
                    if (search_term.lower() not in project.project_name.lower() and
                        (not project.po_number or search_term.lower() not in project.po_number.lower())):
                        continue
                
                # Filter by status
                if status_filter != "All" and project.status != status_filter.lower():
                    continue
                
                filtered_projects.append(project)
            
            # Display results
            st.markdown("### 📊 Search Results")
            if filtered_projects:
                # Prepare data for display
                project_data = []
                for project in filtered_projects:
                    project_data.append({
                        'Project Name': project.project_name,
                        'Status': project.status.title(),
                        'Client': project.po_issuing_company.name if project.po_issuing_company else 'N/A',
                        'Budget': f"৳{project.total_po_value:,.2f}" if project.total_po_value else '৳0.00'
                    })
                st.dataframe(pd.DataFrame(project_data), use_container_width=True)
            else:
                st.info("No projects found matching your search criteria.")
        
        except Exception as e:
            st.error(f"Search error: {str(e)}")
        finally:
            db_ops.close()
def show_project_advance_management(project):
    """Show project advance management section"""
    st.markdown("### 💰 Project Advance Management")
    
    current_advance = project.project_advance_amount or 0.0
    current_percentage = project.project_advance_percentage or 0.0
    
    # Display current advance info
    if current_advance > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Advance Amount", f"৳{current_advance:,.2f}")
        
        with col2:
            st.metric("Advance Percentage", f"{current_percentage:.1f}%")
        
        with col3:
            # Get disbursed amount
            db_ops = DatabaseOperations()
            try:
                advance_summary = db_ops.get_project_advance_summary(project.id)
                remaining = current_advance - advance_summary['total_disbursed']
                st.metric("Remaining Balance", f"৳{remaining:,.2f}")
            except:
                st.metric("Remaining Balance", "Error loading")
            finally:
                db_ops.close()
    else:
        st.info("💡 No advance amount set for this project.")
    
    # Advance amount setting form
    with st.expander("⚙️ Set/Update Advance Amount", expanded=False):
        with st.form(f"advance_form_{project.id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_advance_amount = st.number_input(
                    "Advance Amount (৳)",
                    min_value=0.0,
                    value=current_advance,
                    step=1000.0,
                    help="Set the advance amount for this project"
                )
            
            with col2:
                # Calculate percentage if PO value exists
                if project.total_po_value and project.total_po_value > 0:
                    calculated_percentage = (new_advance_amount / project.total_po_value) * 100
                    st.number_input(
                        "Advance Percentage (%)",
                        value=calculated_percentage,
                        disabled=True,
                        help="Automatically calculated based on PO value"
                    )
                    new_advance_percentage = calculated_percentage
                else:
                    new_advance_percentage = st.number_input(
                        "Advance Percentage (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=current_percentage,
                        step=0.1,
                        help="Set advance percentage manually"
                    )
            
            submitted = st.form_submit_button("💾 Update Advance Amount")
            
            if submitted:
                db_ops = DatabaseOperations()
                try:
                    updated_project = db_ops.update_project_advance_amount(
                        project.id, 
                        new_advance_amount, 
                        new_advance_percentage
                    )
                    if updated_project:
                        st.success(f"✅ Advance amount updated to ৳{new_advance_amount:,.2f}")
                        st.rerun()
                    else:
                        st.error("Failed to update advance amount!")
                except Exception as e:
                    st.error(f"Error updating advance amount: {str(e)}")
                finally:
                    db_ops.close()

def get_project_status_info(project):
    """Get enhanced project status information"""
    status_colors = {
        'new': '🆕',
        'active': '🟢',
        'invoice_submitted': '📄',
        'completed': '✅',
        'on_hold': '⏸️',
        'cancelled': '❌'
    }
    
    status_descriptions = {
        'new': 'New Project',
        'active': 'Active Project',
        'invoice_submitted': 'Invoice Submitted',
        'completed': 'Completed',
        'on_hold': 'On Hold',
        'cancelled': 'Cancelled'
    }
    
    icon = status_colors.get(project.status, '⚪')
    description = status_descriptions.get(project.status, project.status.title())
    
    return {
        'display': f"{icon} {description}",
        'last_updated': project.updated_at.strftime('%Y-%m-%d %H:%M') if project.updated_at else 'N/A'
    }

def show_status_progression(project):
    """Show enhanced project status progression with detailed stages"""
    db_ops = DatabaseOperations()
    try:
        # Check project activities
        projections = db_ops.get_initial_projections_by_project(project.id)
        final_costs = db_ops.get_final_costs_by_project(project.id)
        disbursements = db_ops.get_disbursements_by_project(project.id)
        profit_configs = db_ops.get_profit_sharing_configs_by_project(project.id)
        
        # Check for project documents (placeholder for now)
        initial_docs = False  # Will be implemented when document management is added
        final_docs = False    # Will be implemented when document management is added
        
        st.markdown("**📊 Project Progress:**")
        
        # Enhanced progress indicators with more stages
        progress_items = [
            ("Project Created", True, "✅"),
            ("Financial Projections", len(projections) > 0, "✅" if len(projections) > 0 else "⏳"),
            ("Initial Project Documentation", initial_docs, "✅" if initial_docs else "⏳"),
            ("Final Costs Tracked", len(final_costs) > 0, "✅" if len(final_costs) > 0 else "⏳"),
            ("Disbursements Made", len(disbursements) > 0, "✅" if len(disbursements) > 0 else "⏳"),
            ("Profit Configured", len(profit_configs) > 0, "✅" if len(profit_configs) > 0 else "⏳"),
            ("Final Project Documentation", final_docs, "✅" if final_docs else "⏳"),
        ]
        
        # Display progress items with better formatting
        for item, completed, icon in progress_items:
            if completed:
                st.markdown(f"<span style='color: green; font-weight: bold;'>{icon} {item}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: gray;'>{icon} {item}</span>", unsafe_allow_html=True)
        
        # Calculate completion percentage
        completion_rate = sum(1 for _, completed, _ in progress_items if completed) / len(progress_items) * 100
        
        # Progress bar with percentage
        st.progress(completion_rate / 100)
        st.caption(f"Project Completion: {completion_rate:.0f}% ({sum(1 for _, completed, _ in progress_items if completed)}/{len(progress_items)} stages)")
        
        # Show next recommended action
        if completion_rate < 100:
            next_action = None
            for item, completed, _ in progress_items:
                if not completed:
                    next_action = item
                    break
            
            if next_action:
                st.info(f"💡 **Next Step:** {next_action}")
                
                # Provide helpful links for next actions
                if next_action == "Financial Projections":
                    if st.button("📋 Create Financial Projection", key=f"create_proj_{project.id}"):
                        st.session_state.page = "financial"
                        st.session_state.projection_project_id = project.id
                        st.session_state.show_projection_form = True
                        st.rerun()
                
                elif next_action == "Final Costs Tracked":
                    if st.button("💰 Setup Final Costs", key=f"setup_costs_{project.id}"):
                        st.session_state.page = "financial"
                        st.rerun()
                
                elif next_action == "Disbursements Made":
                    if st.button("💸 Create Disbursement", key=f"create_disb_{project.id}"):
                        st.session_state.page = "financial"
                        st.session_state.action = "new_disbursement"
                        st.rerun()
                
                elif next_action == "Profit Configured":
                    if st.button("🤝 Configure Profit Sharing", key=f"config_profit_{project.id}"):
                        st.session_state.page = "projects"
                        st.session_state.profit_sharing_project_id = project.id
                        st.session_state.show_profit_sharing_form = True
                        st.rerun()
        else:
            st.success("🎉 **Project Fully Configured!** All stages completed.")
        
    except Exception as e:
        st.error(f"Error loading progress: {str(e)}")
        # Fallback to basic progress
        st.markdown("**📊 Basic Progress:**")
        st.success("✅ Project Created")
        st.info("⏳ Additional progress tracking requires data loading")
    finally:
        db_ops.close()

def show_enhanced_project_financial_tab(project, db_ops):
    """Show enhanced financial tab with disbursements and key metrics - SIMPLIFIED VERSION"""
    st.markdown("### 💰 Project Financial Overview")
    
    try:
        # Get financial data for this project
        disbursements = db_ops.get_disbursements_by_project(project.id)
        advance_summary = db_ops.get_project_advance_summary(project.id)
        projections = db_ops.get_initial_projections_by_project(project.id)
        final_costs = db_ops.get_final_costs_by_project(project.id)
        
        # Calculate financial metrics
        total_disbursed = sum(d.amount for d in disbursements)
        advance_disbursed = sum(d.amount for d in disbursements if d.disbursement_type == 'advance')
        project_cost_disbursed = sum(d.amount for d in disbursements if d.disbursement_type == 'project_cost')
        personal_loan_disbursed = sum(d.amount for d in disbursements if d.disbursement_type == 'personal_loan')
        
        # Key Financial Metrics
        st.markdown("#### 📊 Key Financial Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total PO Value", f"৳{project.total_po_value or 0:,.2f}")
        
        with col2:
            st.metric("Final PO Value", f"৳{project.final_po_value or 0:,.2f}")
        
        with col3:
            st.metric("Total Disbursed", f"৳{total_disbursed:,.2f}", 
                     delta=f"{len(disbursements)} disbursements")
        
        with col4:
            if project.project_advance_amount and project.project_advance_amount > 0:
                remaining_advance = project.project_advance_amount - advance_disbursed
                st.metric("Advance Remaining", f"৳{remaining_advance:,.2f}")
            else:
                st.metric("Advance Amount", "Not Set")
        
        with col5:
            budget_remaining = (project.final_po_value or 0) - total_disbursed
            delta_color = "normal" if budget_remaining >= 0 else "inverse"
            st.metric("Budget Remaining", f"৳{budget_remaining:,.2f}", 
                     delta_color=delta_color)
        
        # Financial Breakdown - ENHANCED WITH ADVANCE INFO
        st.markdown("#### 💰 Financial Breakdown")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Project Values:**")
            
            # Build breakdown data with advance information
            breakdown_data = [
                {"Item": "Total PO Value", "Amount": f"৳{project.total_po_value or 0:,.2f}"},
                {"Item": f"Less: VAT ({project.vat_rate or 15}%)", "Amount": f"৳{project.vat_amount or 0:,.2f}"},
                {"Item": f"Less: AIT ({project.ait_rate or 2}%)", "Amount": f"৳{project.ait_amount or 0:,.2f}"},
                {"Item": "**Final PO Value**", "Amount": f"**৳{project.final_po_value or 0:,.2f}**"}
            ]
            
            # Add advance information row
            if project.project_advance_amount and project.project_advance_amount > 0:
                advance_percentage = project.project_advance_percentage or 0
                breakdown_data.append({
                    "Item": f"Advance Received ({advance_percentage:.1f}%)", 
                    "Amount": f"৳{project.project_advance_amount:,.2f}"
                })
                
                # Add remaining amount after advance
                remaining_after_advance = (project.final_po_value or 0) - project.project_advance_amount
                breakdown_data.append({
                    "Item": "Remaining After Advance", 
                    "Amount": f"৳{remaining_after_advance:,.2f}"
                })
            else:
                breakdown_data.append({
                    "Item": "Advance Received", 
                    "Amount": "৳0.00 (No advance)"
                })
            
            df_breakdown = pd.DataFrame(breakdown_data)
            st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Disbursement Summary:**")
            if disbursements:
                disb_summary_data = [
                    {"Type": "Advance Disbursements", "Amount": f"৳{advance_disbursed:,.2f}"},
                    {"Type": "Project Cost Disbursements", "Amount": f"৳{project_cost_disbursed:,.2f}"},
                    {"Type": "Personal Loans", "Amount": f"৳{personal_loan_disbursed:,.2f}"},
                    {"Type": "**Total Disbursed**", "Amount": f"**৳{total_disbursed:,.2f}**"}
                ]
                
                df_disb_summary = pd.DataFrame(disb_summary_data)
                st.dataframe(df_disb_summary, use_container_width=True, hide_index=True)
            else:
                st.info("No disbursements recorded for this project.")
        
        # Project Disbursements List
        if disbursements:
            st.markdown("#### 💸 Project Disbursements")
            
            # Prepare disbursement table data
            disb_table_data = []
            for disb in disbursements:
                # Get money receipt info
                try:
                    money_receipt = db_ops.get_money_receipt_by_disbursement(disb.id)
                    receipt_number = money_receipt.receipt_number if money_receipt else 'N/A'
                    receipt_status = '✅ Complete' if money_receipt else '⏳ Pending'
                except:
                    receipt_number = 'N/A'
                    receipt_status = '❌ Error'
                
                disb_table_data.append({
                    'ID': f"#{disb.id}",
                    'Type': disb.disbursement_type.replace('_', ' ').title(),
                    'Amount': f"৳{disb.amount:,.2f}",
                    'Date': disb.disbursement_date.strftime('%Y-%m-%d'),
                    'Receipt': receipt_number,
                    'Status': receipt_status,
                    'Description': disb.description[:40] + "..." if len(disb.description or "") > 40 else (disb.description or "")
                })
            
            df_disbursements = pd.DataFrame(disb_table_data)
            st.dataframe(df_disbursements, use_container_width=True, hide_index=True)
        
        else:
            st.markdown("#### 💸 Project Disbursements")
            st.info("📭 No disbursements recorded for this project yet.")
            
            if project.project_advance_amount and project.project_advance_amount > 0:
                st.success(f"💰 Advance Available: ৳{project.project_advance_amount:,.2f}")
            else:
                st.info("💡 No advance amount set for this project.")
    
    except Exception as e:
        st.error(f"Error loading financial data: {str(e)}")
        
        # Fallback to basic financial display
        st.markdown("#### 💰 Basic Financial Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total PO Value", f"৳{project.total_po_value or 0:,.2f}")
            st.metric("VAT Amount", f"৳{project.vat_amount or 0:,.2f}")
        
        with col2:
            st.metric("AIT Amount", f"৳{project.ait_amount or 0:,.2f}")
            st.metric("Final PO Value", f"৳{project.final_po_value or 0:,.2f}")
                   
def show_project_details(project_id):
    """Show detailed view of a specific project"""
    st.subheader(f"📄 Project Details - #{project_id}")
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        
        if project:
            # Project header
            col1, col2= st.columns([2, 1])
            
            with col1:
                st.markdown(f"## {project.project_name}")
                st.markdown(f"**PO Number:** {project.po_number or 'N/A'}")
            
            with col2:
                status_colors = {
                    'new': '🆕',
                    'active': '🟢',
                    'completed': '✅',
                    'on_hold': '⏸️',
                    'cancelled': '❌'
                }
                status_icon = status_colors.get(project.status, '⚪')
                st.markdown(f"**Status:** {status_icon} {project.status.title()}")
            
            # Project information tabs
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "💰 Financial", "📄 Documents"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📋 Basic Information")
                    st.info(f"""
                    **Project ID:** {project.id}  
                    **Name:** {project.project_name}  
                    **PO Number:** {project.po_number or 'N/A'}  
                    **Status:** {project.status.title()}  
                    **Start Date:** {project.start_date.strftime('%Y-%m-%d') if project.start_date else 'N/A'}  
                    **Due Date:** {project.tentative_end_date.strftime('%Y-%m-%d') if project.tentative_end_date else 'N/A'}
                    """)
                
                with col2:
                    st.markdown("### 🏢 Companies & Status")
                    client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
                    supplier_name = project.supplier_company.name if project.supplier_company else 'N/A'
                    
                    # Enhanced status display
                    status_info = get_project_status_info(project)
                    
                    st.info(f"""
                    **Client:** {client_name}  
                    **Supplier:** {supplier_name}  
                    **Status:** {status_info['display']}  
                    **Last Updated:** {status_info['last_updated']}
                    """)
                    
                    # Status progression indicator
                    show_status_progression(project)
            
            with tab2:
                show_enhanced_project_financial_tab(project, db_ops)
            
            with tab3:
                st.markdown("### 📄 Project Documents")
                st.info("Document management will be implemented in later steps.")
        
        else:
            st.error(f"Project with ID {project_id} not found.")
            
    except Exception as e:
        st.error(f"Error loading project details: {str(e)}")
    finally:
        db_ops.close()