import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.operations import DatabaseOperations
from modules.auth import AuthenticationManager

def show_financial():
    """Main financial management page"""
    
    st.title("💰 Financial Management")
    
    user = AuthenticationManager.get_current_user()
    
    # Check for specific actions from quick actions
    if st.session_state.get('action') == 'new_disbursement':
        st.session_state.action = None  # Clear the action
        show_disbursement_management()
        return
    
    # Different interfaces based on user role
    if user['role'] == 'finance':
        # Finance users see limited interface
        show_finance_user_interface()
    elif user['role'] in ['admin', 'user']:
        # Admin and regular users see full interface
        show_full_financial_interface()
    else:
        st.error("Access denied. Insufficient permissions.")

def show_full_financial_interface():
    """Full financial interface for admin and regular users"""
    
    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Financial Overview", 
        "📋 Initial Projections", 
        "💸 Disbursements",
        "📈 Financial Reports"
    ])
    
    with tab1:
        show_financial_overview()
    
    with tab2:
        show_initial_projections()
    
    with tab3:
        show_disbursement_management()
    
    with tab4:
        show_financial_reports()

def show_finance_user_interface():
    """Limited interface for finance users"""
    
    st.info("🔒 **Finance User Access**: You can view and edit Initial Financial Projections and Final Financial Cost (real cost column only).")
    
    # Tab navigation for finance users
    tab1, tab2 = st.tabs(["📋 Initial Projections", "💰 Final Costs"])
    
    with tab1:
        show_initial_projections()
    
    with tab2:
        show_final_costs_finance_view()

def show_financial_overview():
    """Show financial overview dashboard"""
    st.subheader("📊 Financial Overview")
    
    # Get financial data
    financial_data = get_financial_overview_data()
    
    if not financial_data['has_data']:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;">
            <h3>📊 Welcome to Financial Management!</h3>
            <p style="color: #6c757d;">No financial projections found. Start by creating projections for your existing projects.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show available projects
        db_ops = DatabaseOperations()
        try:
            projects = db_ops.get_all_projects()
            if projects:
                st.info(f"💼 You have {len(projects)} project(s) available for financial projection.")
                if st.button("📋 Create Financial Projections", use_container_width=True):
                    # Go directly to projections tab instead of showing confusing button
                    st.session_state.financial_tab = "projections"
                    st.rerun()
            else:
                st.warning("⚠️ No projects found. You need to create projects first before making financial projections.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📋 Go to Projects", use_container_width=True):
                        st.session_state.page = "projects"
                        st.rerun()
                with col2:
                    if st.button("🏢 Manage Companies", use_container_width=True):
                        st.session_state.page = "settings"
                        st.rerun()
        except Exception as e:
            st.error(f"Error loading projects: {str(e)}")
        finally:
            db_ops.close()
        return
    
    # Financial KPIs
    show_financial_kpis(financial_data)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        show_project_budget_chart(financial_data)
    
    with col2:
        show_disbursement_chart(financial_data)
    
    # Project financial summary table
    show_project_financial_summary(financial_data)

def show_initial_projections():
    """Show initial financial projections management"""
    st.subheader("📋 Initial Financial Projections")
    
    # Handle projection form display
    if st.session_state.get('show_projection_form'):
        show_projection_form()
        return
    
    # Handle editing
    if st.session_state.get('edit_projection_id'):
        show_edit_projection_form(st.session_state.edit_projection_id)
        return
    
    # Project selection and projection management
    show_projection_management()

