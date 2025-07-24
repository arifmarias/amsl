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
    
    # Tab navigation - UPDATED with Final Costs tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Financial Overview", 
        "📋 Initial Projections", 
        "💰 Final Costs",  # NEW TAB
        "💸 Disbursements",
        "📈 Financial Reports"
    ])
    
    with tab1:
        show_financial_overview()
    
    with tab2:
        show_initial_projections()
    
    with tab3:
        show_final_costs()  # NEW TAB CONTENT
    
    with tab4:
        show_disbursement_management()
    
    with tab5:
        show_financial_reports()

def show_finance_user_interface():
    """Limited interface for finance users"""
    
    st.info("🔒 **Finance User Access**: You can view and edit Initial Financial Projections and Final Financial Cost (real cost column only).")
    
    # Tab navigation for finance users - UPDATED
    tab1, tab2 = st.tabs(["📋 Initial Projections", "💰 Final Costs"])
    
    with tab1:
        show_initial_projections()
    
    with tab2:
        show_final_costs()  # Finance users can access final costs

def show_financial_overview():
    """Show financial overview dashboard with final costs integration"""
    st.subheader("📊 Financial Overview")
    
    # Get financial data including final costs
    financial_data = get_enhanced_financial_overview_data()
    
    if not financial_data['has_data']:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;">
            <h3>📊 Welcome to Financial Management!</h3>
            <p style="color: #6c757d;">No financial data found. Start by creating projections for your existing projects.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced Financial KPIs
    show_enhanced_financial_kpis(financial_data)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        show_cost_tracking_chart(financial_data)
    
    with col2:
        show_variance_summary_chart(financial_data)
    
    # Project financial summary table
    show_enhanced_project_financial_summary(financial_data)

def get_enhanced_financial_overview_data():
    """Get enhanced financial overview data including final costs"""
    db_ops = DatabaseOperations()
    try:
        projection_stats = db_ops.get_all_financial_projections_summary()
        final_cost_stats = db_ops.get_final_cost_summary()
        
        has_data = (projection_stats['total_projection_items'] > 0 or 
                   final_cost_stats['total_cost_items'] > 0)
        
        return {
            'has_data': has_data,
            'projection_stats': projection_stats,
            'final_cost_stats': final_cost_stats
        }
    except Exception as e:
        return {'has_data': False, 'projection_stats': {}, 'final_cost_stats': {}}
    finally:
        db_ops.close()

def show_enhanced_financial_kpis(data):
    """Show enhanced financial KPIs including variance metrics"""
    st.markdown("### 💰 Financial Performance Metrics")
    
    proj_stats = data['projection_stats']
    cost_stats = data['final_cost_stats']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Projections",
            f"৳{proj_stats.get('total_projection_amount', 0):,.0f}",
            delta=f"{proj_stats.get('projects_with_projections', 0)} projects"
        )
    
    with col2:
        st.metric(
            "Actual Costs",
            f"৳{cost_stats.get('total_real_cost', 0):,.0f}",
            delta=f"{cost_stats.get('projects_with_costs', 0)} projects"
        )
    
    with col3:
        variance_amount = cost_stats.get('variance_amount', 0)
        variance_pct = cost_stats.get('variance_percentage', 0)
        delta_color = "inverse" if variance_amount > 0 else "normal"
        
        st.metric(
            "Cost Variance",
            f"৳{variance_amount:,.0f}",
            delta=f"{variance_pct:+.1f}%",
            delta_color=delta_color
        )
    
    with col4:
        total_projects = proj_stats.get('total_projects', 0)
        projects_with_costs = cost_stats.get('projects_with_costs', 0)
        cost_tracking_rate = (projects_with_costs / total_projects * 100) if total_projects > 0 else 0
        
        st.metric(
            "Cost Tracking",
            f"{cost_tracking_rate:.0f}%",
            delta=f"{projects_with_costs}/{total_projects} projects"
        )
    
    with col5:
        st.metric(
            "Line Items",
            f"{cost_stats.get('total_cost_items', 0)}",
            delta=f"{proj_stats.get('total_projection_items', 0)} projected"
        )

def show_cost_tracking_chart(data):
    """Show cost tracking progress chart"""
    st.subheader("📈 Cost Tracking Progress")
    
    try:
        # Placeholder for cost tracking chart
        st.info("Cost tracking visualization will be enhanced in the next step.")
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def show_variance_summary_chart(data):
    """Show variance summary chart"""
    st.subheader("📊 Variance Overview")
    
    try:
        # Placeholder for variance chart
        st.info("Variance visualization will be enhanced in the next step.")
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def show_enhanced_project_financial_summary(data):
    """Show enhanced project financial summary"""
    st.subheader("📋 Project Financial Summary")
    
    try:
        # Placeholder for enhanced summary
        st.info("Enhanced project summary will be implemented in the next step.")
    except Exception as e:
        st.error(f"Error loading summary: {str(e)}")


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
def show_created_disbursement_summary():
    """Show summary of just created disbursement - FIXED VERSION"""
    st.subheader("📊 Disbursement Created Successfully!")
    
    disbursement_info = st.session_state.disbursement_created['disbursement']
    receipt_info = st.session_state.disbursement_created['receipt']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💸 Disbursement Details")
        st.info(f"""
        **Disbursement ID:** #{disbursement_info['id']}  
        **Type:** {disbursement_info['type'].replace('_', ' ').title()}  
        **Amount:** ৳{disbursement_info['amount']:,.2f}  
        **Date:** {disbursement_info['date'].strftime('%Y-%m-%d %H:%M')}  
        **Description:** {disbursement_info['description']}
        """)
    
    with col2:
        st.markdown("### 📄 Money Receipt Details")
        st.info(f"""
        **Receipt Number:** {receipt_info['number']}  
        **Amount:** ৳{receipt_info['amount']:,.2f}  
        **Received From:** {receipt_info['received_from']}  
        **Received By:** {receipt_info['received_by']}  
        **Receipt Date:** {receipt_info['date'].strftime('%Y-%m-%d')}
        """)
    
    # Action buttons - FIXED: Use actual receipt ID instead of TempReceipt
    st.markdown("### 📋 Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Download Receipt PDF", use_container_width=True):
            # Get the actual money receipt from database
            db_ops = DatabaseOperations()
            try:
                money_receipt = db_ops.get_money_receipt_by_disbursement(disbursement_info['id'])
                if money_receipt:
                    generate_receipt_pdf(money_receipt)
                else:
                    st.error("Receipt not found!")
            except Exception as e:
                st.error(f"Error loading receipt: {str(e)}")
            finally:
                db_ops.close()
    
    with col2:
        if st.button("➕ Create Another", use_container_width=True):
            del st.session_state.disbursement_created
            st.session_state.show_disbursement_form = True
            st.rerun()
    
    with col3:
        if st.button("📋 View All Disbursements", use_container_width=True):
            del st.session_state.disbursement_created
            st.rerun()
    
    with col4:
        if st.button("🏠 Back to Financial", use_container_width=True):
            del st.session_state.disbursement_created
            st.rerun()
            
