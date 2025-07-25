import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
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

def show_invoice_management():
    """Show invoice management interface"""
    st.subheader("📄 Invoice Management")
    
    user = AuthenticationManager.get_current_user()
    
    # Handle invoice creation form
    if st.session_state.get('show_invoice_form'):
        show_invoice_creation_form()
        return
    
    # Handle invoice view
    if st.session_state.get('view_invoice_id'):
        show_invoice_details(st.session_state.view_invoice_id)
        return
    
    # Main invoice management interface
    show_invoice_management_interface()

def show_invoice_management_interface():
    """Main invoice management interface - FIXED SESSION ISSUE"""
    
    # Get projects that can have invoices created
    db_ops = DatabaseOperations()
    try:
        projects = db_ops.get_all_projects()
        
        if not projects:
            st.warning("⚠️ No projects found. Please create projects first.")
            return
        
        # Process projects and extract all needed data while session is active
        processed_projects = []
        for project in projects:
            # Extract all data we need while session is active
            project_data = {
                'id': project.id,
                'project_name': project.project_name,
                'po_number': project.po_number,
                'status': project.status,
                'final_po_value': project.final_po_value or 0,
                'vat_amount': project.vat_amount or 0,
                'ait_amount': project.ait_amount or 0,
                'invoice_submission_date': project.invoice_submission_date,
                'final_bill_collection_date': project.final_bill_collection_date,
                'client_name': project.po_issuing_company.name if project.po_issuing_company else 'N/A',
                'client_id': project.po_issuing_company_id
            }
            processed_projects.append(project_data)
        
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")
        return
    finally:
        db_ops.close()
    
    # Now work with processed data (no database session needed)
    projects_ready_for_invoice = []
    projects_with_invoices = []
    projects_not_ready = []
    
    for project_data in processed_projects:
        if project_data['status'] == 'cancelled':
            continue
        elif project_data['status'] == 'invoice_submitted':
            projects_with_invoices.append(project_data)
        elif project_data['status'] in ['active'] and project_data['final_po_value'] > 0:
            projects_ready_for_invoice.append(project_data)
        else:
            projects_not_ready.append(project_data)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", len(processed_projects))
    
    with col2:
        st.metric("Ready for Invoice", len(projects_ready_for_invoice))
    
    with col3:
        st.metric("Invoices Created", len(projects_with_invoices))
    
    with col4:
        pending_invoices = len(projects_ready_for_invoice)
        st.metric("Pending Invoices", pending_invoices)
    
    # Invoice Due Date Tracking
    show_invoice_due_date_tracker()
    
    st.markdown("---")  # Add separator
    
    # Projects ready for invoice creation
    if projects_ready_for_invoice:
        st.markdown("### 📝 Projects Ready for Invoice Creation")
        st.info("💡 These projects are ready to have invoices created.")
        
        for project_data in projects_ready_for_invoice:
            with st.expander(f"🚀 {project_data['project_name']} - Create Invoice"):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info(f"""
                    **Project:** {project_data['project_name']}  
                    **Client:** {project_data['client_name']}  
                    **PO:** {project_data['po_number'] or 'N/A'}  
                    **Status:** {project_data['status'].title()}
                    """)
                
                with col2:
                    st.metric("Project Value", f"৳{project_data['final_po_value']:,.2f}")
                    st.metric("VAT Amount", f"৳{project_data['vat_amount']:,.2f}")
                    st.metric("AIT Amount", f"৳{project_data['ait_amount']:,.2f}")
                
                with col3:
                    if st.button("📄 Create Invoice", key=f"create_invoice_{project_data['id']}"):
                        st.session_state.invoice_project_id = project_data['id']
                        st.session_state.show_invoice_form = True
                        st.rerun()
    
    # Projects with existing invoices
    if projects_with_invoices:
        st.markdown("### 📄 Projects with Invoices")
        
        for project_data in projects_with_invoices:
            with st.expander(f"📄 {project_data['project_name']} - Invoice Created"):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.success(f"""
                    **Status:** ✅ Invoice Submitted  
                    **Project:** {project_data['project_name']}  
                    **Client:** {project_data['client_name']}  
                    **PO:** {project_data['po_number'] or 'N/A'}
                    """)
                
                with col2:
                    st.metric("Invoice Amount", f"৳{project_data['final_po_value']:,.2f}")
                    if project_data['invoice_submission_date']:
                        st.metric("Submitted On", project_data['invoice_submission_date'].strftime('%Y-%m-%d'))
                    
                    # Show payment terms
                    if project_data['invoice_submission_date'] and project_data['final_bill_collection_date']:
                        payment_days = (project_data['final_bill_collection_date'] - project_data['invoice_submission_date']).days
                        if payment_days == 0:
                            payment_terms_display = "Due on Receipt"
                        else:
                            payment_terms_display = f"Net {payment_days}"
                        st.metric("Payment Terms", payment_terms_display)
                
                with col3:
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("👀 View Invoice", key=f"view_invoice_{project_data['id']}"):
                            st.session_state.view_invoice_id = project_data['id']
                            st.rerun()
                    
                    with col_b:
                        if st.button("📥 Download", key=f"download_invoice_{project_data['id']}"):
                            # Create a temporary project object for PDF generation
                            temp_project = type('Project', (), project_data)()
                            # Add necessary attributes for PDF generation
                            temp_project.po_issuing_company = type('Company', (), {
                                'name': project_data['client_name'],
                                'address': None,
                                'phone': None,
                                'email': None
                            })()
                            temp_project.supplier_company_id = None
                            generate_invoice_pdf(temp_project)
    
    # Projects not ready for invoicing
    if projects_not_ready:
        st.markdown("### ⏳ Projects Not Ready for Invoice")
        st.warning("These projects need to be activated and have proper financial data before invoices can be created.")
        
        for project_data in projects_not_ready[:5]:  # Show first 5
            col1, col2 = st.columns([3, 1])
            with col1:
                reason = get_invoice_readiness_reason_from_data(project_data)
                st.write(f"• **{project_data['project_name']}** - {reason}")
            with col2:
                st.caption(f"Status: {project_data['status'].title()}")
        
        if len(projects_not_ready) > 5:
            st.caption(f"... and {len(projects_not_ready) - 5} more projects")

def get_invoice_readiness_reason_from_data(project_data):
    """Get reason why project is not ready for invoice from processed data"""
    if project_data['status'] == 'new':
        return "Project is still new - needs financial projections"
    elif project_data['final_po_value'] <= 0:
        return "No project value defined"
    elif project_data['status'] == 'completed':
        return "Project already completed"
    else:
        return f"Status: {project_data['status']}"

def get_invoice_readiness_reason(project):
    """Get reason why project is not ready for invoice"""
    if project.status == 'new':
        return "Project is still new - needs financial projections"
    elif not project.final_po_value or project.final_po_value <= 0:
        return "No project value defined"
    elif project.status == 'completed':
        return "Project already completed"
    else:
        return f"Status: {project.status}"

def show_invoice_creation_form():
    """Show invoice creation form"""
    st.subheader("📄 Create Professional Invoice")
    
    # Back button
    if st.button("⬅️ Back to Invoice Management"):
        del st.session_state.show_invoice_form
        if 'invoice_project_id' in st.session_state:
            del st.session_state.invoice_project_id
        st.rerun()
    
    # Get project ID
    project_id = st.session_state.get('invoice_project_id')
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
        st.markdown(f"### 💼 Creating Invoice for: {project.project_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**PO Number:** {project.po_number or 'N/A'}")
        with col2:
            client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
            st.info(f"**Client:** {client_name}")
        with col3:
            st.info(f"**Invoice Amount:** ৳{project.final_po_value or 0:,.2f}")
        
        # Invoice form
        with st.form("invoice_creation_form"):
            st.markdown("### 📋 Invoice Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input(
                    "Invoice Number *",
                    value=f"INV-{datetime.now().strftime('%Y%m%d')}-{project.id:03d}",
                    help="Unique invoice number"
                )
                
                invoice_date = st.date_input(
                    "Invoice Date *",
                    value=date.today(),
                    help="Date when invoice is created"
                )
            
            with col2:
                payment_terms = st.selectbox(
                    "Payment Terms",
                    ["Net 30", "Net 15", "Net 7", "Due on Receipt", "Custom"],
                    help="Payment terms for the invoice"
                )
                
                # Auto-calculate due date based on payment terms
                if payment_terms == "Net 30":
                    default_due_date = invoice_date + timedelta(days=30)
                elif payment_terms == "Net 15":
                    default_due_date = invoice_date + timedelta(days=15)
                elif payment_terms == "Net 7":
                    default_due_date = invoice_date + timedelta(days=7)
                elif payment_terms == "Due on Receipt":
                    default_due_date = invoice_date
                else:  # Custom
                    default_due_date = invoice_date + timedelta(days=30)
                
                due_date = st.date_input(
                    "Due Date *",
                    value=default_due_date,
                    help="Payment due date (auto-calculated from payment terms)"
                )
            
            # Add custom payment terms field when Custom is selected
            if payment_terms == "Custom":
                custom_terms = st.text_input(
                    "Custom Payment Terms *",
                    placeholder="e.g., Net 45, 2/10 Net 30, etc.",
                    help="Enter custom payment terms"
                )
            else:
                custom_terms = payment_terms
            
            # Invoice description
            description = st.text_area(
                "Work Description *",
                value=f"Professional services for {project.project_name} project as per PO #{project.po_number or 'N/A'}",
                help="Description of work/services provided"
            )
            
            # Financial breakdown (read-only, from project)
            st.markdown("### 💰 Financial Breakdown")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Base Amount", f"৳{project.total_po_value or 0:,.2f}")
            
            with col2:
                st.metric(f"VAT ({project.vat_rate or 0}%)", f"৳{project.vat_amount or 0:,.2f}")
            
            with col3:
                st.metric(f"AIT ({project.ait_rate or 0}%)", f"৳{project.ait_amount or 0:,.2f}")
            
            st.markdown("---")
            st.markdown(f"### **Total Invoice Amount: ৳{project.final_po_value or 0:,.2f}**")
            
            # Submit button - MAKE SURE THIS IS INSIDE THE FORM
            submitted = st.form_submit_button("📄 Generate Invoice", use_container_width=True)
        
        # Form processing - MAKE SURE THIS IS OUTSIDE THE FORM
        if submitted:
            # Validation
            # Validation
            if not invoice_number or not description:
                st.error("Invoice number and description are required!")
                return
                
            if payment_terms == "Custom" and not custom_terms:
                st.error("Custom payment terms are required when 'Custom' is selected!")
                return
                
            if invoice_date > due_date:
                st.error("Due date cannot be before invoice date!")
                return
            
            try:
                # Create invoice record (we'll store basic info in project)
                project.invoice_submission_date = invoice_date
                project.final_bill_collection_date = due_date  # Using this field for due date
                
                # Update project status to invoice_submitted
                db_ops.trigger_status_update(project.id, 'invoice_created')
                
                db_ops.db.commit()
                
                # Store invoice details in session for PDF generation
                st.session_state.invoice_data = {
                        'project': project,
                        'invoice_number': invoice_number,
                        'invoice_date': invoice_date,
                        'due_date': due_date,
                        'payment_terms': custom_terms,  # Use custom_terms instead of payment_terms
                        'description': description
                    }
                
                st.success(f"✅ Invoice created successfully!")
                st.success(f"📄 Invoice #{invoice_number} for ৳{project.final_po_value:,.2f}")
                st.balloons()
                
                # Generate PDF immediately
                generate_invoice_pdf(project, st.session_state.invoice_data)
                
                # Clear form and return
                del st.session_state.show_invoice_form
                if 'invoice_project_id' in st.session_state:
                    del st.session_state.invoice_project_id
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error creating invoice: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading invoice form: {str(e)}")
    finally:
        db_ops.close()