def show_projection_management():
    """Show projection management interface"""
    
    # Get projects for selection
    db_ops = DatabaseOperations()
    try:
        projects = db_ops.get_all_projects()
        
        if not projects:
            st.warning("⚠️ No projects found. Please create a project first.")
            
            user = AuthenticationManager.get_current_user()
            if user['role'] in ['admin', 'user']:  # Only show if user can access projects
                if st.button("📋 Go to Projects"):
                    st.session_state.page = "projects"
                    st.rerun()
            else:
                st.info("🔒 Contact an admin or regular user to create projects.")
            return
        
        # Filter projects that don't have projections yet
        projects_with_projections = []
        projects_without_projections = []
        
        for project in projects:
            projections = db_ops.get_initial_projections_by_project(project.id)
            if projections:
                projects_with_projections.append((project, projections))
            else:
                projects_without_projections.append(project)
        
        # New projection section
        if projects_without_projections:
            st.markdown("### ➕ Create New Projection")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_project = st.selectbox(
                    "Select Project for New Projection:",
                    options=[(p.id, f"{p.project_name} (PO: {p.po_number or 'N/A'})") for p in projects_without_projections],
                    format_func=lambda x: x[1]
                )
            
            with col2:
                if st.button("📋 Create Projection", use_container_width=True):
                    st.session_state.projection_project_id = selected_project[0]
                    st.session_state.show_projection_form = True
                    st.rerun()
        
        # Existing projections
        if projects_with_projections:
            st.markdown("### 📊 Existing Projections")
            
            for project, projections in projects_with_projections:
                with st.expander(f"💼 {project.project_name} - {len(projections)} line items"):
                    
                    # Project info
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
                        st.info(f"""
                        **Project:** {project.project_name}  
                        **Client:** {client_name}  
                        **PO:** {project.po_number or 'N/A'}  
                        **Status:** {project.status.title()}
                        """)
                    
                    with col2:
                        total_projection = sum(p.amount for p in projections)
                        st.metric("Total Projection", f"৳{total_projection:,.2f}")
                        st.metric("Line Items", len(projections))
                        
                        # Budget comparison
                        if project.total_po_value and project.total_po_value > 0:
                            percentage = (total_projection / project.total_po_value) * 100
                            if percentage > 100:
                                st.warning(f"⚠️ {percentage:.1f}% of budget")
                            else:
                                st.success(f"✅ {percentage:.1f}% of budget")
                    
                    with col3:
                        if st.button("✏️ Edit Projection", key=f"edit_proj_{project.id}"):
                            st.session_state.edit_projection_id = project.id
                            st.rerun()
                        
                        if st.button("🗑️ Delete Projection", key=f"del_proj_{project.id}"):
                            st.session_state.delete_projection_id = project.id
                            st.rerun()
                    
                    # Projection summary table
                    proj_data = []
                    for proj in projections:
                        proj_data.append({
                            'SL': proj.sl_no,
                            'Particulars': proj.particulars,
                            'Days': proj.days,
                            'Qty': proj.qty,
                            'Unit Price': f"৳{proj.unit_price:,.2f}",
                            'Amount': f"৳{proj.amount:,.2f}"
                        })
                    
                    if proj_data:
                        df = pd.DataFrame(proj_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Handle delete confirmation
        if st.session_state.get('delete_projection_id'):
            project_to_delete = next((p for p in projects if p.id == st.session_state.delete_projection_id), None)
            if project_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete the projection for '{project_to_delete.project_name}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", key="confirm_proj_delete"):
                        delete_projection(st.session_state.delete_projection_id)
                with col2:
                    if st.button("❌ Cancel", key="cancel_proj_delete"):
                        del st.session_state.delete_projection_id
                        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading projections: {str(e)}")
    finally:
        db_ops.close()

def show_projection_form():
    """Show new projection creation form"""
    st.subheader("📋 Create Initial Financial Projection")
    
    # Back button
    if st.button("⬅️ Back to Projections"):
        del st.session_state.show_projection_form
        if 'projection_project_id' in st.session_state:
            del st.session_state.projection_project_id
        st.rerun()
    
    # Get selected project
    project_id = st.session_state.get('projection_project_id')
    if not project_id:
        st.error("No project selected!")
        return
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        if not project:
            st.error("Project not found!")
            return
        
        # Project information
        st.markdown(f"### 💼 Project: {project.project_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**PO Number:** {project.po_number or 'N/A'}")
        with col2:
            client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
            st.info(f"**Client:** {client_name}")
        
        # Dynamic projection form
        st.markdown("### 📊 Financial Projection Details")
        
        # Initialize projection items in session state
        if 'projection_items' not in st.session_state:
            st.session_state.projection_items = [
                {'sl_no': 1, 'particulars': '', 'days': 0.0, 'qty': 0.0, 'unit_price': 0.0, 'amount': 0.0}
            ]
        
        # Display projection items
        show_projection_items_form()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add Line Item", use_container_width=True):
                add_projection_item()
        
        with col2:
            if st.button("💾 Save Projection", use_container_width=True):
                save_projection(project_id)
        
        with col3:
            if st.button("🔄 Reset Form", use_container_width=True):
                reset_projection_form()
        
        # Show total
        total_amount = sum(item['amount'] for item in st.session_state.projection_items)
        st.markdown(f"### 💰 **Total Projection: ৳{total_amount:,.2f}**")
        
        # Budget comparison
        if project.total_po_value and total_amount > 0:
            percentage = (total_amount / project.total_po_value) * 100
            if percentage > 100:
                st.warning(f"⚠️ Projection exceeds PO value by {percentage - 100:.1f}%")
            else:
                st.success(f"✅ Projection is {percentage:.1f}% of PO value")
    
    except Exception as e:
        st.error(f"Error creating projection: {str(e)}")
    finally:
        db_ops.close()

def show_projection_items_form():
    """Show dynamic projection items form"""
    
    for i, item in enumerate(st.session_state.projection_items):
        with st.container():
            st.markdown(f"#### Line Item {item['sl_no']}")
            
            col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 1, 1, 1.5, 1])
            
            with col1:
                st.text_input("SL", value=item['sl_no'], disabled=True, key=f"sl_{i}")
            
            with col2:
                particulars = st.text_input(
                    "Particulars *", 
                    value=item['particulars'],
                    placeholder="Description of work/item",
                    key=f"particulars_{i}"
                )
                st.session_state.projection_items[i]['particulars'] = particulars
            
            with col3:
                days = st.number_input(
                    "Days", 
                    min_value=0.0, 
                    value=item['days'],
                    step=0.5,
                    key=f"days_{i}"
                )
                st.session_state.projection_items[i]['days'] = days
            
            with col4:
                qty = st.number_input(
                    "Qty", 
                    min_value=0.0, 
                    value=item['qty'],
                    step=1.0,
                    key=f"qty_{i}"
                )
                st.session_state.projection_items[i]['qty'] = qty
            
            with col5:
                unit_price = st.number_input(
                    "Unit Price (৳)", 
                    min_value=0.0, 
                    value=item['unit_price'],
                    step=100.0,
                    key=f"unit_price_{i}"
                )
                st.session_state.projection_items[i]['unit_price'] = unit_price
            
            with col6:
                # Calculate amount automatically
                amount = days * qty * unit_price
                st.session_state.projection_items[i]['amount'] = amount
                st.metric("Amount", f"৳{amount:,.2f}")
                
                # Remove button for items after the first one
                if len(st.session_state.projection_items) > 1:
                    if st.button("🗑️", key=f"remove_{i}", help="Remove this item"):
                        remove_projection_item(i)
                        st.rerun()
            
            st.markdown("---")