def show_disbursement_management():
    """Enhanced disbursement management with three types - FIXED VERSION"""
    st.subheader("💸 Disbursement Management")
    
    # Show disbursement summary if just created
    if st.session_state.get('disbursement_created'):
        show_created_disbursement_summary()
        return
    
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
    """Simplified disbursement creation form with dropdown company selection"""
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
        
        # Description
        description = st.text_area(
            "Description/Purpose *",
            placeholder="Describe the purpose of this disbursement",
            help="Detailed description of what this disbursement is for"
        )
        
        # Simplified Money Receipt Information
        st.markdown("### 💼 Money Receipt Information")
        
        if disbursement_type in ["advance", "project_cost"]:
            # For project disbursements: dropdown selection from all companies
            st.info("💡 Select companies from your company directory for both 'Received From' and 'Received By'.")
            
            # Get all companies for dropdown
            db_ops = DatabaseOperations()
            try:
                all_companies = db_ops.get_all_companies()
                company_options = [(c.id, f"{c.name} ({c.company_type.title()})") for c in all_companies]
            except Exception as e:
                st.error(f"Error loading companies: {str(e)}")
                company_options = []
            finally:
                db_ops.close()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Received From (Company):**")
                if company_options:
                    selected_from_company = st.selectbox(
                        "Select 'Received From' Company *",
                        options=[(None, "Select Company")] + company_options,
                        format_func=lambda x: x[1] if x[1] else "Select Company",
                        key="from_company_dropdown"
                    )
                    
                    if selected_from_company[0]:
                        # Get company details to show preview
                        try:
                            db_ops = DatabaseOperations()
                            from_company = db_ops.get_company_by_id(selected_from_company[0])
                            if from_company:
                                st.caption(f"📍 {from_company.address or 'No address'}")
                                st.caption(f"📞 {from_company.phone or 'No phone'}")
                            db_ops.close()
                        except:
                            pass
                else:
                    st.warning("No companies found. Please add companies first.")
                    selected_from_company = (None, None)
            
            with col2:
                st.markdown("**Received By (Company):**")
                if company_options:
                    selected_by_company = st.selectbox(
                        "Select 'Received By' Company *",
                        options=[(None, "Select Company")] + company_options,
                        format_func=lambda x: x[1] if x[1] else "Select Company",
                        key="by_company_dropdown"
                    )
                    
                    if selected_by_company[0]:
                        # Get company details to show preview
                        try:
                            db_ops = DatabaseOperations()
                            by_company = db_ops.get_company_by_id(selected_by_company[0])
                            if by_company:
                                st.caption(f"📍 {by_company.address or 'No address'}")
                                st.caption(f"📞 {by_company.phone or 'No phone'}")
                            db_ops.close()
                        except:
                            pass
                else:
                    st.warning("No companies found. Please add companies first.")
                    selected_by_company = (None, None)
            
            # Store the selected company IDs for later use
            received_from_company_id = selected_from_company[0] if selected_from_company[0] else None
            received_by_company_id = selected_by_company[0] if selected_by_company[0] else None
            
        else:  # Personal loan - manual text input only
            st.info("💡 For personal loans, manually enter any individual or company information.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Received From:**")
                received_from = st.text_input(
                    "Received From *",
                    placeholder="Company/Individual name",
                    help="Who is providing this money (can be any company or individual)",
                    key="personal_loan_from"
                )
                received_from_company_id = None
            
            with col2:
                st.markdown("**Received By:**")
                received_by = st.text_input(
                    "Received By *",
                    placeholder="Company/Individual name", 
                    help="Who is receiving this money (can be any company or individual)",
                    key="personal_loan_by"
                )
                received_by_company_id = None
        
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
            
            # Validate company selection for project disbursements
            if disbursement_type in ["advance", "project_cost"]:
                if not received_from_company_id:
                    st.error("❌ Please select a 'Received From' company!")
                    return
                if not received_by_company_id:
                    st.error("❌ Please select a 'Received By' company!")
                    return
            else:  # Personal loan
                if not received_from or not received_by:
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
            if disbursement_type in ["advance", "project_cost"]:
                create_disbursement_with_companies(
                    project_id=project_id,
                    disbursement_type=disbursement_type,
                    amount=amount,
                    disbursement_date=disbursement_datetime,
                    description=description,
                    received_from_company_id=received_from_company_id,
                    received_by_company_id=received_by_company_id
                )
            else:
                create_disbursement(
                    project_id=project_id,
                    disbursement_type=disbursement_type,
                    amount=amount,
                    disbursement_date=disbursement_datetime,
                    description=description,
                    received_from=received_from,
                    received_by=received_by
                )
                
def create_disbursement_with_companies(project_id, disbursement_type, amount, disbursement_date, 
                                     description, received_from_company_id, received_by_company_id):
    """Create disbursement with company IDs for better PDF generation"""
    
    db_ops = DatabaseOperations()
    user = AuthenticationManager.get_current_user()
    
    try:
        # Get company names for receipt
        from_company = db_ops.get_company_by_id(received_from_company_id)
        by_company = db_ops.get_company_by_id(received_by_company_id)
        
        received_from = from_company.name if from_company else "Unknown Company"
        received_by = by_company.name if by_company else "Unknown Company"
        
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
        st.success(f"📄 Professional Money Receipt #{receipt_number} generated!")
        st.balloons()
        
        # Store the disbursement and receipt info in session state
        st.session_state.disbursement_created = {
            'disbursement': {
                'id': disbursement.id,
                'type': disbursement.disbursement_type,
                'amount': disbursement.amount,
                'date': disbursement.disbursement_date,
                'description': disbursement.description
            },
            'receipt': {
                'number': money_receipt.receipt_number,
                'amount': money_receipt.amount,
                'received_from': money_receipt.received_from,
                'received_by': money_receipt.received_by,
                'date': money_receipt.receipt_date
            }
        }
        
        # Clear form and return
        del st.session_state.show_disbursement_form
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error creating disbursement: {str(e)}")
    finally:
        db_ops.close()
        