def get_invoice_due_date_analysis():
    """Get invoice due date analysis for tracking"""
    db_ops = DatabaseOperations()
    try:
        # Get all projects with invoices
        projects = db_ops.get_all_projects()
        invoice_projects = [p for p in projects if p.status == 'invoice_submitted']
        
        if not invoice_projects:
            return {
                'total_invoices': 0,
                'overdue_invoices': [],
                'due_soon_invoices': [],
                'paid_invoices': []
            }
        
        current_date = date.today()
        overdue_invoices = []
        due_soon_invoices = []
        paid_invoices = []
        
        for project in invoice_projects:
            if project.final_bill_collection_date:
                due_date = project.final_bill_collection_date
                days_until_due = (due_date - current_date).days
                
                if project.status == 'completed':
                    paid_invoices.append({
                        'project': project,
                        'due_date': due_date,
                        'days_until_due': days_until_due
                    })
                elif days_until_due < 0:
                    overdue_invoices.append({
                        'project': project,
                        'due_date': due_date,
                        'days_overdue': abs(days_until_due)
                    })
                elif days_until_due <= 7:
                    due_soon_invoices.append({
                        'project': project,
                        'due_date': due_date,
                        'days_until_due': days_until_due
                    })
        
        return {
            'total_invoices': len(invoice_projects),
            'overdue_invoices': overdue_invoices,
            'due_soon_invoices': due_soon_invoices,
            'paid_invoices': paid_invoices
        }
        
    except Exception as e:
        print(f"Error getting invoice due date analysis: {str(e)}")
        return {
            'total_invoices': 0,
            'overdue_invoices': [],
            'due_soon_invoices': [],
            'paid_invoices': []
        }
    finally:
        db_ops.close()

def show_invoice_due_date_tracker():
    """Show invoice due date tracking section"""
    st.markdown("### 📅 Invoice Due Date Tracker")
    
    analysis = get_invoice_due_date_analysis()
    
    if analysis['total_invoices'] == 0:
        st.info("📭 No invoices found for tracking.")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Invoices", analysis['total_invoices'])
    
    with col2:
        overdue_count = len(analysis['overdue_invoices'])
        st.metric(
            "Overdue Invoices", 
            overdue_count,
            delta="🚨 Needs attention" if overdue_count > 0 else "✅ None"
        )
    
    with col3:
        due_soon_count = len(analysis['due_soon_invoices'])
        st.metric(
            "Due Soon (7 days)", 
            due_soon_count,
            delta="⏰ Follow up" if due_soon_count > 0 else "✅ None"
        )
    
    with col4:
        paid_count = len(analysis['paid_invoices'])
        st.metric("Paid Invoices", paid_count)
    
    # Overdue invoices alert
    if analysis['overdue_invoices']:
        st.error("🚨 **Overdue Invoices - Immediate Action Required**")
        
        for invoice in analysis['overdue_invoices'][:5]:  # Show first 5
            project = invoice['project']
            days_overdue = invoice['days_overdue']
            client_name = project.po_issuing_company.name if project.po_issuing_company else 'Unknown'
            
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{project.project_name}**")
                st.caption(f"Client: {client_name}")
            
            with col2:
                st.write(f"Due: {invoice['due_date'].strftime('%Y-%m-%d')}")
                st.write(f"Amount: ৳{project.final_po_value or 0:,.2f}")
            
            with col3:
                st.error(f"{days_overdue} days overdue")
        
        if len(analysis['overdue_invoices']) > 5:
            st.caption(f"... and {len(analysis['overdue_invoices']) - 5} more overdue invoices")
    
    # Due soon invoices
    if analysis['due_soon_invoices']:
        st.warning("⏰ **Invoices Due Soon (Within 7 Days)**")
        
        for invoice in analysis['due_soon_invoices']:
            project = invoice['project']
            days_until_due = invoice['days_until_due']
            client_name = project.po_issuing_company.name if project.po_issuing_company else 'Unknown'
            
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{project.project_name}**")
                st.caption(f"Client: {client_name}")
            
            with col2:
                st.write(f"Due: {invoice['due_date'].strftime('%Y-%m-%d')}")
                st.write(f"Amount: ৳{project.final_po_value or 0:,.2f}")
            
            with col3:
                if days_until_due == 0:
                    st.warning("Due Today")
                else:
                    st.warning(f"Due in {days_until_due} days")
    
    # Show good news if no issues
    if not analysis['overdue_invoices'] and not analysis['due_soon_invoices']:
        st.success("✅ **All Invoices On Track!** No overdue or urgent invoices.")