def add_projection_item():
    """Add a new projection item"""
    next_sl = len(st.session_state.projection_items) + 1
    st.session_state.projection_items.append({
        'sl_no': next_sl,
        'particulars': '',
        'days': 0.0,
        'qty': 0.0,
        'unit_price': 0.0,
        'amount': 0.0
    })
    st.rerun()

def remove_projection_item(index):
    """Remove a projection item"""
    if len(st.session_state.projection_items) > 1:
        st.session_state.projection_items.pop(index)
        # Renumber remaining items
        for i, item in enumerate(st.session_state.projection_items):
            item['sl_no'] = i + 1

def reset_projection_form():
    """Reset the projection form"""
    st.session_state.projection_items = [
        {'sl_no': 1, 'particulars': '', 'days': 0.0, 'qty': 0.0, 'unit_price': 0.0, 'amount': 0.0}
    ]
    st.rerun()

def save_projection(project_id):
    """Save the projection to database"""
    
    # Validate form
    valid_items = []
    for item in st.session_state.projection_items:
        if item['particulars'].strip():  # At least particulars should be filled
            valid_items.append(item)
    
    if not valid_items:
        st.error("❌ Please add at least one item with particulars!")
        return
    
    db_ops = DatabaseOperations()
    try:
        # Save each item
        for item in valid_items:
            db_ops.create_initial_projection(
                project_id=project_id,
                sl_no=item['sl_no'],
                particulars=item['particulars'],
                days=item['days'],
                qty=item['qty'],
                unit_price=item['unit_price'],
                amount=item['amount']
            )
        
        st.success(f"✅ Projection saved successfully! {len(valid_items)} items created.")
        st.balloons()
        
        # Clear form and return to management
        del st.session_state.show_projection_form
        del st.session_state.projection_items
        if 'projection_project_id' in st.session_state:
            del st.session_state.projection_project_id
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error saving projection: {str(e)}")
    finally:
        db_ops.close()

def show_edit_projection_form(project_id):
    """Show edit projection form"""
    st.subheader("✏️ Edit Financial Projection")
    
    # Back button
    if st.button("⬅️ Back to Projections"):
        del st.session_state.edit_projection_id
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        projections = db_ops.get_initial_projections_by_project(project_id)
        
        if not project or not projections:
            st.error("Project or projections not found!")
            return
        
        # Project info
        st.markdown(f"### 💼 Editing: {project.project_name}")
        
        st.info("📝 **Note:** This will replace the existing projection. Use 'Add Line Item' and 'Remove' buttons to modify.")
        
        # Load existing items into session state
        if 'edit_projection_items' not in st.session_state:
            st.session_state.edit_projection_items = []
            for proj in projections:
                st.session_state.edit_projection_items.append({
                    'id': proj.id,
                    'sl_no': proj.sl_no,
                    'particulars': proj.particulars,
                    'days': proj.days,
                    'qty': proj.qty,
                    'unit_price': proj.unit_price,
                    'amount': proj.amount
                })
        
        # Show editable items
        show_edit_projection_items_form()
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Item", use_container_width=True):
                add_edit_projection_item()
        
        with col2:
            if st.button("💾 Update Projection", use_container_width=True):
                update_projection(project_id)
        
        with col3:
            if st.button("🔄 Reset Changes", use_container_width=True):
                del st.session_state.edit_projection_items
                st.rerun()
        
        with col4:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state.edit_projection_id
                if 'edit_projection_items' in st.session_state:
                    del st.session_state.edit_projection_items
                st.rerun()
        
        # Show total
        total_amount = sum(item['amount'] for item in st.session_state.edit_projection_items)
        st.markdown(f"### 💰 **Total Projection: ৳{total_amount:,.2f}**")
        
    except Exception as e:
        st.error(f"Error editing projection: {str(e)}")
    finally:
        db_ops.close()