def create_disbursement_enhanced(project_id, disbursement_type, amount, disbursement_date, 
                               description, received_from, received_by, 
                               override_received_from=False, override_received_by=False):
    """Enhanced disbursement creation with company integration"""
    
    db_ops = DatabaseOperations()
    user = AuthenticationManager.get_current_user()
    
    try:
        # For project-related disbursements, prepare company info for receipt
        final_received_from = received_from
        final_received_by = received_by
        
        if disbursement_type in ["advance", "project_cost"] and project_id:
            project = db_ops.get_project_by_id(project_id)
            
            if not override_received_from and project and project.po_issuing_company:
                final_received_from = project.po_issuing_company.name
            
            if not override_received_by and project and project.supplier_company:
                final_received_by = project.supplier_company.name
        
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
        
        # Create money receipt with final company info
        money_receipt = db_ops.create_money_receipt(
            project_id=project_id,
            disbursement_id=disbursement.id,
            receipt_number=receipt_number,
            amount=amount,
            received_from=final_received_from,
            received_by=final_received_by,
            receipt_date=disbursement_date.date()
        )
        
        st.success(f"✅ Disbursement created successfully!")
        st.success(f"📄 Professional Money Receipt #{receipt_number} generated!")
        st.balloons()
        
        # Store the disbursement and receipt info in session state
        st.session_state.disbursement_created = {
            'disbursement': {
                'id': disbursement.id,
                'type': disbursement.disbursement_type,
                'amount': disbursement.amount,
                'date': disbursement.disbursement_date,
                'description': disbursement.description
            },
            'receipt': {
                'number': money_receipt.receipt_number,
                'amount': money_receipt.amount,
                'received_from': money_receipt.received_from,
                'received_by': money_receipt.received_by,
                'date': money_receipt.receipt_date
            }
        }
        
        # Clear form and return
        del st.session_state.show_disbursement_form
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error creating disbursement: {str(e)}")
    finally:
        db_ops.close()
        
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
    """Create disbursement and auto-generate money receipt - FIXED VERSION"""
    
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
        
        # Store the disbursement and receipt info in session state to show summary outside the form
        st.session_state.disbursement_created = {
            'disbursement': {
                'id': disbursement.id,
                'type': disbursement.disbursement_type,
                'amount': disbursement.amount,
                'date': disbursement.disbursement_date,
                'description': disbursement.description
            },
            'receipt': {
                'number': money_receipt.receipt_number,
                'amount': money_receipt.amount,
                'received_from': money_receipt.received_from,
                'received_by': money_receipt.received_by,
                'date': money_receipt.receipt_date
            }
        }
        
        # Clear form and return - this will trigger a rerun
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
# Add this function to modules/financial.py (at the end, before helper functions)

def show_final_costs():
    """Show final financial costs management"""
    st.subheader("💰 Final Financial Costs")
    
    user = AuthenticationManager.get_current_user()
    
    # Handle final cost form display
    if st.session_state.get('show_final_cost_form'):
        show_final_cost_form()
        return
    
    # Handle editing
    if st.session_state.get('edit_final_cost_id'):
        show_edit_final_cost_form(st.session_state.edit_final_cost_id)
        return
    
    # Final cost management
    show_final_cost_management()

def show_final_cost_management():
    """Show final cost management interface"""
    
    # Get projects for selection
    db_ops = DatabaseOperations()
    try:
        projects = db_ops.get_all_projects()
        
        if not projects:
            st.warning("⚠️ No projects found. Please create a project first.")
            return
        
        # Filter projects that have initial projections
        projects_with_projections = []
        projects_with_final_costs = []
        projects_without_projections = []
        
        for project in projects:
            projections = db_ops.get_initial_projections_by_project(project.id)
            final_costs = db_ops.get_final_costs_by_project(project.id)
            
            if projections:
                if final_costs:
                    projects_with_final_costs.append((project, projections, final_costs))
                else:
                    projects_with_projections.append((project, projections))
            else:
                projects_without_projections.append(project)
        
        # Show different sections based on project status
        
        # Section 1: Projects ready for final cost tracking
        if projects_with_projections:
            st.markdown("### 📋 Projects Ready for Final Cost Tracking")
            st.info("💡 These projects have initial projections and are ready for final cost tracking.")
            
            for project, projections in projects_with_projections:
                with st.expander(f"🚀 {project.project_name} - Ready for Final Costs"):
                    
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
                        st.metric("Initial Projection", f"৳{total_projection:,.2f}")
                        st.metric("Projection Items", len(projections))
                    
                    with col3:
                        if st.button("📊 Create Final Costs", key=f"create_final_{project.id}"):
                            # Copy initial projections to final costs
                            success, message = db_ops.copy_initial_to_final_costs(project.id)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        
        # Section 2: Projects with final costs (for editing)
        if projects_with_final_costs:
            st.markdown("### 💰 Projects with Final Costs")
            
            for project, projections, final_costs in projects_with_final_costs:
                with st.expander(f"💼 {project.project_name} - Final Cost Tracking"):
                    
                    # Calculate variance
                    initial_total = sum(p.amount for p in projections)
                    final_total = sum(f.real_cost for f in final_costs)
                    variance = final_total - initial_total
                    variance_pct = (variance / initial_total * 100) if initial_total > 0 else 0
                    
                    # Project summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Initial Projection", f"৳{initial_total:,.2f}")
                    
                    with col2:
                        st.metric("Actual Cost", f"৳{final_total:,.2f}")
                    
                    with col3:
                        delta_color = "inverse" if variance > 0 else "normal"
                        st.metric(
                            "Variance", 
                            f"৳{variance:,.2f}",
                            delta=f"{variance_pct:+.1f}%",
                            delta_color=delta_color
                        )
                    
                    with col4:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✏️ Edit", key=f"edit_final_{project.id}"):
                                st.session_state.edit_final_cost_project_id = project.id
                                st.session_state.show_final_cost_form = True
                                st.rerun()
                        with col_b:
                            if st.button("📊 Analysis", key=f"analysis_{project.id}"):
                                st.session_state.show_variance_analysis = project.id
                                st.rerun()
                    
                    # Cost comparison table
                    st.markdown("#### Cost Comparison")
                    comparison_data = []
                    
                    for i, cost in enumerate(final_costs):
                        # Find matching projection
                        matching_proj = next((p for p in projections if p.sl_no == cost.sl_no), None)
                        projected_amount = matching_proj.amount if matching_proj else 0
                        
                        item_variance = cost.real_cost - projected_amount
                        variance_pct = (item_variance / projected_amount * 100) if projected_amount > 0 else 0
                        
                        comparison_data.append({
                            'Item': cost.particulars,
                            'Projected': f"৳{projected_amount:,.2f}",
                            'Actual': f"৳{cost.real_cost:,.2f}",
                            'Variance': f"৳{item_variance:,.2f} ({variance_pct:+.1f}%)"
                        })
                    
                    if comparison_data:
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Section 3: Projects without projections
        if projects_without_projections:
            st.markdown("### ⚠️ Projects Without Initial Projections")
            st.warning("These projects need initial projections before final cost tracking:")
            
            for project in projects_without_projections:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• **{project.project_name}** (PO: {project.po_number or 'N/A'})")
                with col2:
                    if st.button("📋 Create Projection", key=f"proj_{project.id}"):
                        # Switch to projections tab
                        st.info("💡 Please create initial projection first in the 'Initial Projections' tab.")
        
        # Handle variance analysis display
        if st.session_state.get('show_variance_analysis'):
            project_id = st.session_state.show_variance_analysis
            show_variance_analysis(project_id)
            if st.button("⬅️ Back to Final Costs"):
                del st.session_state.show_variance_analysis
                st.rerun()
            return
        
    except Exception as e:
        st.error(f"Error loading final costs: {str(e)}")
    finally:
        db_ops.close()

