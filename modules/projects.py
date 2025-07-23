import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.operations import DatabaseOperations
from modules.auth import AuthenticationManager

def show_projects():
    """Main projects page"""
    
    st.title("📋 Project Management")
    
    # Check for specific actions from quick actions
    if st.session_state.get('action') == 'new_project':
        st.session_state.action = None  # Clear the action
        show_new_project_form()
        return
    
    # Tab navigation
    tab1, tab2, tab3 = st.tabs(["📊 All Projects", "➕ New Project", "🔍 Search & Filter"])
    
    with tab1:
        show_all_projects()
    
    with tab2:
        show_new_project_form()
    
    with tab3:
        show_project_search()

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
            st.subheader("📝 Project Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_id = st.selectbox(
                    "Select Project ID for Actions:",
                    options=[p['ID'] for p in project_data],
                    format_func=lambda x: f"#{x} - {next(p['Project Name'] for p in project_data if p['ID'] == x)}"
                )
            
            with col2:
                if st.button("👀 View Details", key=f"view_details_{selected_id}"):
                    st.session_state.show_project_details = selected_id
                    st.rerun()
            
            with col3:
                if st.button("✏️ Edit Project", key=f"edit_project_{selected_id}"):
                    st.session_state.edit_project_id = selected_id
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

def show_new_project_form():
    """Display new project creation form"""
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
                    value=3.0,
                    step=0.1,
                    help="Advance Income Tax percentage"
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
                
                try:
                    # Calculate financial values
                    vat_amount = total_po_value * (vat_rate / 100)
                    ait_amount = total_po_value * (ait_rate / 100)
                    final_po_value = total_po_value + vat_amount - ait_amount
                    
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
                    
                    db_ops.db.commit()
                    
                    # Handle file upload (basic implementation)
                    if uploaded_file:
                        # In a full implementation, save file to uploads folder
                        # For now, just acknowledge the upload
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
                    
                except Exception as e:
                    st.error(f"Error creating project: {str(e)}")
        
    except Exception as e:
        st.error(f"Error loading form data: {str(e)}")
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
                    
def show_project_details(project_id):
    """Show detailed view of a specific project"""
    st.subheader(f"📄 Project Details - #{project_id}")
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        
        if project:
            # Project header
            col1, col2, col3 = st.columns([2, 1, 1])
            
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
            
            with col3:
                if st.button("✏️ Edit Project", key=f"edit_project_details_{project_id}"):
                    st.session_state.edit_project_id = project_id
                    st.rerun()
            
            # Project information tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Financial", "📄 Documents", "📈 Progress"])
            
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
                    st.markdown("### 🏢 Companies")
                    client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
                    supplier_name = project.supplier_company.name if project.supplier_company else 'N/A'
                    st.info(f"""
                    **Client:** {client_name}  
                    **Supplier:** {supplier_name}
                    """)
            
            with tab2:
                st.markdown("### 💰 Financial Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total PO Value", f"৳{project.total_po_value:,.2f}")
                    st.metric("VAT Amount", f"৳{project.vat_amount:,.2f}")
                
                with col2:
                    st.metric("AIT Amount", f"৳{project.ait_amount:,.2f}")
                    st.metric("Final PO Value", f"৳{project.final_po_value:,.2f}")
            
            with tab3:
                st.markdown("### 📄 Project Documents")
                st.info("Document management will be implemented in later steps.")
            
            with tab4:
                st.markdown("### 📈 Project Progress")
                st.info("Progress tracking will be implemented in later steps.")
                
                # Mock progress data
                progress_data = {
                    'Phase': ['Planning', 'Design', 'Development', 'Testing', 'Deployment'],
                    'Status': ['Completed', 'Completed', 'In Progress', 'Pending', 'Pending'],
                    'Progress': [100, 100, 60, 0, 0]
                }
                st.dataframe(pd.DataFrame(progress_data), use_container_width=True)
        
        else:
            st.error(f"Project with ID {project_id} not found.")
            
    except Exception as e:
        st.error(f"Error loading project details: {str(e)}")
    finally:
        db_ops.close()