def show_edit_projection_items_form():
    """Show editable projection items form"""
    
    for i, item in enumerate(st.session_state.edit_projection_items):
        with st.container():
            st.markdown(f"#### Line Item {item['sl_no']}")
            
            col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 1, 1, 1.5, 1])
            
            with col1:
                st.text_input("SL", value=item['sl_no'], disabled=True, key=f"edit_sl_{i}")
            
            with col2:
                particulars = st.text_input(
                    "Particulars *", 
                    value=item['particulars'],
                    key=f"edit_particulars_{i}"
                )
                st.session_state.edit_projection_items[i]['particulars'] = particulars
            
            with col3:
                days = st.number_input(
                    "Days", 
                    min_value=0.0, 
                    value=item['days'],
                    step=0.5,
                    key=f"edit_days_{i}"
                )
                st.session_state.edit_projection_items[i]['days'] = days
            
            with col4:
                qty = st.number_input(
                    "Qty", 
                    min_value=0.0, 
                    value=item['qty'],
                    step=1.0,
                    key=f"edit_qty_{i}"
                )
                st.session_state.edit_projection_items[i]['qty'] = qty
            
            with col5:
                unit_price = st.number_input(
                    "Unit Price (৳)", 
                    min_value=0.0, 
                    value=item['unit_price'],
                    step=100.0,
                    key=f"edit_unit_price_{i}"
                )
                st.session_state.edit_projection_items[i]['unit_price'] = unit_price
            
            with col6:
                # Calculate amount automatically
                amount = days * qty * unit_price
                st.session_state.edit_projection_items[i]['amount'] = amount
                st.metric("Amount", f"৳{amount:,.2f}")
                
                # Remove button
                if len(st.session_state.edit_projection_items) > 1:
                    if st.button("🗑️", key=f"edit_remove_{i}", help="Remove this item"):
                        remove_edit_projection_item(i)
                        st.rerun()
            
            st.markdown("---")

def add_edit_projection_item():
    """Add a new item to edit projection"""
    next_sl = len(st.session_state.edit_projection_items) + 1
    st.session_state.edit_projection_items.append({
        'id': None,  # New item
        'sl_no': next_sl,
        'particulars': '',
        'days': 0.0,
        'qty': 0.0,
        'unit_price': 0.0,
        'amount': 0.0
    })
    st.rerun()

def remove_edit_projection_item(index):
    """Remove an item from edit projection"""
    if len(st.session_state.edit_projection_items) > 1:
        st.session_state.edit_projection_items.pop(index)
        # Renumber remaining items
        for i, item in enumerate(st.session_state.edit_projection_items):
            item['sl_no'] = i + 1

def update_projection(project_id):
    """Update the projection in database"""
    
    # Validate form
    valid_items = []
    for item in st.session_state.edit_projection_items:
        if item['particulars'].strip():
            valid_items.append(item)
    
    if not valid_items:
        st.error("❌ Please have at least one item with particulars!")
        return
    
    db_ops = DatabaseOperations()
    try:
        # Delete existing projections
        db_ops.delete_initial_projections_by_project(project_id)
        
        # Create new projections
        for item in valid_items:
            db_ops.create_initial_projection(
                project_id=project_id,
                sl_no=item['sl_no'],
                particulars=item['particulars'],
                days=item['days'],
                qty=item['qty'],
                unit_price=item['unit_price'],
                amount=item['amount']
            )
        
        st.success(f"✅ Projection updated successfully! {len(valid_items)} items saved.")
        
        # Clear form and return
        del st.session_state.edit_projection_id
        del st.session_state.edit_projection_items
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error updating projection: {str(e)}")
    finally:
        db_ops.close()

def delete_projection(project_id):
    """Delete a projection"""
    db_ops = DatabaseOperations()
    try:
        if db_ops.delete_initial_projections_by_project(project_id):
            st.success("✅ Projection deleted successfully!")
            if 'delete_projection_id' in st.session_state:
                del st.session_state.delete_projection_id
            st.rerun()
        else:
            st.error("Failed to delete projection!")
    except Exception as e:
        st.error(f"Error deleting projection: {str(e)}")
    finally:
        db_ops.close()

# Placeholder functions for other tabs

def show_disbursement_management():
    """Enhanced disbursement management with three types"""
    st.subheader("💸 Disbursement Management")
    
    # Handle disbursement form display
    if st.session_state.get('show_disbursement_form'):
        show_disbursement_form()
        return
    
    # Handle edit disbursement
    if st.session_state.get('edit_disbursement_id'):
        show_edit_disbursement_form(st.session_state.edit_disbursement_id)
        return
    
    # Disbursement overview
    show_disbursement_overview()