def show_variance_analysis(project_id):
    """Show detailed variance analysis for a project - ENHANCED VERSION"""
    st.markdown("---")
    st.subheader("📊 Cost Variance Analysis")
    
    db_ops = DatabaseOperations()
    try:
        analysis = db_ops.get_cost_variance_analysis(project_id)
        
        if not analysis:
            st.error("Unable to load variance analysis.")
            return
        
        project = analysis['project']
        initial_projections = analysis['initial_projections']
        final_costs = analysis['final_costs']
        
        # Header
        st.markdown(f"### 💼 {project.project_name}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Initial Projection",
                f"৳{analysis['initial_projection_total']:,.2f}"
            )
        
        with col2:
            st.metric(
                "Actual Costs",
                f"৳{analysis['final_cost_total']:,.2f}"
            )
        
        with col3:
            variance_color = "inverse" if analysis['variance_amount'] > 0 else "normal"
            st.metric(
                "Cost Variance",
                f"৳{analysis['variance_amount']:,.2f}",
                delta=f"{analysis['variance_percentage']:+.1f}%",
                delta_color=variance_color
            )
        
        with col4:
            st.metric(
                "Budget Remaining",
                f"৳{analysis['budget_remaining']:,.2f}"
            )
        
        # Analysis insights
        st.markdown("### 🔍 Analysis Insights")
        
        if analysis['variance_percentage'] > 10:
            st.error(f"🚨 **Cost Overrun Alert**: Actual costs are {analysis['variance_percentage']:.1f}% higher than projected!")
        elif analysis['variance_percentage'] > 5:
            st.warning(f"⚠️ **Budget Concern**: Costs are {analysis['variance_percentage']:.1f}% over projection.")
        elif analysis['variance_percentage'] < -5:
            st.success(f"💰 **Cost Savings**: Project is {abs(analysis['variance_percentage']):.1f}% under budget!")
        else:
            st.info(f"📊 **On Track**: Costs are within {abs(analysis['variance_percentage']):.1f}% of projection.")
        
        # Detailed line-by-line variance analysis
        st.markdown("### 📋 Detailed Line Item Analysis")
        
        # Create comprehensive comparison table
        variance_data = []
        
        # Create a mapping of final costs by sl_no for easier lookup
        final_costs_dict = {fc.sl_no: fc for fc in final_costs}
        
        # Process each initial projection
        for proj in initial_projections:
            final_cost = final_costs_dict.get(proj.sl_no)
            
            if final_cost:
                actual_cost = final_cost.real_cost
                variance_amount = actual_cost - proj.amount
                variance_pct = (variance_amount / proj.amount * 100) if proj.amount > 0 else 0
                
                # Determine status
                if abs(variance_pct) <= 5:
                    status = "✅ On Track"
                    status_color = "normal"
                elif variance_pct > 5:
                    status = f"🔴 Over by {variance_pct:.1f}%"
                    status_color = "inverse"
                else:
                    status = f"🟢 Under by {abs(variance_pct):.1f}%"
                    status_color = "normal"
                
                variance_data.append({
                    'Item': proj.particulars,
                    'Projected': f"৳{proj.amount:,.2f}",
                    'Actual': f"৳{actual_cost:,.2f}",
                    'Variance': f"৳{variance_amount:,.2f}",
                    'Variance %': f"{variance_pct:+.1f}%",
                    'Status': status
                })
            else:
                # Item was projected but no actual cost recorded
                variance_data.append({
                    'Item': proj.particulars,
                    'Projected': f"৳{proj.amount:,.2f}",
                    'Actual': "৳0.00",
                    'Variance': f"৳{-proj.amount:,.2f}",
                    'Variance %': "-100.0%",
                    'Status': "⚠️ Not Executed"
                })
        
        # Check for final costs that weren't in initial projection (new items)
        initial_sl_nos = {proj.sl_no for proj in initial_projections}
        
        for final_cost in final_costs:
            if final_cost.sl_no not in initial_sl_nos:
                variance_data.append({
                    'Item': f"🆕 {final_cost.particulars}",
                    'Projected': "৳0.00",
                    'Actual': f"৳{final_cost.real_cost:,.2f}",
                    'Variance': f"৳{final_cost.real_cost:,.2f}",
                    'Variance %': "N/A",
                    'Status': "🆕 New Item"
                })
        
        if variance_data:
            df = pd.DataFrame(variance_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Variance charts
        st.markdown("### 📊 Visual Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Variance by category chart
            if variance_data:
                try:
                    import plotly.express as px
                    import plotly.graph_objects as go
                    
                    # Prepare data for variance chart
                    chart_data = []
                    for item in variance_data:
                        if "৳" in item['Variance']:
                            variance_amount = float(item['Variance'].replace('৳', '').replace(',', ''))
                            chart_data.append({
                                'Item': item['Item'][:20] + "..." if len(item['Item']) > 20 else item['Item'],
                                'Variance': variance_amount
                            })
                    
                    if chart_data:
                        chart_df = pd.DataFrame(chart_data)
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                x=chart_df['Item'],
                                y=chart_df['Variance'],
                                marker_color=['red' if x > 0 else 'green' for x in chart_df['Variance']],
                                text=[f"৳{x:,.0f}" for x in chart_df['Variance']],
                                textposition='auto'
                            )
                        ])
                        
                        fig.update_layout(
                            title="Cost Variance by Item",
                            xaxis_title="Items",
                            yaxis_title="Variance (৳)",
                            height=400,
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    st.info("Chart visualization not available")
        
        with col2:
            # Summary pie chart
            try:
                import plotly.graph_objects as go
                
                # Calculate summary categories
                total_projected = analysis['initial_projection_total']
                total_actual = analysis['final_cost_total']
                
                if total_projected > 0:
                    on_budget = min(total_projected, total_actual)
                    over_budget = max(0, total_actual - total_projected)
                    under_budget = max(0, total_projected - total_actual)
                    
                    labels = []
                    values = []
                    colors = []
                    
                    if on_budget > 0:
                        labels.append('On Budget')
                        values.append(on_budget)
                        colors.append('#28a745')
                    
                    if over_budget > 0:
                        labels.append('Over Budget')
                        values.append(over_budget)
                        colors.append('#dc3545')
                    
                    if under_budget > 0:
                        labels.append('Under Budget')
                        values.append(under_budget)
                        colors.append('#17a2b8')
                    
                    if values:
                        fig = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values,
                            marker_colors=colors,
                            textinfo='label+percent+value'
                        )])
                        
                        fig.update_layout(
                            title="Budget Performance",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
            except Exception as e:
                st.info("Summary chart not available")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        if analysis['variance_percentage'] > 10:
            st.markdown("""
            **Immediate Actions Needed:**
            - 🔍 Review high-variance items to identify cost drivers
            - 📋 Implement stricter cost controls for remaining work
            - 💰 Consider renegotiating scope or budget with client
            - 📊 Update future project estimates based on learnings
            """)
        elif analysis['variance_percentage'] > 5:
            st.markdown("""
            **Monitor Closely:**
            - 👀 Track remaining costs carefully
            - 📈 Identify trends in cost overruns
            - 🎯 Focus on high-variance categories
            """)
        else:
            st.markdown("""
            **Good Performance:**
            - ✅ Costs are well-controlled
            - 📚 Document successful practices for future projects
            - 🎯 Consider if some categories can be optimized further
            """)
        
        # Export options
        st.markdown("### 📤 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Report", use_container_width=True):
                st.info("Report generation will be implemented in later steps.")
        
        with col2:
            if st.button("📧 Email Analysis", use_container_width=True):
                st.info("Email functionality will be implemented in later steps.")
        
        with col3:
            if st.button("💾 Download CSV", use_container_width=True):
                if variance_data:
                    csv_df = pd.DataFrame(variance_data)
                    csv = csv_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"variance_analysis_{project.project_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("No data to export")
        
    except Exception as e:
        st.error(f"Error in variance analysis: {str(e)}")
    finally:
        db_ops.close()

# Placeholder functions for the form (will implement in next steps)
# Replace the placeholder functions in modules/financial.py

# Replace these functions in modules/financial.py

def show_final_cost_form():
    """Show final cost editing form with add/reset functionality"""
    st.subheader("💰 Edit Final Costs")
    
    # Back button
    if st.button("⬅️ Back to Final Costs"):
        del st.session_state.show_final_cost_form
        if 'edit_final_cost_project_id' in st.session_state:
            del st.session_state.edit_final_cost_project_id
        if 'final_cost_items' in st.session_state:
            del st.session_state.final_cost_items
        st.rerun()
    
    # Get project ID
    project_id = st.session_state.get('edit_final_cost_project_id')
    if not project_id:
        st.error("No project selected!")
        return
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        final_costs = db_ops.get_final_costs_by_project(project_id)
        
        if not project:
            st.error("Project not found!")
            return
        
        if not final_costs:
            st.error("No final costs found for this project!")
            return
        
        # Project information
        st.markdown(f"### 💼 Project: {project.project_name}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**PO Number:** {project.po_number or 'N/A'}")
        with col2:
            client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
            st.info(f"**Client:** {client_name}")
        
        # Instructions
        st.markdown("### 📝 Edit Real Costs")
        st.info("💡 Update the 'Real Cost' column with actual expenses. You can also add new line items if needed.")
        
        # Initialize final costs in session state if not already done
        if 'final_cost_items' not in st.session_state:
            initialize_final_cost_items(final_costs)
        
        # Display final cost items form
        show_final_cost_items_form()
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Line Item", use_container_width=True):
                add_final_cost_item()
        
        with col2:
            if st.button("🔄 Reset All", use_container_width=True):
                reset_final_cost_items(final_costs)
        
        with col3:
            if st.button("💾 Save Final Costs", use_container_width=True):
                save_final_costs(project_id)
        
        with col4:
            if st.button("📊 View Analysis", use_container_width=True):
                # Save first, then show analysis
                save_final_costs(project_id)
                st.session_state.show_variance_analysis = project_id
                del st.session_state.show_final_cost_form
                if 'edit_final_cost_project_id' in st.session_state:
                    del st.session_state.edit_final_cost_project_id
                if 'final_cost_items' in st.session_state:
                    del st.session_state.final_cost_items
                st.rerun()
        
        # Show current totals
        projected_total = sum(item['projected_amount'] for item in st.session_state.final_cost_items)
        real_total = sum(item['real_cost'] for item in st.session_state.final_cost_items)
        variance = real_total - projected_total
        variance_pct = (variance / projected_total * 100) if projected_total > 0 else 0
        
        st.markdown("### 💰 Cost Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Projected Total", f"৳{projected_total:,.2f}")
        
        with col2:
            st.metric("Real Cost Total", f"৳{real_total:,.2f}")
        
        with col3:
            delta_color = "inverse" if variance > 0 else "normal"
            st.metric(
                "Variance", 
                f"৳{variance:,.2f}",
                delta=f"{variance_pct:+.1f}%",
                delta_color=delta_color
            )
    
    except Exception as e:
        st.error(f"Error loading final costs: {str(e)}")
    finally:
        db_ops.close()

def initialize_final_cost_items(final_costs):
    """Initialize final cost items in session state - FIXED VERSION"""
    st.session_state.final_cost_items = []
    for cost in final_costs:
        st.session_state.final_cost_items.append({
            'id': cost.id,
            'sl_no': cost.sl_no,
            'particulars': cost.particulars,
            'days': cost.days,
            'qty': cost.qty,
            'unit_price': cost.unit_price,
            'projected_amount': cost.amount,  # From initial projection
            'real_cost': cost.real_cost,  # Actual cost (editable)
            'is_new': False  # All existing items are not new
        })

def add_final_cost_item():
    """Add a new line item to final costs"""
    if 'final_cost_items' not in st.session_state:
        st.session_state.final_cost_items = []
    
    # Get next serial number
    next_sl = len(st.session_state.final_cost_items) + 1
    
    # Add new item
    st.session_state.final_cost_items.append({
        'id': None,  # New item, no database ID yet
        'sl_no': next_sl,
        'particulars': '',
        'days': 0.0,
        'qty': 0.0,
        'unit_price': 0.0,
        'projected_amount': 0.0,  # New items have no initial projection
        'real_cost': 0.0,
        'is_new': True  # Mark as new item
    })
    st.rerun()

def reset_final_cost_items(original_final_costs):
    """Reset all final cost items to original values"""
    # Clear existing session state
    if 'final_cost_items' in st.session_state:
        del st.session_state.final_cost_items
    
    # Reinitialize with original values but reset real_cost to 0
    st.session_state.final_cost_items = []
    for cost in original_final_costs:
        st.session_state.final_cost_items.append({
            'id': cost.id,
            'sl_no': cost.sl_no,
            'particulars': cost.particulars,
            'days': cost.days,
            'qty': cost.qty,
            'unit_price': cost.unit_price,
            'projected_amount': cost.amount,  # Keep original projected amount
            'real_cost': 0.0,  # Reset to zero
            'is_new': False
        })
    
    st.success("✅ All real costs reset to zero!")
    st.rerun()

def show_final_cost_items_form():
    """Show final cost items editing form with enhanced features - FIXED VERSION"""
    
    user = AuthenticationManager.get_current_user()
    is_finance_user = user['role'] == 'finance'
    
    for i, item in enumerate(st.session_state.final_cost_items):
        with st.container():
            # Safely check for is_new key
            is_new_item = item.get('is_new', False)
            
            # Highlight new items
            if is_new_item:
                st.markdown(f"#### 🆕 New Line Item {item['sl_no']}")
                st.markdown("*This is a new item not in the original projection*")
            else:
                st.markdown(f"#### Line Item {item['sl_no']}")
            
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.8, 3, 1, 1, 1.2, 1.5, 0.8])
            
            with col1:
                st.text_input("SL", value=item['sl_no'], disabled=True, key=f"final_sl_{i}")
            
            with col2:
                if is_finance_user and not is_new_item:
                    # Finance users can only edit real cost for existing items
                    st.text_input("Particulars", value=item['particulars'], disabled=True, key=f"final_particulars_{i}")
                else:
                    # Admin/users can edit particulars, finance users can edit new items
                    particulars = st.text_input(
                        "Particulars *", 
                        value=item['particulars'],
                        placeholder="Description of work/expense",
                        key=f"final_particulars_{i}"
                    )
                    st.session_state.final_cost_items[i]['particulars'] = particulars
            
            with col3:
                if is_finance_user and not is_new_item:
                    st.number_input("Days", value=item['days'], disabled=True, key=f"final_days_{i}")
                else:
                    days = st.number_input(
                        "Days", 
                        min_value=0.0, 
                        value=item['days'],
                        step=0.5,
                        key=f"final_days_{i}"
                    )
                    st.session_state.final_cost_items[i]['days'] = days
            
            with col4:
                if is_finance_user and not is_new_item:
                    st.number_input("Qty", value=item['qty'], disabled=True, key=f"final_qty_{i}")
                else:
                    qty = st.number_input(
                        "Qty", 
                        min_value=0.0, 
                        value=item['qty'],
                        step=1.0,
                        key=f"final_qty_{i}"
                    )
                    st.session_state.final_cost_items[i]['qty'] = qty
            
            with col5:
                # For new items, allow editing projected amount
                if is_new_item:
                    projected_amount = st.number_input(
                        "Projected (৳)", 
                        min_value=0.0, 
                        value=item['projected_amount'],
                        step=100.0,
                        key=f"final_projected_{i}",
                        help="Estimated cost for this new item"
                    )
                    st.session_state.final_cost_items[i]['projected_amount'] = projected_amount
                else:
                    # Existing items - projected amount is read-only
                    st.metric("Projected", f"৳{item['projected_amount']:,.2f}")
                    st.caption("(From projection)")
            
            with col6:
                # Real cost (editable by all users)
                real_cost = st.number_input(
                    "Real Cost (৳) *", 
                    min_value=0.0, 
                    value=item['real_cost'],
                    step=100.0,
                    key=f"final_real_cost_{i}",
                    help="Enter the actual cost incurred"
                )
                st.session_state.final_cost_items[i]['real_cost'] = real_cost
                
                # Show variance for this item
                if item['projected_amount'] > 0:
                    item_variance = real_cost - item['projected_amount']
                    item_variance_pct = (item_variance / item['projected_amount']) * 100
                    if abs(item_variance_pct) > 5:  # Show variance if > 5%
                        variance_color = "🔴" if item_variance > 0 else "🟢"
                        st.caption(f"{variance_color} {item_variance_pct:+.1f}%")
            
            with col7:
                # Remove button for items (except if only one item)
                if len(st.session_state.final_cost_items) > 1:
                    if st.button("🗑️", key=f"remove_final_{i}", help="Remove this item"):
                        remove_final_cost_item(i)
                        st.rerun()
            
            st.markdown("---")