def show_invoice_details(project_id):
    """Show invoice details view"""
    st.subheader("👀 Invoice Details")
    
    # Back button
    if st.button("⬅️ Back to Invoice Management"):
        del st.session_state.view_invoice_id
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        if not project:
            st.error("Project not found!")
            return
        
        if project.status != 'invoice_submitted':
            st.warning("This project doesn't have an invoice created yet.")
            return
        
        # Show invoice preview
        st.markdown(f"### 📄 Invoice for: {project.project_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Invoice Status:** ✅ Created  
            **Project:** {project.project_name}  
            **Client:** {project.po_issuing_company.name if project.po_issuing_company else 'N/A'}  
            **PO Number:** {project.po_number or 'N/A'}
            """)
        
        with col2:
            st.info(f"""
            **Invoice Amount:** ৳{project.final_po_value or 0:,.2f}  
            **Invoice Date:** {project.invoice_submission_date.strftime('%Y-%m-%d') if project.invoice_submission_date else 'N/A'}  
            **Due Date:** {project.final_bill_collection_date.strftime('%Y-%m-%d') if project.final_bill_collection_date else 'N/A'}
            """)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download Invoice PDF", use_container_width=True):
                generate_invoice_pdf(project)
        
        with col2:
            if st.button("📧 Email Invoice", use_container_width=True):
                st.info("Email functionality will be implemented in later phases.")
        
        with col3:
            if st.button("🖨️ Print Invoice", use_container_width=True):
                st.info("Print functionality will be implemented in later phases.")
        
    except Exception as e:
        st.error(f"Error loading invoice details: {str(e)}")
    finally:
        db_ops.close()

def generate_invoice_pdf(project, invoice_data=None):
    """Generate professional invoice PDF with company logo - ENHANCED VERSION"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.utils import ImageReader
        import io
        import base64
        import os
        from datetime import datetime
        
        # Get supplier company details from database
        db_ops = DatabaseOperations()
        supplier_company = None
        try:
            if project.supplier_company_id:
                supplier_company = db_ops.get_company_by_id(project.supplier_company_id)
        finally:
            db_ops.close()
        
        # Use stored invoice data or create default
        if invoice_data:
            inv_data = invoice_data
        else:
            # Create default invoice data from project
            inv_data = {
                'project': project,
                'invoice_number': f"INV-{datetime.now().strftime('%Y%m%d')}-{project.id:03d}",
                'invoice_date': project.invoice_submission_date or date.today(),
                'due_date': project.final_bill_collection_date or date.today() + timedelta(days=30),
                'payment_terms': 'Net 30',
                'description': f"Professional services for {project.project_name} project"
            }
        
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
                logo_y = height - 130
                logo_width = 80
                logo_height = 80
                
                # Draw the logo
                p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
                
                # Adjust title position to accommodate logo
                title_y_position = y_position - 20
            else:
                title_y_position = y_position
                
        except Exception as logo_error:
            title_y_position = y_position
        
        # Supplier Company Information - Top Right (from database)
        p.setFont("Helvetica-Bold", 12)
        company_info_x = width - 200
        company_info_y = height - 80
        
        if supplier_company:
            p.drawString(company_info_x, company_info_y, supplier_company.name)
            
            p.setFont("Helvetica", 10)
            company_info_y -= 15
            
            if supplier_company.address:
                # Clean address (remove city/postal code lines if they exist)
                address_parts = supplier_company.address.split('\n')
                clean_address = [part for part in address_parts if not part.startswith('City:') and not part.startswith('Postal:')]
                for addr_line in clean_address[:2]:  # Show first 2 lines
                    p.drawString(company_info_x, company_info_y, addr_line)
                    company_info_y -= 12
            
            if supplier_company.email:
                p.drawString(company_info_x, company_info_y, f"Email: {supplier_company.email}")
                company_info_y -= 12
            
            if supplier_company.phone:
                p.drawString(company_info_x, company_info_y, f"Phone: {supplier_company.phone}")
        else:
            # Fallback company info
            p.drawString(company_info_x, company_info_y, "AM Square Limited")
            p.setFont("Helvetica", 10)
            company_info_y -= 15
            p.drawString(company_info_x, company_info_y, "Marketing & Communications")
            company_info_y -= 12
            p.drawString(company_info_x, company_info_y, "Dhaka, Bangladesh")
        
        # Invoice Title - Centered
        p.setFont("Helvetica-Bold", 28)
        title = "INVOICE"
        title_width = p.stringWidth(title, "Helvetica-Bold", 28)
        p.drawString((width - title_width) / 2, title_y_position, title)
        
        # Invoice Details - Right side
        y_position = height - 180
        p.setFont("Helvetica-Bold", 12)
        p.drawString(company_info_x, y_position, f"Invoice #: {inv_data['invoice_number']}")
        
        y_position -= 20
        p.setFont("Helvetica", 11)
        p.drawString(company_info_x, y_position, f"Invoice Date: {inv_data['invoice_date'].strftime('%B %d, %Y')}")
        
        y_position -= 15
        p.drawString(company_info_x, y_position, f"Due Date: {inv_data['due_date'].strftime('%B %d, %Y')}")
        
        y_position -= 15
        p.drawString(company_info_x, y_position, f"Payment Terms: {inv_data.get('payment_terms', 'Net 30')}")
        
        # Client Information - Left side
        y_position = height - 180
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Bill To:")
        
        y_position -= 20
        p.setFont("Helvetica-Bold", 11)
        client_name = project.po_issuing_company.name if project.po_issuing_company else 'Client Name'
        p.drawString(50, y_position, client_name)
        
        y_position -= 15
        p.setFont("Helvetica", 10)
        if project.po_issuing_company and project.po_issuing_company.address:
            # Handle long addresses by wrapping
            address_lines = wrap_text(p, project.po_issuing_company.address, "Helvetica", 10, 250)
            for line in address_lines[:3]:  # Show first 3 lines
                p.drawString(50, y_position, line)
                y_position -= 12
        
        if project.po_issuing_company and project.po_issuing_company.phone:
            p.drawString(50, y_position, f"Phone: {project.po_issuing_company.phone}")
            y_position -= 12
        
        if project.po_issuing_company and project.po_issuing_company.email:
            p.drawString(50, y_position, f"Email: {project.po_issuing_company.email}")
            y_position -= 12
        
        # Project Details Section - SIMPLIFIED
        y_position = height - 320
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Project Details:")
        
        y_position -= 20
        p.setFont("Helvetica", 11)
        p.drawString(50, y_position, f"PO Number: {project.po_number or 'N/A'}")
        
        # Service Description - SIMPLIFIED
        y_position -= 30
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Description of Services:")
        
        # Financial Breakdown Table - ENHANCED
        y_position -= 50
        
        # Table headers
        p.setFont("Helvetica-Bold", 11)
        table_y = y_position
        
        # Draw table header background
        p.setFillColor((0.9, 0.9, 0.9))
        p.rect(50, table_y - 5, width - 100, 25, fill=1, stroke=1)
        
        # Reset text color
        p.setFillColor((0, 0, 0))
        
        # Table headers
        p.drawString(60, table_y + 5, "Description")
        p.drawString(350, table_y + 5, "Amount")
        p.drawString(480, table_y + 5, "Total")
        
        # Table content
        table_y -= 30
        p.setFont("Helvetica", 10)
        
        # Base amount row (without VAT)
        p.drawString(60, table_y, project.project_name)
        p.drawString(350, table_y, f"{project.total_po_value or 0:,.2f}")
        p.drawString(480, table_y, f"{project.total_po_value or 0:,.2f}")
        
        # VAT row (separate line)
        if project.vat_amount and project.vat_amount > 0:
            table_y -= 20
            p.drawString(60, table_y, f"VAT ({project.vat_rate or 15}%)")
            p.drawString(350, table_y, f"{project.vat_amount:,.2f}")
            p.drawString(480, table_y, f"{project.vat_amount:,.2f}")
        
        # AIT row (deduction)
        # if project.ait_amount and project.ait_amount > 0:
        #     table_y -= 20
        #     p.drawString(60, table_y, f"Less: AIT ({project.ait_rate or 2}%)")
        #     p.drawString(350, table_y, f"-{project.ait_amount:,.2f}")
        #     p.drawString(480, table_y, f"-{project.ait_amount:,.2f}")
        
        # Draw table border
        table_bottom = table_y - 10
        p.rect(50, table_bottom, width - 100, y_position - table_bottom + 40, fill=0, stroke=1)
        
        # Total section
        table_y -= 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(350, table_y, "TOTAL AMOUNT:")
        p.drawString(480, table_y, f"{project.final_po_value or 0:,.2f}")
        
        # Amount in words - ALL CAPITALS
        table_y -= 25
        p.setFont("Helvetica", 10)
        amount_words = amount_to_words_professional(project.final_po_value or 0).upper()
        p.drawString(60, table_y, f"Amount in Words: {amount_words}")
        
        # Payment Instructions
        table_y -= 40
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, table_y, "Payment Instructions:")
        
        table_y -= 20
        p.setFont("Helvetica", 10)
        payment_instructions = [
            "• Please make payment within the specified due date",
            "• Include invoice number in payment reference",
            "• For bank transfer, please contact us for account details"
        ]
        
        for instruction in payment_instructions:
            p.drawString(60, table_y, instruction)
            table_y -= 15
        
        # Footer section - FIXED LAYOUT
        footer_y = 200
        
        # Signature section - FROM SUPPLIER COMPANY
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, footer_y, "Authorized Signature:")
        
        footer_y -= 25
        p.setFont("Helvetica", 10)
        
        if supplier_company:
            p.drawString(50, footer_y, f"For {supplier_company.name}")
            footer_y -= 15
            
            if supplier_company.contact_person:
                p.drawString(50, footer_y, supplier_company.contact_person)
                footer_y -= 12
            
            if supplier_company.designation:
                p.drawString(50, footer_y, supplier_company.designation)
                footer_y -= 12
        else:
            p.drawString(50, footer_y, "For AM Square Limited")
            footer_y -= 15
            p.drawString(50, footer_y, "Mohammad Abir Mazumder")
            footer_y -= 12
            p.drawString(50, footer_y, "Managing Director")
        
        # Signature line
        footer_y -= 25
        p.drawString(50, footer_y, "Signature: _________________________")
        
        # Date line
        footer_y -= 15
        p.drawString(50, footer_y, f"Date: {inv_data['invoice_date'].strftime('%B %d, %Y')}")
        
        # Terms and conditions - FIXED POSITIONING
        footer_y -= 30
        p.setFont("Helvetica", 8)
        p.drawString(50, footer_y, "Terms & Conditions:")
        footer_y -= 10
        p.drawString(50, footer_y, "1. Payment is due within the specified payment terms.")
        footer_y -= 10
        p.drawString(50, footer_y, "2. All disputes must be reported within 7 days.")
        
        # Footer - CLEAN VERSION
        # p.setFont("Helvetica-Oblique", 8)
        # footer_text = f"Invoice generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AM Square Limited"
        # footer_width = p.stringWidth(footer_text, "Helvetica-Oblique", 8)
        # p.drawString((width - footer_width) / 2, 50, footer_text)
        
        p.save()
        
        # Prepare download
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        # Create download link
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="invoice_{inv_data["invoice_number"]}.pdf">📄 Click here to download Invoice PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Professional invoice PDF generated successfully!")
        
    except ImportError as e:
        st.error("❌ ReportLab library is not installed!")
        st.info("💡 To fix this, install reportlab: `pip install reportlab`")
        st.code("pip install reportlab")
        
    except Exception as e:
        st.error(f"❌ Error generating invoice PDF: {str(e)}")
        st.info("💡 Invoice PDF generation failed. Please check the error details above.")

def show_full_financial_interface():
    """Full financial interface for admin and regular users - UPDATED WITH PROFIT SHARING"""
    
    # Tab navigation - UPDATED with Profit Sharing tab
    # Tab navigation - ENHANCED WITH INVOICE MANAGEMENT
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Financial Overview", 
        "📋 Initial Projections", 
        "💰 Final Costs",
        "📄 Invoice Management",  # NEW TAB
        "💸 Disbursements",
        "📈 Financial Reports"
    ])
    
    with tab1:
        show_financial_overview()
    
    with tab2:
        show_initial_projections()
    
    with tab3:
        show_final_costs()
    
    with tab4:  # NEW TAB
        show_invoice_management()
    
    with tab5:  # Updated number
        show_disbursement_management()
    
    with tab6:  # Updated number
        show_financial_reports()

# Finance user interface remains the same (no profit sharing access for finance users)
def show_finance_user_interface():
    """Limited interface for finance users"""
    
    st.info("🔒 **Finance User Access**: You can view and edit Initial Financial Projections and Final Financial Cost (real cost column only).")
    
    # Tab navigation for finance users - NO PROFIT SHARING ACCESS
    tab1, tab2 = st.tabs(["📋 Initial Projections", "💰 Final Costs"])
    
    with tab1:
        show_initial_projections()
    
    with tab2:
        show_final_costs()

def show_profit_sharing():
    """Show profit sharing management"""
    st.subheader("🤝 Profit Sharing Management")
    
    user = AuthenticationManager.get_current_user()
    
    # Only admin and regular users can access profit sharing
    if user['role'] == 'finance':
        st.error("🔒 Access denied. Profit sharing is only available to admin and regular users.")
        st.info("💡 Finance users can access Initial Projections and Final Costs only.")
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
    
    # Profit sharing management
    show_profit_sharing_management()