def show_disbursement_overview():
    """Show disbursement overview and management"""
    
    # Get disbursement statistics
    disbursement_stats = get_disbursement_statistics()
    
    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Disbursements", 
            disbursement_stats['total_count'],
            delta=f"৳{disbursement_stats['total_amount']:,.0f}"
        )
    
    with col2:
        st.metric(
            "Advance Disbursements", 
            disbursement_stats['advance_count'],
            delta=f"৳{disbursement_stats['advance_amount']:,.0f}"
        )
    
    with col3:
        st.metric(
            "Project Cost", 
            disbursement_stats['project_cost_count'],
            delta=f"৳{disbursement_stats['project_cost_amount']:,.0f}"
        )
    
    with col4:
        st.metric(
            "Personal Loans", 
            disbursement_stats['personal_loan_count'],
            delta=f"৳{disbursement_stats['personal_loan_amount']:,.0f}"
        )
    
    # Action buttons
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("➕ New Disbursement", use_container_width=True):
            st.session_state.show_disbursement_form = True
            st.rerun()
    
    with col2:
        # Filter options
        filter_type = st.selectbox(
            "Filter by Type:", 
            ["All", "advance", "project_cost", "personal_loan"],
            format_func=lambda x: "All Types" if x == "All" else x.replace("_", " ").title()
        )
    
    # Disbursements table
    show_disbursements_table(filter_type)