def remove_final_cost_item(index):
    """Remove a final cost item - FIXED VERSION"""
    if len(st.session_state.final_cost_items) > 1:
        removed_item = st.session_state.final_cost_items.pop(index)
        
        # Renumber remaining items
        for i, item in enumerate(st.session_state.final_cost_items):
            item['sl_no'] = i + 1
        
        # If it was an existing item (not new), we need to mark it for deletion in the database
        is_new_item = removed_item.get('is_new', False)
        if not is_new_item and removed_item.get('id'):
            if 'items_to_delete' not in st.session_state:
                st.session_state.items_to_delete = []
            st.session_state.items_to_delete.append(removed_item['id'])
            
def save_final_costs(project_id):
    """Save final costs to database with support for new items - FIXED VERSION"""
    
    if 'final_cost_items' not in st.session_state:
        st.error("No final cost items to save!")
        return
    
    # Validate required fields
    for i, item in enumerate(st.session_state.final_cost_items):
        if not item['particulars'].strip():
            st.error(f"❌ Line item {item['sl_no']}: Particulars is required!")
            return
        if item['real_cost'] <= 0:
            st.warning(f"⚠️ Line item {item['sl_no']}: Real cost is zero. Is this correct?")
    
    db_ops = DatabaseOperations()
    try:
        # Delete removed items first
        if 'items_to_delete' in st.session_state:
            for item_id in st.session_state.items_to_delete:
                db_ops.delete_final_cost(item_id)
            del st.session_state.items_to_delete
        
        # Update existing items and create new ones
        for item in st.session_state.final_cost_items:
            is_new_item = item.get('is_new', False)
            
            if is_new_item:
                # Create new final cost item
                db_ops.create_final_financial_cost(
                    project_id=project_id,
                    sl_no=item['sl_no'],
                    particulars=item['particulars'],
                    days=item['days'],
                    qty=item['qty'],
                    unit_price=item['unit_price'],
                    amount=item['projected_amount'],  # Projected amount
                    real_cost=item['real_cost']  # Real cost
                )
            else:
                # Update existing final cost item
                db_ops.update_final_cost(
                    cost_id=item['id'],
                    particulars=item['particulars'],
                    days=item['days'],
                    qty=item['qty'],
                    unit_price=item['unit_price'],
                    amount=item['projected_amount'],  # Keep projected amount
                    real_cost=item['real_cost']  # Update real cost
                )
        
        st.success(f"✅ Final costs updated successfully! {len(st.session_state.final_cost_items)} items saved.")
        
        # Clear form data
        del st.session_state.final_cost_items
        del st.session_state.show_final_cost_form
        if 'edit_final_cost_project_id' in st.session_state:
            del st.session_state.edit_final_cost_project_id
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error saving final costs: {str(e)}")
    finally:
        db_ops.close()