def show_profit_sharing_management():
    """Show profit sharing management interface"""
    
    # Get projects for profit sharing
    db_ops = DatabaseOperations()
    try:
        projects = db_ops.get_all_projects()
        
        if not projects:
            st.warning("⚠️ No projects found. Please create a project first.")
            return
        
        # Get profit sharing summary
        profit_summary = db_ops.get_profit_sharing_summary()
        
        # Show overview metrics
        st.markdown("### 📊 Profit Sharing Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Projects",
                profit_summary['total_projects']
            )
        
        with col2:
            st.metric(
                "With Profit Sharing",
                profit_summary['projects_with_profit_sharing']
            )
        
        with col3:
            st.metric(
                "Needs Configuration",
                profit_summary['projects_without_profit_sharing']
            )
        
        with col4:
            completion_rate = 0
            if profit_summary['total_projects'] > 0:
                completion_rate = (profit_summary['projects_with_profit_sharing'] / profit_summary['total_projects']) * 100
            
            st.metric(
                "Configuration Rate",
                f"{completion_rate:.0f}%"
            )
        
        # Categorize projects
        projects_with_configs = []
        projects_without_configs = []
        
        for project in projects:
            configs = db_ops.get_profit_sharing_configs_by_project(project.id)
            if configs:
                projects_with_configs.append((project, configs))
            else:
                projects_without_configs.append(project)
        
        # Section 1: Projects ready for profit sharing configuration
        if projects_without_configs:
            st.markdown("### 📋 Projects Ready for Profit Sharing Setup")
            st.info("💡 These projects don't have profit sharing configured yet.")
            
            for project in projects_without_configs:
                with st.expander(f"🚀 {project.project_name} - Setup Profit Sharing"):
                    
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
                        st.metric("Project Value", f"৳{project.final_po_value or 0:,.2f}")
                        if project.final_po_value:
                            # Get cost data to show potential profit
                            try:
                                final_costs = db_ops.get_final_costs_by_project(project.id)
                                total_cost = sum(f.real_cost for f in final_costs)
                                if total_cost > 0:
                                    potential_profit = project.final_po_value - total_cost
                                    st.metric("Potential Profit", f"৳{potential_profit:,.2f}")
                                else:
                                    # Use projected costs
                                    projections = db_ops.get_initial_projections_by_project(project.id)
                                    projected_cost = sum(p.amount for p in projections)
                                    if projected_cost > 0:
                                        potential_profit = project.final_po_value - projected_cost
                                        st.metric("Est. Profit", f"৳{potential_profit:,.2f}")
                            except:
                                pass
                    
                    with col3:
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("🎯 Setup Manual", key=f"manual_setup_{project.id}"):
                                st.session_state.profit_sharing_project_id = project.id
                                st.session_state.show_profit_sharing_form = True
                                st.rerun()
                        
                        with col_b:
                            if st.button("⚡ Copy Defaults", key=f"copy_defaults_{project.id}"):
                                # Copy default percentages from task descriptions
                                success, message = db_ops.copy_default_profit_sharing(project.id)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
        
        # Section 2: Projects with configured profit sharing
        if projects_with_configs:
            st.markdown("### 🤝 Projects with Profit Sharing Configuration")
            
            for project, configs in projects_with_configs:
                with st.expander(f"💼 {project.project_name} - {len(configs)} Configuration(s)"):
                    
                    # Validate percentages
                    validation = db_ops.validate_profit_sharing_percentages(project.id)
                    total_percentage = validation['total_percentage']
                    
                    # Project summary
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Project Value", f"৳{project.final_po_value or 0:,.2f}")
                    
                    with col2:
                        st.metric("Configurations", len(configs))
                    
                    with col3:
                        if validation['valid']:
                            st.metric("Total %", f"{total_percentage:.1f}%", delta="✅ Valid")
                        else:
                            st.metric("Total %", f"{total_percentage:.1f}%", delta="❌ Over 100%", delta_color="inverse")
                    
                    with col4:
                        if total_percentage < 100:
                            unallocated = 100 - total_percentage
                            st.metric("Unallocated", f"{unallocated:.1f}%")
                        else:
                            st.metric("Excess", f"{validation['excess_percentage']:.1f}%")
                    
                    # Configuration table
                    st.markdown("#### Profit Sharing Configuration")
                    config_data = []
                    
                    for config in configs:
                        config_data.append({
                            'Task': config.task_description.task_name,
                            'Assigned To': config.assigned_person_company,
                            'Percentage': f"{config.profit_percentage:.1f}%",
                            'Est. Amount': f"৳{(project.final_po_value or 0) * config.profit_percentage / 100:,.2f}" if project.final_po_value else "N/A"
                        })
                    
                    if config_data:
                        df = pd.DataFrame(config_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("✏️ Edit Config", key=f"edit_config_{project.id}"):
                            st.session_state.edit_profit_sharing_id = project.id
                            st.rerun()
                    
                    with col2:
                        if st.button("📊 Calculate Profit", key=f"calc_profit_{project.id}"):
                            st.session_state.show_profit_calculation = project.id
                            st.rerun()
                    
                    with col3:
                        if st.button("🔄 Reset Config", key=f"reset_config_{project.id}"):
                            st.session_state.reset_profit_config_id = project.id
                            st.rerun()
                    
                    with col4:
                        if st.button("📈 Analytics", key=f"analytics_{project.id}"):
                            st.info("Detailed analytics will be available in the next step.")
        
        # Handle reset confirmation
        if st.session_state.get('reset_profit_config_id'):
            project_to_reset = next((p for p in projects if p.id == st.session_state.reset_profit_config_id), None)
            if project_to_reset:
                st.warning(f"⚠️ Are you sure you want to reset profit sharing configuration for '{project_to_reset.project_name}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Reset", key="confirm_reset_config"):
                        db_ops.delete_profit_sharing_configs_by_project(st.session_state.reset_profit_config_id)
                        st.success("✅ Profit sharing configuration reset!")
                        del st.session_state.reset_profit_config_id
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key="cancel_reset_config"):
                        del st.session_state.reset_profit_config_id
                        st.rerun()
        
        # Show task analytics
        if profit_summary['projects_with_profit_sharing'] > 0:
            st.markdown("### 📈 Task Usage Analytics")
            
            task_analytics = db_ops.get_task_profit_analytics()
            
            if task_analytics:
                analytics_data = []
                for task in task_analytics:
                    analytics_data.append({
                        'Task': task['task_name'],
                        'Projects Using': task['usage_count'],
                        'Avg %': f"{task['avg_percentage']:.1f}%",
                        'Total %': f"{task['total_percentage']:.1f}%"
                    })
                
                df = pd.DataFrame(analytics_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No task analytics available yet.")
        
    except Exception as e:
        st.error(f"Error loading profit sharing: {str(e)}")
    finally:
        db_ops.close()

def show_profit_sharing_form():
    """Show profit sharing configuration form - UPDATED FOR CONSISTENCY"""
    st.subheader("🤝 Configure Profit Sharing")
    
    # Back button
    if st.button("⬅️ Back to Profit Sharing"):
        # Clear ALL session state variables - FIXED
        session_keys_to_clear = [
            'show_profit_sharing_form',
            'profit_sharing_project_id',
            'profit_sharing_configs'
        ]
        
        for key in session_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Get project ID
    project_id = st.session_state.get('profit_sharing_project_id')
    if not project_id:
        st.error("No project selected!")
        return
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        tasks = db_ops.get_all_task_descriptions_with_percentage()
        companies = db_ops.get_all_companies()
        
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
        with col3:
            st.info(f"**Project Value:** ৳{project.final_po_value or 0:,.2f}")
        
        # Instructions
        st.markdown("### 📝 Configure Profit Distribution")
        st.info("💡 Set profit sharing percentages for each task. You can assign different companies to different tasks and adjust percentages as needed.")
        
        # Initialize profit sharing configs in session state
        if 'profit_sharing_configs' not in st.session_state:
            st.session_state.profit_sharing_configs = []
            
            # Start with active tasks that have default percentages
            for task in tasks:
                if task.is_active:
                    default_percentage = getattr(task, 'default_percentage', 0.0)
                    if default_percentage > 0:
                        st.session_state.profit_sharing_configs.append({
                            'task_id': task.id,
                            'task_name': task.task_name,
                            'percentage': default_percentage,
                            'assigned_company': 'To be assigned'
                        })
            
            # If no tasks with defaults, add at least one empty config
            if not st.session_state.profit_sharing_configs:
                if tasks:
                    st.session_state.profit_sharing_configs.append({
                        'task_id': tasks[0].id,
                        'task_name': tasks[0].task_name,
                        'percentage': 0.0,
                        'assigned_company': 'To be assigned'
                    })
        
        # Display profit sharing configuration form
        show_profit_sharing_config_form(tasks, companies)
        
        # Calculate totals
        total_percentage = sum(config['percentage'] for config in st.session_state.profit_sharing_configs)
        estimated_profit = project.final_po_value or 0  # Simplified - will be enhanced with cost calculation
        total_amount = (estimated_profit * total_percentage) / 100
        
        # Show summary
        st.markdown("### 💰 Configuration Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Percentage", f"{total_percentage:.1f}%")
        
        with col2:
            remaining = 100 - total_percentage
            delta_color = "normal" if remaining >= 0 else "inverse"
            st.metric("Remaining", f"{remaining:.1f}%", delta_color=delta_color)
        
        with col3:
            st.metric("Est. Profit", f"৳{estimated_profit:,.2f}")
        
        with col4:
            st.metric("Est. Distribution", f"৳{total_amount:,.2f}")
        
        # Validation warnings
        if total_percentage > 100:
            st.error(f"⚠️ Total percentage ({total_percentage:.1f}%) exceeds 100%! Please adjust the percentages.")
        elif total_percentage < 100:
            st.warning(f"💡 {100 - total_percentage:.1f}% remains unallocated. Consider adding more configurations or adjusting percentages.")
        else:
            st.success("✅ Perfect! Total percentage equals 100%.")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Configuration", use_container_width=True):
                add_profit_sharing_config(tasks)
        
        with col2:
            if st.button("🔄 Reset All", use_container_width=True):
                reset_profit_sharing_configs()
        
        with col3:
            if st.button("💾 Save Configuration", use_container_width=True):
                save_profit_sharing_config(project_id)
        
        with col4:
            if st.button("📊 Preview Distribution", use_container_width=True):
                show_profit_distribution_preview(project, estimated_profit)
    
    except Exception as e:
        st.error(f"Error loading profit sharing form: {str(e)}")
    finally:
        db_ops.close()

def show_profit_sharing_config_form(tasks, companies):
    """Show profit sharing configuration form items"""
    
    # Company options for dropdown
    company_options = ["To be assigned"] + [c.name for c in companies]
    
    for i, config in enumerate(st.session_state.profit_sharing_configs):
        with st.container():
            st.markdown(f"#### Configuration {i + 1}")
            
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 1])
            
            with col1:
                # Task selection
                task_options = [(t.id, t.task_name) for t in tasks if t.is_active]
                current_task_index = next((idx for idx, (tid, _) in enumerate(task_options) if tid == config['task_id']), 0)
                
                selected_task = st.selectbox(
                    "Task",
                    options=task_options,
                    index=current_task_index,
                    format_func=lambda x: x[1],
                    key=f"task_{i}"
                )
                st.session_state.profit_sharing_configs[i]['task_id'] = selected_task[0]
                st.session_state.profit_sharing_configs[i]['task_name'] = selected_task[1]
            
            with col2:
                # Company assignment
                current_company_index = 0
                if config['assigned_company'] in company_options:
                    current_company_index = company_options.index(config['assigned_company'])
                
                assigned_company = st.selectbox(
                    "Assigned Company",
                    options=company_options,
                    index=current_company_index,
                    key=f"company_{i}",
                    help="Select which company gets this profit share"
                )
                st.session_state.profit_sharing_configs[i]['assigned_company'] = assigned_company
            
            with col3:
                # Percentage input
                percentage = st.number_input(
                    "Percentage (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=config['percentage'],
                    step=0.1,
                    key=f"percentage_{i}",
                    help="Profit percentage for this configuration"
                )
                st.session_state.profit_sharing_configs[i]['percentage'] = percentage
            
            with col4:
                # Show default percentage from task (if available)
                task_obj = next((t for t in tasks if t.id == config['task_id']), None)
                if task_obj:
                    default_pct = getattr(task_obj, 'default_percentage', 0.0)
                    if default_pct > 0:
                        st.caption(f"Default: {default_pct}%")
                        if st.button("↩️", key=f"use_default_{i}", help="Use default percentage"):
                            st.session_state.profit_sharing_configs[i]['percentage'] = default_pct
                            st.rerun()
                    else:
                        st.caption("No default")
            
            with col5:
                # Remove button
                if len(st.session_state.profit_sharing_configs) > 1:
                    if st.button("🗑️", key=f"remove_config_{i}", help="Remove this configuration"):
                        remove_profit_sharing_config(i)
                        st.rerun()
            
            st.markdown("---")