def show_disbursement_form():
    """Show new disbursement creation form with advance tracking"""
    st.subheader("💸 Create New Disbursement")
    
    # Back button
    if st.button("⬅️ Back to Disbursements"):
        del st.session_state.show_disbursement_form
        st.rerun()
    
    with st.form("new_disbursement_form"):
        st.markdown("### 📋 Disbursement Information")
        
        # Disbursement Type Selection
        col1, col2 = st.columns(2)
        
        with col1:
            disbursement_type = st.radio(
                "Disbursement Type *",
                ["advance", "project_cost", "personal_loan"],
                format_func=lambda x: {
                    "advance": "💰 Advance Disbursement (From collected advance)",
                    "project_cost": "💼 Project Cost Disbursement (Direct project expenses)",
                    "personal_loan": "👤 Personal Loan (Excluded from profit calculation)"
                }[x],
                help="Select the type of disbursement"
            )
        
        with col2:
            # Project selection (not needed for personal loans)
            if disbursement_type != "personal_loan":
                projects = get_projects_for_disbursement()
                if not projects:
                    st.error("❌ No projects available for disbursement!")
                    st.stop()
                
                selected_project = st.selectbox(
                    "Select Project *",
                    options=[(p.id, f"{p.project_name} (PO: {p.po_number or 'N/A'})") for p in projects],
                    format_func=lambda x: x[1]
                )
                project_id = selected_project[0]
                
                # Show advance information for advance disbursements
                if disbursement_type == "advance":
                    show_advance_info(project_id)
            else:
                project_id = None
                st.info("💡 Personal loans are not linked to specific projects")
        
        # Amount and date/time
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "Amount (৳) *",
                min_value=1.0,
                step=100.0,
                help="Disbursement amount in BDT"
            )
        
        with col2:
            disbursement_date = st.date_input(
                "Disbursement Date *",
                value=date.today(),
                help="Date when the disbursement was made"
            )
            
            disbursement_time = st.time_input(
                "Disbursement Time *",
                value=datetime.now().time(),
                help="Time when the disbursement was made"
            )
        
        # Description and recipient details
        description = st.text_area(
            "Description/Purpose *",
            placeholder="Describe the purpose of this disbursement",
            help="Detailed description of what this disbursement is for"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            received_from = st.text_input(
                "Received From *",
                placeholder="Company/Person giving the money",
                help="Who is providing this money (for money receipt)"
            )
        
        with col2:
            received_by = st.text_input(
                "Received By *",
                placeholder="Person receiving the money",
                help="Who is receiving this money (for money receipt)"
            )
        
        # Submit button
        submitted = st.form_submit_button("💸 Create Disbursement & Generate Receipt", use_container_width=True)
        
        if submitted:
            # Validation
            if not amount or amount <= 0:
                st.error("❌ Please enter a valid amount!")
                return
            
            if not description.strip():
                st.error("❌ Please provide a description!")
                return
            
            if not received_from.strip() or not received_by.strip():
                st.error("❌ Please provide both 'Received From' and 'Received By' information!")
                return
            
            if disbursement_type != "personal_loan" and not project_id:
                st.error("❌ Please select a project!")
                return
            
            # Validate advance disbursement
            if disbursement_type == "advance" and project_id:
                validation_result = validate_advance_disbursement(project_id, amount)
                if not validation_result['valid']:
                    st.error(validation_result['message'])
                    return
            
            # Combine date and time
            disbursement_datetime = datetime.combine(disbursement_date, disbursement_time)
            
            # Create disbursement
            create_disbursement(
                project_id=project_id,
                disbursement_type=disbursement_type,
                amount=amount,
                disbursement_date=disbursement_datetime,
                description=description,
                received_from=received_from,
                received_by=received_by
            )

def show_advance_info(project_id):
    """Show advance information for a project"""
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        if project:
            advance_info = db_ops.get_project_advance_summary(project_id)
            
            if project.project_advance_amount and project.project_advance_amount > 0:
                st.markdown("#### 💰 Advance Information")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Advance", f"৳{project.project_advance_amount:,.2f}")
                
                with col2:
                    st.metric("Disbursed", f"৳{advance_info['total_disbursed']:,.2f}")
                
                with col3:
                    remaining = project.project_advance_amount - advance_info['total_disbursed']
                    st.metric("Remaining", f"৳{remaining:,.2f}")
                
                if remaining <= 0:
                    st.warning("⚠️ No advance amount remaining for disbursement!")
                elif remaining < 10000:
                    st.warning(f"⚠️ Low advance balance: ৳{remaining:,.2f}")
                else:
                    st.success(f"✅ Available for disbursement: ৳{remaining:,.2f}")
            else:
                st.info("ℹ️ No advance amount set for this project. You can set advance amount in project settings.")
    except Exception as e:
        st.error(f"Error loading advance info: {str(e)}")
    finally:
        db_ops.close()

def validate_advance_disbursement(project_id, amount):
    """Validate advance disbursement against available balance"""
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        if not project:
            return {'valid': False, 'message': 'Project not found!'}
        
        if not project.project_advance_amount or project.project_advance_amount <= 0:
            return {'valid': False, 'message': 'No advance amount set for this project!'}
        
        advance_info = db_ops.get_project_advance_summary(project_id)
        remaining_advance = project.project_advance_amount - advance_info['total_disbursed']
        
        if amount > remaining_advance:
            return {
                'valid': False, 
                'message': f'Insufficient advance balance! Available: ৳{remaining_advance:,.2f}, Requested: ৳{amount:,.2f}'
            }
        
        return {'valid': True, 'message': 'Valid advance disbursement'}
        
    except Exception as e:
        return {'valid': False, 'message': f'Validation error: {str(e)}'}
    finally:
        db_ops.close()
        
def create_disbursement(project_id, disbursement_type, amount, disbursement_date, 
                       description, received_from, received_by):
    """Create disbursement and auto-generate money receipt"""
    
    db_ops = DatabaseOperations()
    user = AuthenticationManager.get_current_user()
    
    try:
        # Create disbursement
        disbursement = db_ops.create_disbursement(
            project_id=project_id,
            disbursement_type=disbursement_type,
            amount=amount,
            disbursement_date=disbursement_date,
            description=description,
            created_by=user['id']
        )
        
        # Generate unique receipt number
        receipt_number = generate_receipt_number(disbursement.id)
        
        # Create money receipt
        money_receipt = db_ops.create_money_receipt(
            project_id=project_id,
            disbursement_id=disbursement.id,
            receipt_number=receipt_number,
            amount=amount,
            received_from=received_from,
            received_by=received_by,
            receipt_date=disbursement_date.date()
        )
        
        st.success(f"✅ Disbursement created successfully!")
        st.success(f"📄 Money Receipt #{receipt_number} generated automatically!")
        st.balloons()
        
        # Show disbursement summary
        show_disbursement_summary(disbursement, money_receipt)
        
        # Clear form and return
        del st.session_state.show_disbursement_form
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error creating disbursement: {str(e)}")
    finally:
        db_ops.close()

def show_disbursement_summary(disbursement, money_receipt):
    """Show summary of created disbursement - FIXED VERSION"""
    st.markdown("### 📊 Disbursement Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Disbursement ID:** #{disbursement.id}  
        **Type:** {disbursement.disbursement_type.replace('_', ' ').title()}  
        **Amount:** ৳{disbursement.amount:,.2f}  
        **Date:** {disbursement.disbursement_date.strftime('%Y-%m-%d %H:%M')}
        """)
    
    with col2:
        st.info(f"""
        **Receipt Number:** {money_receipt.receipt_number}  
        **Received From:** {money_receipt.received_from}  
        **Received By:** {money_receipt.received_by}  
        **Receipt Date:** {money_receipt.receipt_date.strftime('%Y-%m-%d')}
        """)
    
    # Move action buttons OUTSIDE the form context
    st.markdown("### 📄 Receipt Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download Receipt PDF", key=f"download_summary_{money_receipt.id}"):
            generate_receipt_pdf(money_receipt)
    
    with col2:
        if st.button("✉️ Email Receipt", key=f"email_summary_{money_receipt.id}"):
            st.info("Email functionality will be implemented in later phases.")
    
    with col3:
        if st.button("🖨️ Print Receipt", key=f"print_summary_{money_receipt.id}"):
            st.info("Print functionality will be implemented in later phases.")

def show_disbursements_table(filter_type="All"):
    """Show disbursements table with enhanced filtering - FIXED VERSION"""
    st.markdown("### 📋 Recent Disbursements")
    
    # Enhanced filtering options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Project filter
        db_ops = DatabaseOperations()
        try:
            projects = db_ops.get_projects_for_disbursement()
            project_options = [("All", "All Projects")] + [(p.id, p.project_name) for p in projects]
            selected_project = st.selectbox(
                "Filter by Project:",
                options=project_options,
                format_func=lambda x: x[1]
            )
            project_filter = selected_project[0] if selected_project[0] != "All" else None
        except:
            project_filter = None
        finally:
            db_ops.close()
    
    with col2:
        # Date range filter
        date_filter = st.selectbox(
            "Filter by Date:",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
        )
    
    with col3:
        # Amount range filter
        amount_filter = st.selectbox(
            "Filter by Amount:",
            ["All Amounts", "< ৳10,000", "৳10,000 - ৳50,000", "> ৳50,000"]
        )
    
    db_ops = DatabaseOperations()
    try:
        disbursements = db_ops.get_disbursements_with_receipts_filtered(
            type_filter=filter_type,
            project_filter=project_filter,
            date_filter=date_filter,
            amount_filter=amount_filter
        )
        
        if not disbursements:
            st.info("📭 No disbursements found matching the filters.")
            return
        
        # Prepare table data
        table_data = []
        for disb, receipt in disbursements:
            if disb.disbursement_type == "personal_loan":
                project_name = "Personal Loan"
            else:
                project_name = disb.project.project_name if disb.project else "Unknown Project"
            
            table_data.append({
                'ID': f"#{disb.id}",
                'Type': disb.disbursement_type.replace('_', ' ').title(),
                'Project': project_name,
                'Amount': f"৳{disb.amount:,.2f}",
                'Date': disb.disbursement_date.strftime('%Y-%m-%d'),
                'Receipt': receipt.receipt_number if receipt else 'N/A',
                'Status': '✅ Complete' if receipt else '⏳ Pending'
            })
        
        df = pd.DataFrame(table_data)
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Action section
        if disbursements:
            st.markdown("### 📝 Disbursement Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                selected_disbursement = st.selectbox(
                    "Select Disbursement:",
                    options=[disb.id for disb, receipt in disbursements],
                    format_func=lambda x: f"#{x} - ৳{next(disb.amount for disb, receipt in disbursements if disb.id == x):,.2f}"
                )
            
            with col2:
                if st.button("👀 View Details", key="view_details_table"):
                    show_disbursement_details(selected_disbursement)
            
            with col3:
                if st.button("📄 Download Receipt", key="download_receipt_table"):
                    # Find the receipt for selected disbursement
                    selected_receipt = next((receipt for disb, receipt in disbursements if disb.id == selected_disbursement and receipt), None)
                    if selected_receipt:
                        generate_receipt_pdf(selected_receipt)
                    else:
                        st.error("No receipt found for this disbursement!")
            
            with col4:
                if st.button("✏️ Edit Disbursement", key="edit_disbursement_table"):
                    st.session_state.edit_disbursement_id = selected_disbursement
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading disbursements: {str(e)}")
    finally:
        db_ops.close()

def show_disbursement_details(disbursement_id):
    """Show detailed view of a disbursement"""
    st.markdown(f"### 📄 Disbursement Details - #{disbursement_id}")
    
    db_ops = DatabaseOperations()
    try:
        disbursement = db_ops.get_disbursement_by_id(disbursement_id)
        money_receipt = db_ops.get_money_receipt_by_disbursement(disbursement_id)
        
        if not disbursement:
            st.error("Disbursement not found!")
            return
        
        # Disbursement information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💸 Disbursement Information")
            project_name = "Personal Loan" if not disbursement.project else disbursement.project.project_name
            
            st.info(f"""
            **ID:** #{disbursement.id}  
            **Type:** {disbursement.disbursement_type.replace('_', ' ').title()}  
            **Project:** {project_name}  
            **Amount:** ৳{disbursement.amount:,.2f}  
            **Date:** {disbursement.disbursement_date.strftime('%Y-%m-%d %H:%M')}  
            **Description:** {disbursement.description}
            """)
        
        with col2:
            if money_receipt:
                st.markdown("#### 📄 Money Receipt Information")
                st.info(f"""
                **Receipt Number:** {money_receipt.receipt_number}  
                **Amount:** ৳{money_receipt.amount:,.2f}  
                **Received From:** {money_receipt.received_from}  
                **Received By:** {money_receipt.received_by}  
                **Receipt Date:** {money_receipt.receipt_date.strftime('%Y-%m-%d')}
                """)
                
                # Receipt actions
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📄 Download PDF", key=f"download_{disbursement_id}"):
                        generate_receipt_pdf(money_receipt)
                with col_b:
                    if st.button("🖨️ Print", key=f"print_{disbursement_id}"):
                        st.info("Print functionality coming soon.")
            else:
                st.warning("⚠️ No money receipt found for this disbursement.")
    
    except Exception as e:
        st.error(f"Error loading disbursement details: {str(e)}")
    finally:
        db_ops.close()

def get_projects_for_disbursement():
    """Get projects available for disbursement"""
    db_ops = DatabaseOperations()
    try:
        # Get projects that are not cancelled
        projects = db_ops.get_projects_for_disbursement()
        return projects
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
        return []
    finally:
        db_ops.close()

def get_disbursement_statistics():
    """Get disbursement statistics"""
    db_ops = DatabaseOperations()
    try:
        stats = db_ops.get_disbursement_statistics()
        return stats
    except Exception as e:
        return {
            'total_count': 0, 'total_amount': 0,
            'advance_count': 0, 'advance_amount': 0,
            'project_cost_count': 0, 'project_cost_amount': 0,
            'personal_loan_count': 0, 'personal_loan_amount': 0
        }
    finally:
        db_ops.close()

def generate_receipt_number(disbursement_id):
    """Generate unique receipt number"""
    from datetime import datetime
    
    # Format: MR-YYYYMMDD-ID (e.g., MR-20250724-001)
    date_str = datetime.now().strftime('%Y%m%d')
    receipt_number = f"MR-{date_str}-{disbursement_id:03d}"
    
    return receipt_number

def generate_receipt_pdf(money_receipt):
    """Generate PDF for money receipt - FIXED VERSION"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        import io
        import base64
        
        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredText(width/2, height - 80, "MONEY RECEIPT")
        
        # Receipt details
        p.setFont("Helvetica", 12)
        y = height - 150
        
        details = [
            f"Receipt No: {money_receipt.receipt_number}",
            f"Date: {money_receipt.receipt_date.strftime('%B %d, %Y')}",
            f"Amount: ৳{money_receipt.amount:,.2f}",
            f"Received From: {money_receipt.received_from}",
            f"Received By: {money_receipt.received_by}",
        ]
        
        for detail in details:
            p.drawString(100, y, detail)
            y -= 25
        
        # Amount in words (simplified)
        p.drawString(100, y - 20, f"Amount in Words: {amount_to_words(money_receipt.amount)} Taka Only")
        
        # Signature section
        y = 200
        p.drawString(100, y, "Received By: _________________")
        p.drawString(400, y, "Authorized By: _________________")
        
        p.drawString(100, y - 40, "Signature")
        p.drawString(400, y - 40, "Signature")
        
        # Footer
        p.setFont("Helvetica-Oblique", 10)
        p.drawCentredText(width/2, 50, "This is a computer generated receipt.")
        
        p.save()
        
        # Prepare download
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        # Create download link
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="receipt_{money_receipt.receipt_number}.pdf">📄 Click here to download Receipt PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ PDF generated successfully! Click the link above to download.")
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        st.info("💡 PDF generation requires the reportlab library. Make sure it's installed.")

def amount_to_words(amount):
    """Convert amount to words (simplified version)"""
    # This is a simplified version
    return f"Rupees {int(amount)}"

def show_edit_disbursement_form(disbursement_id):
    """Show edit disbursement form"""
    st.subheader("✏️ Edit Disbursement")
    st.info("Edit disbursement functionality will be implemented in next phase.")
    
    if st.button("⬅️ Back to Disbursements"):
        del st.session_state.edit_disbursement_id
        st.rerun()

def show_final_costs_finance_view():
    """Placeholder for final costs (finance view)"""
    st.subheader("💰 Final Financial Cost")
    st.info("Final cost management will be implemented in upcoming steps.")

def show_financial_reports():
    """Placeholder for financial reports"""
    st.subheader("📈 Financial Reports")
    st.info("Financial reporting will be implemented in upcoming steps.")

def get_financial_overview_data():
    """Get financial overview data"""
    db_ops = DatabaseOperations()
    try:
        financial_stats = db_ops.get_all_financial_projections_summary()
        has_data = financial_stats['total_projection_items'] > 0
        return {'has_data': has_data, 'stats': financial_stats}
    except Exception as e:
        return {'has_data': False, 'stats': {}}
    finally:
        db_ops.close()

def show_financial_kpis(data):
    """Show financial KPIs"""
    pass

def show_project_budget_chart(data):
    """Show project budget chart"""
    pass

def show_disbursement_chart(data):
    """Show disbursement chart"""
    pass

def show_project_financial_summary(data):
    """Show project financial summary"""
    pass