def show_edit_final_cost_form(project_id):
    """Show edit final cost form - this is just a redirect"""
    # This function is called when edit button is clicked
    # It just sets up the session state for the main form
    st.session_state.edit_final_cost_project_id = project_id
    st.session_state.show_final_cost_form = True
    if 'edit_final_cost_id' in st.session_state:
        del st.session_state.edit_final_cost_id
    st.rerun()
        
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
    """Generate professional PDF money receipt with company logo"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.utils import ImageReader
        import io
        import base64
        import os
        from datetime import datetime
        
        # Get additional data from database
        db_ops = DatabaseOperations()
        try:
            # Get disbursement details
            disbursement = db_ops.get_disbursement_by_id(money_receipt.disbursement_id)
            project = None
            received_from_company = None
            received_by_company = None
            
            if disbursement and disbursement.project_id:
                project = db_ops.get_project_by_id(disbursement.project_id)
                if project:
                    received_from_company = project.po_issuing_company
                    received_by_company = project.supplier_company
        finally:
            db_ops.close()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Add border around the entire page
        margin = 30
        p.rect(margin, margin, width - 2*margin, height - 2*margin)
        
        # Header section with logo
        y_position = height - 80
        
        # Company Logo - Top Left Corner
        logo_path = "assets/images/am_logo.png"
        try:
            if os.path.exists(logo_path):
                # Logo positioning (top left)
                logo_x = 50
                logo_y = height - 130  # Moved logo up a bit
                logo_width = 80
                logo_height = 80
                
                # Draw the logo
                p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
                
                # Adjust title position to accommodate logo
                title_y_position = y_position
            else:
                # If logo file doesn't exist, show a placeholder
                p.setFont("Helvetica", 8)
                p.drawString(50, height - 60, f"Logo not found: {logo_path}")
                title_y_position = y_position
                
        except Exception as logo_error:
            # If there's an error loading the logo, continue without it
            p.setFont("Helvetica", 8)
            p.drawString(50, height - 60, f"Logo error: {str(logo_error)}")
            title_y_position = y_position
        
        # Money Receipt Title - Centered
        p.setFont("Helvetica-Bold", 24)
        title = "Money Receipt"
        title_width = p.stringWidth(title, "Helvetica-Bold", 24)
        p.drawString((width - title_width) / 2, title_y_position, title)
        
        # Date and Receipt Number - Better positioned below logo
        y_position = height - 160  # More space from logo
        p.setFont("Helvetica", 12)
        
        # Date (left side)
        receipt_date = money_receipt.receipt_date.strftime('%d.%m.%Y')
        p.drawString(50, y_position, f"Date: {receipt_date}")
        
        # Receipt Number (right side)
        receipt_num_text = f"Receipt No: {money_receipt.receipt_number}"
        receipt_num_width = p.stringWidth(receipt_num_text, "Helvetica", 12)
        p.drawString(width - receipt_num_width - 50, y_position, receipt_num_text)
        
        # Add some space after header
        y_position -= 60
        
        # Received From section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "Received from:")
        
        y_position -= 25
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, money_receipt.received_from)
        
        # Add company details if available
        if received_from_company and disbursement and disbursement.disbursement_type != "personal_loan":
            y_position -= 18
            p.setFont("Helvetica", 10)
            if received_from_company.address:
                # Handle long addresses by wrapping
                address_lines = wrap_text(p, received_from_company.address, "Helvetica", 10, width - 100)
                for line in address_lines:
                    p.drawString(50, y_position, line)
                    y_position -= 12
            
            if received_from_company.phone:
                p.drawString(50, y_position, f"Phone: {received_from_company.phone}")
                y_position -= 12
        
        # Amount section with project details
        y_position -= 30
        p.setFont("Helvetica", 11)
        
        # Create the amount description
        amount_text = f"The sum of BDT {money_receipt.amount:,.0f}"
        amount_words = amount_to_words_professional(money_receipt.amount)
        
        # Add disbursement type context
        disbursement_context = ""
        if disbursement:
            if disbursement.disbursement_type == "advance":
                disbursement_context = "(from advance)"
            elif disbursement.disbursement_type == "project_cost":
                disbursement_context = "(as project cost)"
            elif disbursement.disbursement_type == "personal_loan":
                disbursement_context = "(as personal loan)"
        
        # Build the full description
        full_description = f"{amount_text} {disbursement_context}, totaling BDT {money_receipt.amount:,.0f} ({amount_words}), has been received"
        
        # Add project context if available
        if project:
            full_description += f" for the {project.project_name} project"
        elif disbursement and disbursement.description:
            full_description += f" for {disbursement.description}"
        
        full_description += "."
        
        # Word wrap the description
        description_lines = wrap_text(p, full_description, "Helvetica", 11, width - 100)
        
        # Draw the wrapped text
        for line in description_lines:
            p.drawString(50, y_position, line)
            y_position -= 16
        
        # Received By section
        y_position -= 30
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_position, "Received by:")
        
        y_position -= 25
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, money_receipt.received_by)
        
        # Add company details if available
        if received_by_company and disbursement and disbursement.disbursement_type != "personal_loan":
            y_position -= 18
            p.setFont("Helvetica", 10)
            if received_by_company.address:
                # Handle long addresses by wrapping
                address_lines = wrap_text(p, received_by_company.address, "Helvetica", 10, width - 100)
                for line in address_lines:
                    p.drawString(50, y_position, line)
                    y_position -= 12
            
            if received_by_company.phone:
                p.drawString(50, y_position, f"Phone: {received_by_company.phone}")
                y_position -= 12
        
        # Signature section - Fixed position at bottom
        signature_y = 200
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, signature_y, "Acknowledged By:")
        
        signature_y -= 25
        p.setFont("Helvetica", 11)
        p.drawString(50, signature_y, f"For {money_receipt.received_by}")
        
        # Add contact person if available
        if received_by_company and received_by_company.contact_person:
            signature_y -= 18
            p.drawString(50, signature_y, f"Name: {received_by_company.contact_person}")
        
        # Signature line
        signature_y -= 35
        p.setFont("Helvetica", 10)
        p.drawString(50, signature_y, "Signature: _________________________")
        
        # Date line
        signature_y -= 25
        p.drawString(50, signature_y, f"Date: {receipt_date}")
        
        # Footer
        p.setFont("Helvetica-Oblique", 8)
        footer_text = "This is a computer generated money receipt."
        footer_width = p.stringWidth(footer_text, "Helvetica-Oblique", 8)
        p.drawString((width - footer_width) / 2, 50, footer_text)
        
        p.save()
        
        # Prepare download
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        # Create download link
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="receipt_{money_receipt.receipt_number}.pdf">📄 Click here to download Receipt PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Professional money receipt with company logo generated successfully!")
        
    except ImportError as e:
        st.error("❌ ReportLab library is not installed!")
        st.info("💡 To fix this, install reportlab: `pip install reportlab`")
        st.code("pip install reportlab")
        
    except Exception as e:
        st.error(f"❌ Error generating PDF: {str(e)}")
        st.info("💡 PDF generation failed. Please check the error details above.")
        
        # Debug information for logo issues
        if "am_logo.png" in str(e):
            st.info("🔍 Logo Debug Information:")
            logo_path = "assets/images/am_logo.png"
            st.code(f"Looking for logo at: {logo_path}")
            st.code(f"File exists: {os.path.exists(logo_path)}")
            if os.path.exists("assets"):
                st.code(f"Assets folder contents: {os.listdir('assets')}")
            if os.path.exists("assets/images"):
                st.code(f"Images folder contents: {os.listdir('assets/images')}")

def wrap_text(canvas_obj, text, font_name, font_size, max_width):
    """Helper function to wrap text for PDF generation"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if canvas_obj.stringWidth(test_line, font_name, font_size) < max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def amount_to_words_professional(amount):
    """Convert amount to words in professional format"""
    try:
        ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
                'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
                'seventeen', 'eighteen', 'nineteen']
        
        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        
        def convert_hundred(num):
            result = ''
            if num > 99:
                result += ones[num // 100] + ' hundred '
                num %= 100
            if num > 19:
                result += tens[num // 10]
                if num % 10 > 0:
                    result += '-' + ones[num % 10]
                result += ' '
                num = 0
            if num > 0:
                result += ones[num] + ' '
            return result
        
        if amount == 0:
            return 'zero Taka'
        
        int_amount = int(amount)
        result = ''
        
        # Handle crores (10,000,000)
        if int_amount >= 10000000:
            crore = int_amount // 10000000
            result += convert_hundred(crore) + 'crore '
            int_amount %= 10000000
            
        # Handle lakhs (100,000)
        if int_amount >= 100000:
            lakh = int_amount // 100000
            result += convert_hundred(lakh) + 'lakh '
            int_amount %= 100000
            
        # Handle thousands
        if int_amount >= 1000:
            thousand = int_amount // 1000
            result += convert_hundred(thousand) + 'thousand '
            int_amount %= 1000
            
        # Handle remaining hundreds, tens, and ones
        if int_amount > 0:
            result += convert_hundred(int_amount)
            
        # Clean up and format
        result = result.strip()
        if result:
            return result + ' Taka'
        else:
            return 'zero Taka'
            
    except Exception as e:
        # Fallback to simple version
        return f"Rupees {int(amount)} Taka"
    
def update_disbursement_form_for_companies():
    """Enhanced disbursement form to better handle company selection"""
    # This function can be used to enhance the disbursement form
    # to provide better company selection for received_from and received_by
    pass

# Additional helper function for the disbursement form
def get_company_options_for_disbursement():
    """Get formatted company options for disbursement forms"""
    db_ops = DatabaseOperations()
    try:
        companies = db_ops.get_all_companies()
        
        # Format companies for selection
        company_options = []
        for company in companies:
            display_name = company.name
            if company.contact_person:
                display_name += f" (Contact: {company.contact_person})"
            
            company_options.append({
                'id': company.id,
                'name': company.name,
                'display_name': display_name,
                'type': company.company_type,
                'address': company.address,
                'phone': company.phone,
                'contact_person': company.contact_person
            })
        
        return company_options
        
    except Exception as e:
        st.error(f"Error loading companies: {str(e)}")
        return []
    finally:
        db_ops.close()
        
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