def add_profit_sharing_config(tasks):
    """Add a new profit sharing configuration"""
    if tasks:
        # Find a task not already used (if possible)
        used_task_ids = {config['task_id'] for config in st.session_state.profit_sharing_configs}
        available_tasks = [t for t in tasks if t.is_active and t.id not in used_task_ids]
        
        if available_tasks:
            task = available_tasks[0]
            default_percentage = getattr(task, 'default_percentage', 0.0)
        else:
            # Use first task if all are used
            task = tasks[0]
            default_percentage = 0.0
        
        st.session_state.profit_sharing_configs.append({
            'task_id': task.id,
            'task_name': task.task_name,
            'percentage': default_percentage,
            'assigned_company': 'To be assigned'
        })
        st.rerun()
def remove_profit_sharing_config(index):
    """Remove a profit sharing configuration"""
    if len(st.session_state.profit_sharing_configs) > 1:
        st.session_state.profit_sharing_configs.pop(index)

def reset_profit_sharing_configs():
    """Reset all profit sharing configurations"""
    if 'profit_sharing_configs' in st.session_state:
        del st.session_state.profit_sharing_configs
    st.success("✅ All configurations reset!")
    st.rerun()

def save_profit_sharing_config(project_id):
    """Save profit sharing configuration to database - FIXED VERSION"""
    
    if 'profit_sharing_configs' not in st.session_state or not st.session_state.profit_sharing_configs:
        st.error("No configurations to save!")
        return
    
    # Validate configurations
    total_percentage = sum(config['percentage'] for config in st.session_state.profit_sharing_configs)
    
    if total_percentage > 100:
        st.error(f"❌ Cannot save! Total percentage ({total_percentage:.1f}%) exceeds 100%.")
        return
    
    # Check for unassigned companies
    unassigned_configs = [config for config in st.session_state.profit_sharing_configs if config['assigned_company'] == 'To be assigned']
    if unassigned_configs:
        st.error(f"❌ Please assign companies to all configurations. {len(unassigned_configs)} configuration(s) are unassigned.")
        return
    
    # Check for zero percentages
    zero_configs = [config for config in st.session_state.profit_sharing_configs if config['percentage'] <= 0]
    if zero_configs:
        st.warning(f"⚠️ {len(zero_configs)} configuration(s) have 0% allocation. Is this correct?")
    
    db_ops = DatabaseOperations()
    try:
        # Delete existing configurations
        db_ops.delete_profit_sharing_configs_by_project(project_id)
        
        # Create new configurations
        for config in st.session_state.profit_sharing_configs:
            db_ops.create_profit_sharing_config(
                project_id=project_id,
                task_description_id=config['task_id'],
                profit_percentage=config['percentage'],
                assigned_person_company=config['assigned_company']
            )
        
        st.success(f"✅ Profit sharing configuration saved! {len(st.session_state.profit_sharing_configs)} configurations created.")
        st.balloons()
        
        # Clear ALL related session state variables - FIXED
        session_keys_to_clear = [
            'profit_sharing_configs',
            'show_profit_sharing_form', 
            'profit_sharing_project_id',
            'edit_profit_sharing_id'
        ]
        
        for key in session_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error saving configuration: {str(e)}")
    finally:
        db_ops.close()

def show_profit_distribution_preview(project, estimated_profit):
    """Show profit distribution preview"""
    st.markdown("### 📊 Profit Distribution Preview")
    
    # Group by company
    company_totals = {}
    for config in st.session_state.profit_sharing_configs:
        company = config['assigned_company']
        if company not in company_totals:
            company_totals[company] = {'percentage': 0, 'amount': 0, 'tasks': []}
        
        company_totals[company]['percentage'] += config['percentage']
        company_totals[company]['amount'] += (estimated_profit * config['percentage']) / 100
        company_totals[company]['tasks'].append(config['task_name'])
    
    # Display company breakdown
    for company, data in company_totals.items():
        with st.expander(f"🏢 {company} - {data['percentage']:.1f}% (৳{data['amount']:,.2f})"):
            st.markdown("**Tasks assigned:**")
            for task in data['tasks']:
                st.markdown(f"• {task}")
    
    # Summary chart (if plotly available)
    try:
        import plotly.graph_objects as go
        
        companies = list(company_totals.keys())
        percentages = [data['percentage'] for data in company_totals.values()]
        
        fig = go.Figure(data=[go.Pie(
            labels=companies,
            values=percentages,
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent}<br>৳%{value:,.0f}',
            hovertemplate='<b>%{label}</b><br>Percentage: %{percent}<br>Amount: ৳%{value:,.0f}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Profit Distribution by Company",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.info("Chart visualization not available")
        
def show_edit_profit_sharing_form(project_id):
    """Show edit profit sharing form - FIXED VERSION"""
    st.subheader("✏️ Edit Profit Sharing Configuration")
    
    # Back button
    if st.button("⬅️ Back to Profit Sharing"):
        # Clear ALL session state variables - FIXED
        session_keys_to_clear = [
            'edit_profit_sharing_id',
            'profit_sharing_configs',
            'profit_sharing_project_id'
        ]
        
        for key in session_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        existing_configs = db_ops.get_profit_sharing_configs_by_project(project_id)
        tasks = db_ops.get_all_task_descriptions_with_percentage()
        companies = db_ops.get_all_companies()
        
        if not project:
            st.error("Project not found!")
            return
        
        if not existing_configs:
            st.error("No existing configurations found!")
            return
        
        # Project information
        st.markdown(f"### 💼 Editing: {project.project_name}")
        
        st.info("📝 **Note:** This will replace the existing configuration. Make your changes and save.")
        
        # Load existing configs into session state (only once)
        if 'profit_sharing_configs' not in st.session_state:
            st.session_state.profit_sharing_configs = []
            for config in existing_configs:
                st.session_state.profit_sharing_configs.append({
                    'id': config.id,
                    'task_id': config.task_description_id,
                    'task_name': config.task_description.task_name,
                    'percentage': config.profit_percentage,
                    'assigned_company': config.assigned_person_company
                })
        
        # Show the same form as creation
        show_profit_sharing_config_form(tasks, companies)
        
        # Calculate totals
        total_percentage = sum(config['percentage'] for config in st.session_state.profit_sharing_configs)
        estimated_profit = project.final_po_value or 0
        
        # Show summary
        st.markdown("### 💰 Updated Configuration Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Percentage", f"{total_percentage:.1f}%")
        
        with col2:
            remaining = 100 - total_percentage
            delta_color = "normal" if remaining >= 0 else "inverse"
            st.metric("Remaining", f"{remaining:.1f}%", delta_color=delta_color)
        
        with col3:
            total_amount = (estimated_profit * total_percentage) / 100
            st.metric("Est. Distribution", f"৳{total_amount:,.2f}")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Configuration", use_container_width=True):
                add_profit_sharing_config(tasks)
        
        with col2:
            if st.button("🔄 Reset Changes", use_container_width=True):
                if 'profit_sharing_configs' in st.session_state:
                    del st.session_state.profit_sharing_configs
                st.rerun()
        
        with col3:
            if st.button("💾 Update Configuration", use_container_width=True):
                # Use the project_id parameter directly instead of session state
                save_profit_sharing_config(project_id)
        
        with col4:
            if st.button("❌ Cancel Edit", use_container_width=True):
                # Clear ALL session state variables - FIXED
                session_keys_to_clear = [
                    'edit_profit_sharing_id',
                    'profit_sharing_configs',
                    'profit_sharing_project_id'
                ]
                
                for key in session_keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading edit form: {str(e)}")
    finally:
        db_ops.close()

def show_profit_calculation(project_id):
    """Show comprehensive project profit calculation and analysis"""
    st.markdown("---")
    st.subheader("💰 Project Profit Calculation & Analysis")
    
    # Back button
    if st.button("⬅️ Back to Profit Sharing"):
        del st.session_state.show_profit_calculation
        st.rerun()
    
    db_ops = DatabaseOperations()
    try:
        # Get comprehensive profit calculation
        profit_data = db_ops.calculate_project_profit(project_id)
        
        if not profit_data:
            st.error("❌ Unable to calculate profit for this project.")
            st.info("💡 Make sure the project has financial data (projections, costs, or profit sharing configuration).")
            return
        
        project = profit_data['project']
        financial_summary = profit_data['financial_summary']
        disbursement_summary = profit_data['disbursement_summary']
        cash_flow = profit_data['cash_flow']
        profit_distribution = profit_data['profit_distribution']
        allocation_summary = profit_data['allocation_summary']
        metrics = profit_data['metrics']
        
        # Project Header
        st.markdown(f"### 💼 {project.project_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**PO:** {project.po_number or 'N/A'}")
        with col2:
            client_name = project.po_issuing_company.name if project.po_issuing_company else 'N/A'
            st.info(f"**Client:** {client_name}")
        with col3:
            st.info(f"**Status:** {project.status.title()}")
        
        # Financial Health Score
        health_score = metrics['financial_health_score']
        if health_score >= 80:
            health_color = "success"
            health_icon = "🟢"
            health_status = "Excellent"
        elif health_score >= 60:
            health_color = "normal"
            health_icon = "🟡"
            health_status = "Good"
        elif health_score >= 40:
            health_color = "normal"
            health_icon = "🟠"
            health_status = "Fair"
        else:
            health_color = "inverse"
            health_icon = "🔴"
            health_status = "Poor"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(90deg, #1f4e79, #2e86de); color: white; border-radius: 10px; margin: 1rem 0;">
            <h3>{health_icon} Financial Health Score: {health_score}/100 ({health_status})</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Financial Metrics
        st.markdown("### 📊 Key Financial Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Project Revenue",
                f"৳{financial_summary['total_revenue']:,.2f}",
                help="Final PO value after VAT and AIT"
            )
        
        with col2:
            cost_basis = financial_summary['cost_basis']
            cost_type = "Actual" if financial_summary['total_actual_cost'] > 0 else "Projected"
            st.metric(
                f"{cost_type} Costs",
                f"৳{cost_basis:,.2f}",
                delta=f"{financial_summary['cost_efficiency_percentage']:.1f}% of revenue",
                help=f"{'Actual costs from final cost tracking' if cost_type == 'Actual' else 'Projected costs from initial estimates'}"
            )
        
        with col3:
            gross_profit = financial_summary['gross_profit']
            profit_margin = financial_summary['profit_margin_percentage']
            delta_color = "normal" if gross_profit >= 0 else "inverse"
            st.metric(
                "Gross Profit",
                f"৳{gross_profit:,.2f}",
                delta=f"{profit_margin:+.1f}% margin",
                delta_color=delta_color,
                help="Revenue minus total costs"
            )
        
        with col4:
            operational_disbursed = disbursement_summary['operational_disbursements']
            st.metric(
                "Disbursed Amount",
                f"৳{operational_disbursed:,.2f}",
                delta=f"{cash_flow['collection_rate']:.1f}% collected",
                help="Total advance and project cost disbursements"
            )
        
        with col5:
            cash_balance = cash_flow['cash_flow_balance']
            st.metric(
                "Cash Balance",
                f"৳{cash_balance:,.2f}",
                delta="Remaining to collect" if cash_balance > 0 else "Fully collected",
                help="Revenue minus disbursed amounts"
            )
        
        # Profit Distribution Analysis
        if profit_distribution:
            st.markdown("### 🤝 Profit Distribution Analysis")
            
            # Distribution Summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Allocated",
                    f"{allocation_summary['total_percentage_allocated']:.1f}%",
                    delta=f"৳{allocation_summary['total_distributed']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "Unallocated",
                    f"{allocation_summary['unallocated_percentage']:.1f}%",
                    delta=f"৳{allocation_summary['unallocated_amount']:,.2f}"
                )
            
            with col3:
                config_count = len(profit_distribution)
                company_count = len(set(d['assigned_to'] for d in profit_distribution))
                st.metric(
                    "Configurations",
                    f"{config_count} tasks",
                    delta=f"{company_count} companies"
                )
            
            # Detailed Distribution Table
            st.markdown("#### 📋 Detailed Profit Distribution")
            
            distribution_data = []
            for dist in profit_distribution:
                distribution_data.append({
                    'Task': dist['task_name'],
                    'Assigned To': dist['assigned_to'],
                    'Percentage': f"{dist['percentage']:.1f}%",
                    'Profit Amount': f"৳{dist['amount']:,.2f}",
                    'Status': '✅ Configured'
                })
            
            # Add unallocated row if exists
            if allocation_summary['unallocated_percentage'] > 0:
                distribution_data.append({
                    'Task': '🔄 Unallocated Profit',
                    'Assigned To': 'To be assigned',
                    'Percentage': f"{allocation_summary['unallocated_percentage']:.1f}%",
                    'Profit Amount': f"৳{allocation_summary['unallocated_amount']:,.2f}",
                    'Status': '⚠️ Unassigned'
                })
            
            if distribution_data:
                df = pd.DataFrame(distribution_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Company-wise Summary
            st.markdown("#### 🏢 Company-wise Profit Summary")
            
            # Group by company
            company_profits = {}
            for dist in profit_distribution:
                company = dist['assigned_to']
                if company not in company_profits:
                    company_profits[company] = {
                        'total_percentage': 0,
                        'total_amount': 0,
                        'task_count': 0,
                        'tasks': []
                    }
                
                company_profits[company]['total_percentage'] += dist['percentage']
                company_profits[company]['total_amount'] += dist['amount']
                company_profits[company]['task_count'] += 1
                company_profits[company]['tasks'].append(dist['task_name'])
            
            for company, data in company_profits.items():
                with st.expander(f"🏢 {company} - {data['total_percentage']:.1f}% (৳{data['total_amount']:,.2f})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Percentage", f"{data['total_percentage']:.1f}%")
                        st.metric("Profit Amount", f"৳{data['total_amount']:,.2f}")
                    
                    with col2:
                        st.metric("Task Count", data['task_count'])
                        st.markdown("**Assigned Tasks:**")
                        for task in data['tasks']:
                            st.markdown(f"• {task}")
        
        else:
            st.warning("⚠️ No profit sharing configuration found for this project.")
            st.info("💡 Configure profit sharing to see detailed profit distribution analysis.")
        
        # Cost Analysis Section
        st.markdown("### 📈 Cost Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Cost Breakdown")
            
            projected_cost = financial_summary['total_projected_cost']
            actual_cost = financial_summary['total_actual_cost']
            
            if actual_cost > 0:
                variance = metrics['cost_variance']
                variance_pct = metrics['cost_variance_percentage']
                
                st.metric("Projected Costs", f"৳{projected_cost:,.2f}")
                st.metric(
                    "Actual Costs", 
                    f"৳{actual_cost:,.2f}",
                    delta=f"৳{variance:+,.2f} ({variance_pct:+.1f}%)",
                    delta_color="inverse" if variance > 0 else "normal"
                )
                
                if abs(variance_pct) > 10:
                    if variance_pct > 0:
                        st.error(f"🚨 Cost overrun of {variance_pct:.1f}%!")
                    else:
                        st.success(f"💰 Cost savings of {abs(variance_pct):.1f}%!")
                elif abs(variance_pct) > 5:
                    st.warning(f"⚠️ Cost variance of {variance_pct:+.1f}%")
                else:
                    st.success("✅ Costs are on track!")
            else:
                st.metric("Projected Costs", f"৳{projected_cost:,.2f}")
                st.info("💡 No actual costs recorded yet. Using projected costs for profit calculation.")
        
        with col2:
            st.markdown("#### 💸 Disbursement Breakdown")
            
            advance_amount = disbursement_summary['advance_disbursements']
            project_cost_amount = disbursement_summary['project_cost_disbursements']
            personal_loan_amount = disbursement_summary['personal_loan_disbursements']
            
            st.metric("Advance Disbursements", f"৳{advance_amount:,.2f}")
            st.metric("Project Cost Disbursements", f"৳{project_cost_amount:,.2f}")
            if personal_loan_amount > 0:
                st.metric("Personal Loans", f"৳{personal_loan_amount:,.2f}", help="Not included in profit calculation")
        
        # Visual Analytics Charts
        show_profit_analytics_charts(profit_data)
        
        # Detailed Analysis Section
        st.markdown("### 🔍 Detailed Analysis")
        
        # Create tabs for different analysis views
        tab1, tab2, tab3 = st.tabs(["📊 Financial Breakdown", "💸 Cash Flow Analysis", "📈 Performance Metrics"])
        
        with tab1:
            show_financial_breakdown_analysis(profit_data)
        
        with tab2:
            show_cash_flow_analysis(profit_data)
        
        with tab3:
            show_performance_metrics_analysis(profit_data)
        # Action Buttons
        st.markdown("### 📤 Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Generate Report", use_container_width=True):
                generate_profit_report(profit_data)
        
        with col2:
            if st.button("📧 Email Report", use_container_width=True):
                st.info("Email functionality will be implemented in later phases.")
        
        with col3:
            if st.button("💾 Export CSV", use_container_width=True):
                export_profit_data_csv(profit_data)
        
        with col4:
            if st.button("🔄 Refresh Calculation", use_container_width=True):
                st.rerun()
        # show_profit_recommendations(profit_data)
        
    except Exception as e:
        st.error(f"❌ Error loading profit calculation: {str(e)}")
        st.info("💡 Please check if the project has the required financial data.")
    finally:
        db_ops.close()

def generate_profit_report(profit_data):
    """Generate comprehensive profit report"""
    try:
        project = profit_data['project']
        financial_summary = profit_data['financial_summary']
        profit_distribution = profit_data['profit_distribution']
        allocation_summary = profit_data['allocation_summary']
        metrics = profit_data['metrics']
        
        # Create report content
        report_content = f"""
# PROJECT PROFIT ANALYSIS REPORT

## Project Information
- **Project Name:** {project.project_name}
- **PO Number:** {project.po_number or 'N/A'}
- **Client:** {project.po_issuing_company.name if project.po_issuing_company else 'N/A'}
- **Status:** {project.status.title()}
- **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Financial Summary
- **Total Revenue:** ৳{financial_summary['total_revenue']:,.2f}
- **Total Costs:** ৳{financial_summary['cost_basis']:,.2f}
- **Gross Profit:** ৳{financial_summary['gross_profit']:,.2f}
- **Profit Margin:** {financial_summary['profit_margin_percentage']:.2f}%
- **Financial Health Score:** {metrics['financial_health_score']}/100

## Profit Distribution
"""
        
        if profit_distribution:
            report_content += f"""
- **Total Allocated:** {allocation_summary['total_percentage_allocated']:.1f}% (৳{allocation_summary['total_distributed']:,.2f})
- **Unallocated:** {allocation_summary['unallocated_percentage']:.1f}% (৳{allocation_summary['unallocated_amount']:,.2f})

### Detailed Distribution:
"""
            for dist in profit_distribution:
                report_content += f"- **{dist['task_name']}** → {dist['assigned_to']}: {dist['percentage']:.1f}% (৳{dist['amount']:,.2f})\n"
        else:
            report_content += "- No profit sharing configuration found\n"
        
        # Display report
        st.markdown("### 📋 Generated Profit Report")
        st.markdown(report_content)
        
        # Download option
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=report_content,
            file_name=f"profit_report_{project.project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )
        
        st.success("✅ Profit report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error generating report: {str(e)}")

def export_profit_data_csv(profit_data):
    """Export profit data to CSV format"""
    try:
        project = profit_data['project']
        profit_distribution = profit_data['profit_distribution']
        financial_summary = profit_data['financial_summary']
        disbursement_summary = profit_data['disbursement_summary']
        
        # Prepare CSV data
        csv_data = []
        
        # Add project summary row
        csv_data.append({
            'Type': 'PROJECT_SUMMARY',
            'Description': project.project_name,
            'Company': project.po_issuing_company.name if project.po_issuing_company else 'N/A',
            'Amount': financial_summary['total_revenue'],
            'Percentage': 100.0,
            'Category': 'Revenue'
        })
        
        # Add cost summary
        csv_data.append({
            'Type': 'COST_SUMMARY',
            'Description': 'Total Project Costs',
            'Company': 'Internal',
            'Amount': financial_summary['cost_basis'],
            'Percentage': (financial_summary['cost_basis'] / financial_summary['total_revenue'] * 100) if financial_summary['total_revenue'] > 0 else 0,
            'Category': 'Cost'
        })
        
        # Add gross profit
        csv_data.append({
            'Type': 'GROSS_PROFIT',
            'Description': 'Gross Profit',
            'Company': 'Internal',
            'Amount': financial_summary['gross_profit'],
            'Percentage': financial_summary['profit_margin_percentage'],
            'Category': 'Profit'
        })
        
        # Add profit distribution
        for dist in profit_distribution:
            csv_data.append({
                'Type': 'PROFIT_DISTRIBUTION',
                'Description': dist['task_name'],
                'Company': dist['assigned_to'],
                'Amount': dist['amount'],
                'Percentage': dist['percentage'],
                'Category': 'Distribution'
            })
        
        # Add disbursement summary
        if disbursement_summary['advance_disbursements'] > 0:
            csv_data.append({
                'Type': 'DISBURSEMENT',
                'Description': 'Advance Disbursements',
                'Company': 'Various',
                'Amount': disbursement_summary['advance_disbursements'],
                'Percentage': (disbursement_summary['advance_disbursements'] / financial_summary['total_revenue'] * 100) if financial_summary['total_revenue'] > 0 else 0,
                'Category': 'Disbursement'
            })
        
        if disbursement_summary['project_cost_disbursements'] > 0:
            csv_data.append({
                'Type': 'DISBURSEMENT',
                'Description': 'Project Cost Disbursements',
                'Company': 'Various',
                'Amount': disbursement_summary['project_cost_disbursements'],
                'Percentage': (disbursement_summary['project_cost_disbursements'] / financial_summary['total_revenue'] * 100) if financial_summary['total_revenue'] > 0 else 0,
                'Category': 'Disbursement'
            })
        
        # Convert to DataFrame and CSV
        df = pd.DataFrame(csv_data)
        csv_string = df.to_csv(index=False)
        
        # Download button
        st.download_button(
            label="📥 Download Profit Data (CSV)",
            data=csv_string,
            file_name=f"profit_data_{project.project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Show preview
        st.markdown("### 📊 CSV Data Preview")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.success("✅ CSV export prepared successfully!")
        
    except Exception as e:
        st.error(f"❌ Error exporting CSV: {str(e)}")

def show_profit_analytics_charts(profit_data):
    """Show visual analytics charts for profit data"""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        
        financial_summary = profit_data['financial_summary']
        profit_distribution = profit_data['profit_distribution']
        disbursement_summary = profit_data['disbursement_summary']
        
        st.markdown("### 📊 Visual Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue vs Cost vs Profit Chart
            st.markdown("#### 💰 Financial Overview")
            
            categories = ['Revenue', 'Costs', 'Gross Profit']
            amounts = [
                financial_summary['total_revenue'],
                financial_summary['cost_basis'],
                financial_summary['gross_profit']
            ]
            colors = ['#28a745', '#dc3545', '#007bff']
            
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=amounts,
                    marker_color=colors,
                    text=[f"৳{amt:,.0f}" for amt in amounts],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Revenue vs Costs vs Profit",
                yaxis_title="Amount (৳)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Profit Distribution Pie Chart
            if profit_distribution:
                st.markdown("#### 🤝 Profit Distribution")
                
                companies = [d['assigned_to'] for d in profit_distribution]
                amounts = [d['amount'] for d in profit_distribution]
                
                # Add unallocated if exists
                unallocated = profit_data['allocation_summary']['unallocated_amount']
                if unallocated > 0:
                    companies.append('Unallocated')
                    amounts.append(unallocated)
                
                fig = go.Figure(data=[go.Pie(
                    labels=companies,
                    values=amounts,
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{percent}<br>৳%{value:,.0f}'
                )])
                
                fig.update_layout(
                    title="Profit Distribution by Company",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No profit distribution data to visualize")
        
        # Disbursement Analysis
        if any(disbursement_summary.values()):
            st.markdown("#### 💸 Disbursement Analysis")
            
            disb_types = []
            disb_amounts = []
            
            if disbursement_summary['advance_disbursements'] > 0:
                disb_types.append('Advance')
                disb_amounts.append(disbursement_summary['advance_disbursements'])
            
            if disbursement_summary['project_cost_disbursements'] > 0:
                disb_types.append('Project Cost')
                disb_amounts.append(disbursement_summary['project_cost_disbursements'])
            
            if disbursement_summary['personal_loan_disbursements'] > 0:
                disb_types.append('Personal Loan')
                disb_amounts.append(disbursement_summary['personal_loan_disbursements'])
            
            if disb_types:
                fig = go.Figure(data=[
                    go.Bar(
                        x=disb_types,
                        y=disb_amounts,
                        marker_color=['#ffc107', '#17a2b8', '#6c757d'],
                        text=[f"৳{amt:,.0f}" for amt in disb_amounts],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title="Disbursements by Type",
                    yaxis_title="Amount (৳)",
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.info("Charts not available: Advanced visualization requires additional setup")

def show_financial_breakdown_analysis(profit_data):
    """Show detailed financial breakdown analysis"""
    financial_summary = profit_data['financial_summary']
    disbursement_summary = profit_data['disbursement_summary']
    metrics = profit_data['metrics']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Revenue & Cost Analysis")
        
        revenue = financial_summary['total_revenue']
        cost_basis = financial_summary['cost_basis']
        gross_profit = financial_summary['gross_profit']
        
        # Create a breakdown table
        breakdown_data = [
            {"Category": "Project Revenue", "Amount": f"৳{revenue:,.2f}", "Percentage": "100.0%"},
            {"Category": "Total Costs", "Amount": f"৳{cost_basis:,.2f}", "Percentage": f"{(cost_basis/revenue*100) if revenue > 0 else 0:.1f}%"},
            {"Category": "Gross Profit", "Amount": f"৳{gross_profit:,.2f}", "Percentage": f"{financial_summary['profit_margin_percentage']:.1f}%"}
        ]
        
        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Cost efficiency analysis
        cost_efficiency = financial_summary['cost_efficiency_percentage']
        if cost_efficiency < 70:
            st.success(f"✅ Excellent cost efficiency: {cost_efficiency:.1f}%")
        elif cost_efficiency < 80:
            st.info(f"ℹ️ Good cost efficiency: {cost_efficiency:.1f}%")
        elif cost_efficiency < 90:
            st.warning(f"⚠️ Fair cost efficiency: {cost_efficiency:.1f}%")
        else:
            st.error(f"🚨 Poor cost efficiency: {cost_efficiency:.1f}%")
    
    with col2:
        st.markdown("#### 📊 Cost Variance Analysis")
        
        if financial_summary['total_actual_cost'] > 0:
            projected = financial_summary['total_projected_cost']
            actual = financial_summary['total_actual_cost']
            variance = metrics['cost_variance']
            variance_pct = metrics['cost_variance_percentage']
            
            variance_data = [
                {"Type": "Projected Costs", "Amount": f"৳{projected:,.2f}"},
                {"Type": "Actual Costs", "Amount": f"৳{actual:,.2f}"},
                {"Type": "Variance", "Amount": f"৳{variance:+,.2f} ({variance_pct:+.1f}%)"}
            ]
            
            df = pd.DataFrame(variance_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Variance insights
            if abs(variance_pct) <= 5:
                st.success("✅ Cost variance is within acceptable range (±5%)")
            elif abs(variance_pct) <= 10:
                st.warning("⚠️ Cost variance is moderate (5-10%)")
            else:
                st.error("🚨 Significant cost variance (>10%) - requires attention")
        else:
            st.info("💡 No actual cost data available. Using projected costs for analysis.")
            
            # Show projected cost breakdown if available
            raw_data = profit_data['raw_data']
            if raw_data['initial_projections']:
                st.markdown("**Projected Cost Items:**")
                for proj in raw_data['initial_projections'][:5]:  # Show first 5 items
                    st.markdown(f"• {proj.particulars}: ৳{proj.amount:,.2f}")
                
                if len(raw_data['initial_projections']) > 5:
                    st.caption(f"... and {len(raw_data['initial_projections']) - 5} more items")

def show_cash_flow_analysis(profit_data):
    """Show cash flow analysis"""
    cash_flow = profit_data['cash_flow']
    disbursement_summary = profit_data['disbursement_summary']
    financial_summary = profit_data['financial_summary']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💳 Cash Flow Summary")
        
        total_revenue = financial_summary['total_revenue']
        total_collected = cash_flow['total_collected']
        cash_balance = cash_flow['cash_flow_balance']
        collection_rate = cash_flow['collection_rate']
        
        cash_flow_data = [
            {"Item": "Total Project Revenue", "Amount": f"৳{total_revenue:,.2f}"},
            {"Item": "Amount Collected", "Amount": f"৳{total_collected:,.2f}"},
            {"Item": "Remaining Balance", "Amount": f"৳{cash_balance:,.2f}"},
            {"Item": "Collection Rate", "Amount": f"{collection_rate:.1f}%"}
        ]
        
        df = pd.DataFrame(cash_flow_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Cash flow status
        if collection_rate >= 90:
            st.success("✅ Excellent cash collection rate")
        elif collection_rate >= 70:
            st.info("ℹ️ Good cash collection rate")
        elif collection_rate >= 50:
            st.warning("⚠️ Moderate cash collection rate")
        else:
            st.error("🚨 Low cash collection rate - follow up required")
    
    with col2:
        st.markdown("#### 💸 Disbursement Breakdown")
        
        advance = disbursement_summary['advance_disbursements']
        project_cost = disbursement_summary['project_cost_disbursements']
        personal_loan = disbursement_summary['personal_loan_disbursements']
        total_disb = disbursement_summary['total_disbursements']
        
        disbursement_data = []
        
        if advance > 0:
            disbursement_data.append({"Type": "Advance Disbursements", "Amount": f"৳{advance:,.2f}", "Percentage": f"{(advance/total_disb*100) if total_disb > 0 else 0:.1f}%"})
        
        if project_cost > 0:
            disbursement_data.append({"Type": "Project Cost Disbursements", "Amount": f"৳{project_cost:,.2f}", "Percentage": f"{(project_cost/total_disb*100) if total_disb > 0 else 0:.1f}%"})
        
        if personal_loan > 0:
            disbursement_data.append({"Type": "Personal Loans", "Amount": f"৳{personal_loan:,.2f}", "Percentage": f"{(personal_loan/total_disb*100) if total_disb > 0 else 0:.1f}%"})
        
        if disbursement_data:
            df = pd.DataFrame(disbursement_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Disbursement insights
            operational_disb = advance + project_cost
            if operational_disb > 0:
                disb_efficiency = (operational_disb / total_revenue * 100) if total_revenue > 0 else 0
                st.metric("Operational Disbursement Rate", f"{disb_efficiency:.1f}%")
                
                if disb_efficiency > 80:
                    st.error("🚨 High disbursement rate - monitor cash flow")
                elif disb_efficiency > 60:
                    st.warning("⚠️ Moderate disbursement rate")
                else:
                    st.success("✅ Healthy disbursement rate")
        else:
            st.info("No disbursements recorded for this project")

def show_performance_metrics_analysis(profit_data):
    """Show performance metrics analysis"""
    metrics = profit_data['metrics']
    financial_summary = profit_data['financial_summary']
    allocation_summary = profit_data['allocation_summary']
    
    st.markdown("#### 🎯 Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Financial Health Score breakdown
        health_score = metrics['financial_health_score']
        st.metric("Financial Health Score", f"{health_score}/100")
        
        # Health score interpretation
        if health_score >= 80:
            st.success("🟢 Excellent financial health")
            health_feedback = "Project shows strong profitability and cost control"
        elif health_score >= 60:
            st.info("🟡 Good financial health")
            health_feedback = "Project is performing well with minor areas for improvement"
        elif health_score >= 40:
            st.warning("🟠 Fair financial health")
            health_feedback = "Project needs attention in cost management or profit allocation"
        else:
            st.error("🔴 Poor financial health")
            health_feedback = "Project requires immediate review and corrective action"
        
        st.caption(health_feedback)
    
    with col2:
        # Profit efficiency metrics
        profit_margin = financial_summary['profit_margin_percentage']
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
        
        # Profit margin benchmarks
        if profit_margin >= 25:
            st.success("🌟 Exceptional profit margin")
        elif profit_margin >= 15:
            st.success("✅ Excellent profit margin")
        elif profit_margin >= 10:
            st.info("ℹ️ Good profit margin")
        elif profit_margin >= 5:
            st.warning("⚠️ Acceptable profit margin")
        elif profit_margin > 0:
            st.warning("⚠️ Low profit margin")
        else:
            st.error("🚨 Project is not profitable")
    
    with col3:
        # Allocation efficiency
        allocation_rate = allocation_summary['total_percentage_allocated']
        st.metric("Profit Allocation", f"{allocation_rate:.1f}%")
        
        # Allocation completeness
        if allocation_rate >= 95:
            st.success("✅ Fully allocated")
        elif allocation_rate >= 80:
            st.info("ℹ️ Well allocated")
        elif allocation_rate >= 60:
            st.warning("⚠️ Partially allocated")
        else:
            st.error("🚨 Poorly allocated")
    
    # Performance insights
    st.markdown("#### 💡 Performance Insights")
    
    insights = []
    
    # Profitability insights
    if profit_margin >= 20:
        insights.append("🌟 **Excellent Profitability**: This project shows outstanding profit margins.")
    elif profit_margin <= 5:
        insights.append("⚠️ **Low Profitability**: Consider reviewing costs or pricing strategy.")
    
    # Cost control insights
    cost_efficiency = financial_summary['cost_efficiency_percentage']
    if cost_efficiency <= 70:
        insights.append("✅ **Good Cost Control**: Costs are well managed relative to revenue.")
    elif cost_efficiency >= 90:
        insights.append("🚨 **High Cost Ratio**: Costs are consuming most of the revenue.")
    
    # Allocation insights
    if allocation_rate < 80:
        unallocated_amount = allocation_summary['unallocated_amount']
        insights.append(f"💰 **Unallocated Profit**: ৳{unallocated_amount:,.2f} ({100-allocation_rate:.1f}%) is not yet allocated.")
    
    # Cash flow insights
    cash_flow_balance = profit_data['cash_flow']['cash_flow_balance']
    if cash_flow_balance > financial_summary['total_revenue'] * 0.3:
        insights.append("💳 **Strong Cash Position**: Significant funds remaining to be collected.")
    elif cash_flow_balance < 0:
        insights.append("⚠️ **Over-disbursed**: More money has been disbursed than the project revenue.")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("ℹ️ No specific insights available. Project metrics are within normal ranges.")

# def show_profit_recommendations(profit_data):
#     """Show actionable recommendations based on profit analysis"""
#     st.markdown("### 💡 Recommendations")
    
#     financial_summary = profit_data['financial_summary']
#     allocation_summary = profit_data['allocation_summary']
#     metrics = profit_data['metrics']
#     cash_flow = profit_data['cash_flow']
    
#     recommendations = []
    
#     # Profitability recommendations
#     profit_margin = financial_summary['profit_margin_percentage']
#     if profit_margin < 10:
#         recommendations.append({
#             'type': 'warning',
#             'title': 'Improve Profitability',
#             'description': 'Consider reviewing pricing strategy or reducing costs to improve profit margins.',
#             'actions': ['Review project scope', 'Optimize resource allocation', 'Negotiate better rates']
#         })
#     elif profit_margin > 30:
#         recommendations.append({
#             'type': 'success',
#             'title': 'Replicate Success',
#             'description': 'This project shows excellent profitability. Apply these practices to other projects.',
#             'actions': ['Document best practices', 'Train team on successful methods', 'Use as template for future projects']
#         })
    
#     # Cost control recommendations
#     if financial_summary['total_actual_cost'] > 0:
#         variance_pct = metrics['cost_variance_percentage']
#         if abs(variance_pct) > 15:
#             recommendations.append({
#                 'type': 'error',
#                 'title': 'Cost Control Issues',
#                 'description': f'Significant cost variance of {variance_pct:+.1f}% indicates poor cost estimation or control.',
#                 'actions': ['Review cost estimation process', 'Implement better cost tracking', 'Conduct variance analysis']
#             })
    
#     # Allocation recommendations
#     if allocation_summary['unallocated_percentage'] > 20:
#         recommendations.append({
#             'type': 'info',
#             'title': 'Complete Profit Allocation',
#             'description': f'{allocation_summary["unallocated_percentage"]:.1f}% of profit remains unallocated.',
#             'actions': ['Configure remaining profit sharing', 'Assign tasks to team members', 'Review profit distribution strategy']
#         })
    
#     # Cash flow recommendations
#     collection_rate = cash_flow['collection_rate']
#     if collection_rate < 70:
#         recommendations.append({
#             'type': 'warning',
#             'title': 'Improve Cash Collection',
#             'description': f'Low collection rate of {collection_rate:.1f}% may indicate cash flow issues.',
#             'actions': ['Follow up on pending collections', 'Review disbursement policies', 'Implement milestone-based payments']
#         })
    
#     # Display recommendations
#     if recommendations:
#         for i, rec in enumerate(recommendations):
#             if rec['type'] == 'success':
#                 st.success(f"✅ **{rec['title']}**: {rec['description']}")
#             elif rec['type'] == 'warning':
#                 st.warning(f"⚠️ **{rec['title']}**: {rec['description']}")
#             elif rec['type'] == 'error':
#                 st.error(f"🚨 **{rec['title']}**: {rec['description']}")
#             else:
#                 st.info(f"💡 **{rec['title']}**: {rec['description']}")
            
#             with st.expander(f"Suggested Actions for: {rec['title']}"):
#                 for action in rec['actions']:
#                     st.markdown(f"• {action}")
#     else:
#         st.success("✅ **All Good!** This project shows healthy financial metrics with no immediate concerns.")
        
#     # General best practices
#     with st.expander("📚 General Best Practices"):
#         st.markdown("""
#         **Financial Management Best Practices:**
#         - Regularly update actual costs to maintain accurate profit calculations
#         - Monitor cash flow and collection rates weekly
#         - Review profit allocation quarterly to ensure fair distribution
#         - Document lessons learned for future project improvements
#         - Maintain clear communication with all stakeholders about financial status
        
#         **Red Flags to Watch:**
#         - Profit margins below 5%
#         - Cost variances exceeding 10%
#         - Collection rates below 70%
#         - More than 30% unallocated profit
#         """)

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

# Step 1: Replace the show_disbursement_form() function in modules/financial.py

def show_disbursement_form():
    """Fixed disbursement creation form with dynamic project selection"""
    st.subheader("💸 Create New Disbursement")
    
    # Back button
    if st.button("⬅️ Back to Disbursements"):
        del st.session_state.show_disbursement_form
        # Clear any selection state
        if 'selected_disbursement_project_id' in st.session_state:
            del st.session_state.selected_disbursement_project_id
        st.rerun()
    
    # Step 1: Disbursement Type Selection (outside form)
    st.markdown("### 📋 Step 1: Select Disbursement Type")
    
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
    
    # Step 2: Project Selection (outside form, only for project-related disbursements)
    selected_project_id = None
    if disbursement_type != "personal_loan":
        st.markdown("### 📋 Step 2: Select Project")
        
        projects = get_projects_for_disbursement()
        if not projects:
            st.error("❌ No projects available for disbursement!")
            return
        
        # Project selection with dynamic update
        selected_project = st.selectbox(
            "Select Project *",
            options=[(p.id, f"{p.project_name} (PO: {p.po_number or 'N/A'})") for p in projects],
            format_func=lambda x: x[1],
            key="disbursement_project_selector"
        )
        selected_project_id = selected_project[0]
        
        # Show advance information dynamically (outside form)
        if disbursement_type == "advance":
            st.markdown("### 💰 Advance Information")
            show_advance_info_dynamic(selected_project_id)
    else:
        st.markdown("### 💡 Personal Loan Information")
        st.info("Personal loans are not linked to specific projects and don't affect project budgets.")
    
    # Step 3: Disbursement Details Form
    st.markdown("### 📋 Step 3: Disbursement Details")
    
    with st.form("new_disbursement_form"):
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
        
        # Money Receipt Information
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
            
            if disbursement_type != "personal_loan" and not selected_project_id:
                st.error("❌ Please select a project!")
                return
            
            # Validate advance disbursement
            if disbursement_type == "advance" and selected_project_id:
                validation_result = validate_advance_disbursement(selected_project_id, amount)
                if not validation_result['valid']:
                    st.error(validation_result['message'])
                    return
            
            # Combine date and time
            disbursement_datetime = datetime.combine(disbursement_date, disbursement_time)
            
            # Create disbursement
            if disbursement_type in ["advance", "project_cost"]:
                create_disbursement_with_companies(
                    project_id=selected_project_id,
                    disbursement_type=disbursement_type,
                    amount=amount,
                    disbursement_date=disbursement_datetime,
                    description=description,
                    received_from_company_id=received_from_company_id,
                    received_by_company_id=received_by_company_id
                )
            else:
                create_disbursement(
                    project_id=selected_project_id,
                    disbursement_type=disbursement_type,
                    amount=amount,
                    disbursement_date=disbursement_datetime,
                    description=description,
                    received_from=received_from,
                    received_by=received_by
                )

# Step 2: Add this new function to modules/financial.py

def show_advance_info_dynamic(project_id):
    """Show advance information that updates dynamically when project changes"""
    db_ops = DatabaseOperations()
    try:
        project = db_ops.get_project_by_id(project_id)
        if project:
            advance_info = db_ops.get_project_advance_summary(project_id)
            
            if project.project_advance_amount and project.project_advance_amount > 0:
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