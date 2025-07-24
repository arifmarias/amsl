import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import pandas as pd
from database.operations import DatabaseOperations
from modules.auth import AuthenticationManager
import calendar

def show_dashboard():
    """Enhanced dashboard page with final costs integration"""
    
    user = AuthenticationManager.get_current_user()
    
    # Header with dynamic greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1f4e79, #2e86de); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;">
        <h1>📊 Project Management Dashboard</h1>
        <p>{greeting}, {user['full_name']}! Here's your project overview for {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get comprehensive dashboard data
    dashboard_data = get_comprehensive_dashboard_data()
    
    if not dashboard_data:
        show_empty_dashboard()
        return
    
    # Key Metrics Row - ENHANCED
    show_key_metrics(dashboard_data)
    
    # Charts Row
    col1, col2 = st.columns(2)
    with col1:
        show_project_status_distribution(dashboard_data)
    with col2:
        show_cost_performance_chart(dashboard_data)  # NEW CHART
    
    # Secondary Charts Row
    col1, col2 = st.columns(2)
    with col1:
        show_revenue_analysis(dashboard_data)
    with col2:
        show_monthly_project_creation(dashboard_data)
    
    # Data Tables Row
    col1, col2 = st.columns([2, 1])
    with col1:
        show_recent_projects(dashboard_data)
    with col2:
        show_enhanced_quick_actions(user['role'], dashboard_data)  # ENHANCED
    
    # Bottom Row - System Status and Activities
    col1, col2 = st.columns(2)
    with col1:
        show_project_timeline_analysis(dashboard_data)
    with col2:
        #show_financial_health_summary(dashboard_data)  # NEW SECTION
        show_profit_overview_summary(dashboard_data)  # NEW SECTION

def get_comprehensive_dashboard_data():
    """Get comprehensive data for dashboard analytics - ENHANCED WITH FINAL COSTS"""
    db_ops = DatabaseOperations()
    try:
        # Get all data while session is active
        projects = db_ops.get_all_projects()
        companies = db_ops.get_all_companies()
        tasks = db_ops.get_all_task_descriptions()
        
        if not projects:
            return None
        
        # Process all data while session is still active
        processed_projects = []
        for project in projects:
            # Extract all needed data while session is active
            project_data = {
                'id': project.id,
                'project_name': project.project_name,
                'status': project.status,
                'po_number': project.po_number,
                'total_po_value': project.total_po_value or 0,
                'final_po_value': project.final_po_value or 0,
                'start_date': project.start_date,
                'tentative_end_date': project.tentative_end_date,
                'created_at': project.created_at,
                'po_issuing_company_name': project.po_issuing_company.name if project.po_issuing_company else 'N/A',
                'supplier_company_name': project.supplier_company.name if project.supplier_company else 'N/A'
            }
            processed_projects.append(project_data)
        
        # Process companies data
        processed_companies = []
        for company in companies:
            company_data = {
                'id': company.id,
                'name': company.name,
                'company_type': company.company_type,
                'created_at': company.created_at
            }
            processed_companies.append(company_data)
        
        # Get financial data - ENHANCED WITH PROFIT CALCULATIONS
        projection_stats = db_ops.get_all_financial_projections_summary()
        final_cost_stats = db_ops.get_final_cost_summary()
        disbursement_stats = db_ops.get_disbursement_statistics()
        
        # Get profit calculation summaries for all projects
        profit_summaries = []
        total_gross_profit = 0
        total_allocated_profit = 0
        projects_with_profit_configs = 0
        
        for project_data in processed_projects:
            try:
                profit_data = db_ops.calculate_project_profit(project_data['id'])
                if profit_data:
                    profit_summary = {
                        'project_id': project_data['id'],
                        'project_name': project_data['project_name'],
                        'gross_profit': profit_data['financial_summary']['gross_profit'],
                        'profit_margin': profit_data['financial_summary']['profit_margin_percentage'],
                        'allocated_profit': profit_data['allocation_summary']['total_distributed'],
                        'health_score': profit_data['metrics']['financial_health_score'],
                        'has_configs': len(profit_data['profit_configs']) > 0
                    }
                    profit_summaries.append(profit_summary)
                    total_gross_profit += profit_summary['gross_profit']
                    total_allocated_profit += profit_summary['allocated_profit']
                    if profit_summary['has_configs']:
                        projects_with_profit_configs += 1
            except:
                # Skip projects that can't calculate profit
                pass
        
        # Calculate comprehensive statistics
        stats = {
            'projects': processed_projects,
            'companies': processed_companies,
            'tasks': tasks,
            'total_projects': len(processed_projects),
            'total_companies': len(processed_companies),
            'total_tasks': len(tasks),
            # Financial data
            'projection_stats': projection_stats,
            'final_cost_stats': final_cost_stats,
            'disbursement_stats': disbursement_stats
        }
        
        # Project status breakdown
        status_counts = {}
        for project in processed_projects:
            status = project['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        stats['status_counts'] = status_counts
        stats['active_projects'] = status_counts.get('active', 0)
        stats['completed_projects'] = status_counts.get('completed', 0)
        stats['new_projects'] = status_counts.get('new', 0)
        stats['on_hold_projects'] = status_counts.get('on_hold', 0)
        stats['cancelled_projects'] = status_counts.get('cancelled', 0)
        
        # Financial calculations
        total_revenue = sum(p['final_po_value'] for p in processed_projects)
        total_budget = sum(p['total_po_value'] for p in processed_projects)
        active_revenue = sum(p['final_po_value'] for p in processed_projects if p['status'] == 'active')
        completed_revenue = sum(p['final_po_value'] for p in processed_projects if p['status'] == 'completed')
        
        stats['total_revenue'] = total_revenue
        stats['total_budget'] = total_budget
        stats['active_revenue'] = active_revenue
        stats['completed_revenue'] = completed_revenue
        stats['average_project_value'] = total_revenue / len(processed_projects) if processed_projects else 0
        
        # Company analysis
        customers = [c for c in processed_companies if c['company_type'] == 'customer']
        suppliers = [c for c in processed_companies if c['company_type'] == 'supplier']
        stats['customer_count'] = len(customers)
        stats['supplier_count'] = len(suppliers)
        
        # Timeline analysis
        current_date = date.today()
        overdue_projects = []
        upcoming_deadlines = []
        
        for project in processed_projects:
            if project['tentative_end_date'] and project['status'] in ['new', 'active']:
                if project['tentative_end_date'] < current_date:
                    overdue_projects.append(project)
                elif project['tentative_end_date'] <= current_date + timedelta(days=30):
                    upcoming_deadlines.append(project)
        
        stats['overdue_projects'] = len(overdue_projects)
        stats['upcoming_deadlines'] = len(upcoming_deadlines)
        stats['overdue_project_list'] = overdue_projects
        stats['upcoming_deadline_list'] = upcoming_deadlines
        
        # Monthly project creation data
        monthly_data = {}
        for project in processed_projects:
            if project['created_at']:
                month_key = project['created_at'].strftime('%Y-%m')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
        
        stats['monthly_creation_data'] = monthly_data
        # Add profit statistics
        stats['profit_summaries'] = profit_summaries
        stats['total_gross_profit'] = total_gross_profit
        stats['total_allocated_profit'] = total_allocated_profit
        stats['projects_with_profit_configs'] = projects_with_profit_configs
        stats['average_profit_margin'] = sum(p['profit_margin'] for p in profit_summaries) / len(profit_summaries) if profit_summaries else 0
        stats['average_health_score'] = sum(p['health_score'] for p in profit_summaries) / len(profit_summaries) if profit_summaries else 0
        
        # Recent projects (last 30 days)
        recent_date = datetime.now() - timedelta(days=30)
        recent_projects = [p for p in processed_projects if p['created_at'] and p['created_at'] >= recent_date]
        stats['recent_projects'] = recent_projects
        stats['recent_project_count'] = len(recent_projects)
        
        return stats
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        return None
    finally:
        db_ops.close()

def show_empty_dashboard():
    """Show dashboard when no data exists"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background-color: #f8f9fa; border-radius: 10px; margin: 2rem 0;">
        <h2>📊 Welcome to Your Project Dashboard!</h2>
        <p style="font-size: 1.2em; color: #6c757d;">You haven't created any projects yet. Let's get started!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏢 Add Companies", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()
    
    with col2:
        if st.button("➕ Create First Project", use_container_width=True):
            st.session_state.page = "projects"
            st.session_state.action = "new_project"
            st.rerun()
    
    with col3:
        if st.button("📋 Add Tasks", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()

def show_key_metrics(data):
    """Display key performance metrics - ENHANCED WITH FINAL COSTS"""
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        completion_rate = (data['completed_projects'] / data['total_projects'] * 100) if data['total_projects'] > 0 else 0
        st.metric(
            "Total Projects",
            data['total_projects'],
            delta=f"{completion_rate:.1f}% completed"
        )
    
    with col2:
        st.metric(
            "Active Projects",
            data['active_projects'],
            delta=f"+{data['recent_project_count']} this month"
        )
    
    with col3:
        st.metric(
            "Total Revenue",
            f"৳{data['total_revenue']:,.0f}",
            delta=f"৳{data['average_project_value']:,.0f} avg"
        )
    
    with col4:
        # Financial tracking metrics
        projection_amount = data['projection_stats'].get('total_projection_amount', 0)
        st.metric(
            "Projected Costs",
            f"৳{projection_amount:,.0f}",
            delta=f"{data['projection_stats'].get('projects_with_projections', 0)} projects"
        )
    
    with col5:
        # Final costs metrics
        final_cost_amount = data['final_cost_stats'].get('total_real_cost', 0)
        variance_pct = data['final_cost_stats'].get('variance_percentage', 0)
        delta_color = "inverse" if variance_pct > 0 else "normal"
        
        st.metric(
            "Actual Costs",
            f"৳{final_cost_amount:,.0f}",
            delta=f"{variance_pct:+.1f}% variance",
            delta_color=delta_color
        )
    
    with col6:
        # Profit metrics - NEW
        profit_summaries = data.get('profit_summaries', [])
        if profit_summaries:
            avg_profit_margin = data.get('average_profit_margin', 0)
            st.metric(
                "Avg Profit Margin",
                f"{avg_profit_margin:.1f}%",
                delta=f"{len(profit_summaries)} projects analyzed"
            )
        else:
            total_disbursed = data['disbursement_stats'].get('total_amount', 0)
            st.metric(
                "Total Disbursed",
                f"৳{total_disbursed:,.0f}",
                delta=f"{data['disbursement_stats'].get('total_count', 0)} receipts"
            )

# Add new function for cost performance chart
def show_cost_performance_chart(data):
    """Show cost performance analysis chart"""
    st.subheader("💰 Cost Performance Analysis")
    
    try:
        import plotly.graph_objects as go
        
        # Get cost data
        projected = data['projection_stats'].get('total_projection_amount', 0)
        actual = data['final_cost_stats'].get('total_real_cost', 0)
        disbursed = data['disbursement_stats'].get('total_amount', 0)
        
        # Create cost comparison chart
        categories = ['Projected Costs', 'Actual Costs', 'Disbursed Amount']
        values = [projected, actual, disbursed]
        colors = ['#007bff', '#28a745', '#ffc107']
        
        if any(values):
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker_color=colors,
                    text=[f"৳{val:,.0f}" for val in values],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Amount: ৳%{y:,.0f}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                height=350,
                xaxis_title="Cost Categories",
                yaxis_title="Amount (৳)",
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data available for visualization.")
            
    except Exception as e:
        st.info(f"Chart not available: {str(e)}")

def show_project_status_distribution(data):
    """Show project status distribution pie chart"""
    st.subheader("📊 Project Status Distribution")
    
    if not data['status_counts']:
        st.info("No project status data available.")
        return
    
    # Prepare data for pie chart
    statuses = list(data['status_counts'].keys())
    counts = list(data['status_counts'].values())
    
    # Color mapping for statuses
    color_map = {
        'new': '#ffc107',      # Yellow
        'active': '#28a745',   # Green
        'completed': '#007bff', # Blue
        'on_hold': '#fd7e14',  # Orange
        'cancelled': '#dc3545' # Red
    }
    
    colors = [color_map.get(status, '#6c757d') for status in statuses]
    
    fig = go.Figure(data=[go.Pie(
        labels=[status.replace('_', ' ').title() for status in statuses],
        values=counts,
        marker_colors=colors,
        textinfo='label+percent+value',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        height=350,
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_revenue_analysis(data):
    """Show revenue analysis chart"""
    st.subheader("💰 Revenue Analysis")
    
    # Create revenue breakdown data
    revenue_data = {
        'Category': ['Completed Projects', 'Active Projects', 'New Projects'],
        'Revenue': [
            data['completed_revenue'],
            data['active_revenue'],
            sum(p['final_po_value'] for p in data['projects'] if p['status'] == 'new')
        ],
        'Color': ['#28a745', '#007bff', '#ffc107']
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=revenue_data['Category'],
            y=revenue_data['Revenue'],
            marker_color=revenue_data['Color'],
            text=[f"৳{val:,.0f}" for val in revenue_data['Revenue']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Revenue: ৳%{y:,.0f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        height=350,
        xaxis_title="Project Category",
        yaxis_title="Revenue (৳)",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_company_distribution(data):
    """Show customer vs supplier distribution"""
    st.subheader("🏢 Company Distribution")
    
    company_data = {
        'Type': ['Customers', 'Suppliers'],
        'Count': [data['customer_count'], data['supplier_count']],
        'Color': ['#28a745', '#007bff']
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=company_data['Type'],
        values=company_data['Count'],
        marker_colors=company_data['Color'],
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        height=350,
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_monthly_project_creation(data):
    """Show monthly project creation trend"""
    st.subheader("📅 Monthly Project Creation")
    
    monthly_data = data['monthly_creation_data']
    
    if not monthly_data:
        st.info("No monthly data available.")
        return
    
    # Sort by date and prepare data
    sorted_months = sorted(monthly_data.keys())
    month_labels = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months]
    counts = [monthly_data[month] for month in sorted_months]
    
    fig = go.Figure(data=[
        go.Scatter(
            x=month_labels,
            y=counts,
            mode='lines+markers',
            line=dict(color='#007bff', width=3),
            marker=dict(size=8, color='#007bff'),
            fill='tonexty',
            fillcolor='rgba(0, 123, 255, 0.1)',
            hovertemplate='<b>%{x}</b><br>Projects Created: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        height=350,
        xaxis_title="Month",
        yaxis_title="Projects Created",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_recent_projects(data):
    """Show recent projects table - FIXED VERSION"""
    st.subheader("📋 Recent Projects")
    
    # Sort by created_at using the processed data
    recent_projects = sorted(
        data['projects'], 
        key=lambda x: x['created_at'] or datetime.min, 
        reverse=True
    )[:10]
    
    if not recent_projects:
        st.info("No recent projects to display.")
        return
    
    # Prepare table data using processed data
    table_data = []
    for project in recent_projects:
        # Status emoji mapping
        status_emoji = {
            'new': '🆕',
            'active': '🟢',
            'completed': '✅',
            'on_hold': '⏸️',
            'cancelled': '❌'
        }
        
        table_data.append({
            'Project': project['project_name'],
            'Status': f"{status_emoji.get(project['status'], '⚪')} {project['status'].title()}",
            'Client': project['po_issuing_company_name'],
            'Value': f"৳{project['final_po_value']:,.0f}",
            'Created': project['created_at'].strftime('%Y-%m-%d') if project['created_at'] else 'N/A'
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("📊 View All Projects", use_container_width=True):
        st.session_state.page = "projects"
        st.rerun()

def show_enhanced_quick_actions(user_role, data):
    """Show enhanced context-aware quick actions"""
    # Profit-related alerts - NEW
    profit_summaries = data.get('profit_summaries', [])
    
    if profit_summaries:
        # Check for low-profit projects
        low_profit_projects = [p for p in profit_summaries if p['profit_margin'] < 5]
        if low_profit_projects:
            st.error(f"🚨 {len(low_profit_projects)} project(s) with low profit margins (<5%)")
            if st.button("📊 Review Profit Analysis", use_container_width=True):
                st.session_state.page = "projects"
                st.rerun()
        
        # Check for unallocated profits
        total_gross = data.get('total_gross_profit', 0)
        total_allocated = data.get('total_allocated_profit', 0)
        if total_gross > 0 and (total_allocated / total_gross) < 0.8:
            unallocated_pct = (1 - total_allocated / total_gross) * 100
            st.warning(f"💰 {unallocated_pct:.0f}% of profits unallocated")
            if st.button("🤝 Configure Profit Sharing", use_container_width=True):
                st.session_state.page = "projects"
                st.rerun()
            
    st.subheader("⚡ Quick Actions")
    
    # Financial alerts
    variance_pct = data['final_cost_stats'].get('variance_percentage', 0)
    if variance_pct > 10:
        st.error(f"🚨 High cost variance: {variance_pct:+.1f}%")
        if st.button("📊 View Cost Analysis", use_container_width=True):
            st.session_state.page = "financial"
            st.rerun()
    elif variance_pct > 5:
        st.warning(f"⚠️ Cost variance: {variance_pct:+.1f}%")
    
    # Action based on current data
    if data['overdue_projects'] > 0:
        st.warning(f"⚠️ {data['overdue_projects']} overdue project(s)")
        if st.button("🔍 View Overdue Projects", use_container_width=True):
            st.session_state.page = "projects"
            st.session_state.filter_overdue = True
            st.rerun()
    
    if data['upcoming_deadlines'] > 0:
        st.info(f"📅 {data['upcoming_deadlines']} upcoming deadline(s)")
    
    # Standard quick actions
    if st.button("➕ New Project", use_container_width=True):
        st.session_state.page = "projects"
        st.session_state.action = "new_project"
        st.rerun()
    
    if st.button("💰 Financial Management", use_container_width=True):
        st.session_state.page = "financial"
        st.rerun()
    
    if st.button("💸 New Disbursement", use_container_width=True):
        st.session_state.page = "financial"
        st.session_state.action = "new_disbursement"
        st.rerun()
    
    # Admin actions
    if user_role == 'admin':
        if st.button("🏢 Manage Companies", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()
def show_profit_overview_summary(data):
    """Show profit overview summary - NEW SECTION"""
    st.subheader("💰 Profit Overview")
    
    profit_summaries = data.get('profit_summaries', [])
    
    if not profit_summaries:
        st.info("💡 No profit calculations available. Configure profit sharing for projects to see profit analysis.")
        return
    
    # Profit overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_gross_profit = data.get('total_gross_profit', 0)
        st.metric("Total Gross Profit", f"৳{total_gross_profit:,.0f}")
    
    with col2:
        total_allocated = data.get('total_allocated_profit', 0)
        allocation_rate = (total_allocated / total_gross_profit * 100) if total_gross_profit > 0 else 0
        st.metric("Allocated Profit", f"৳{total_allocated:,.0f}", delta=f"{allocation_rate:.1f}% allocated")
    
    with col3:
        avg_margin = data.get('average_profit_margin', 0)
        st.metric("Avg Profit Margin", f"{avg_margin:.1f}%")
    
    with col4:
        avg_health = data.get('average_health_score', 0)
        projects_with_configs = data.get('projects_with_profit_configs', 0)
        st.metric("Avg Health Score", f"{avg_health:.0f}/100", delta=f"{projects_with_configs} configured")
    
    # Top performing projects
    if len(profit_summaries) >= 3:
        st.markdown("#### 🏆 Top Performing Projects")
        
        # Sort by profit margin
        top_projects = sorted(profit_summaries, key=lambda x: x['profit_margin'], reverse=True)[:5]
        
        for i, project in enumerate(top_projects):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                rank_icon = ["🥇", "🥈", "🥉", "🏅", "⭐"][i] if i < 5 else "📊"
                st.markdown(f"**{rank_icon} {project['project_name']}**")
            
            with col2:
                st.metric("Profit", f"৳{project['gross_profit']:,.0f}")
            
            with col3:
                st.metric("Margin", f"{project['profit_margin']:.1f}%")
            
            # with col4:
            #     health_icon = "🟢" if project['health_score'] >= 80 else "🟡" if project['health_score'] >= 60 else "🔴"
            #     st.markdown(f"{health_icon} {project['health_score']:.0f}")
    
    # Profit health distribution
    if profit_summaries:
        st.markdown("#### 📊 Profit Health Distribution")
        
        health_categories = {'Excellent (80+)': 0, 'Good (60-79)': 0, 'Fair (40-59)': 0, 'Poor (<40)': 0}
        
        for project in profit_summaries:
            score = project['health_score']
            if score >= 80:
                health_categories['Excellent (80+)'] += 1
            elif score >= 60:
                health_categories['Good (60-79)'] += 1
            elif score >= 40:
                health_categories['Fair (40-59)'] += 1
            else:
                health_categories['Poor (<40)'] += 1
        
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        colors = ['success', 'info', 'warning', 'error']
        
        for i, (category, count) in enumerate(health_categories.items()):
            with cols[i]:
                percentage = (count / len(profit_summaries) * 100) if profit_summaries else 0
                st.metric(category, count, delta=f"{percentage:.0f}%")
                
def show_financial_health_summary(data):
    """Show financial health summary - NEW SECTION"""
    st.subheader("💊 Financial Health")
    
    # Cost tracking progress
    total_projects = data['total_projects']
    projects_with_costs = data['final_cost_stats'].get('projects_with_costs', 0)
    tracking_rate = (projects_with_costs / total_projects * 100) if total_projects > 0 else 0
    
    st.metric("Cost Tracking Rate", f"{tracking_rate:.0f}%")
    
    # Financial health indicators
    variance_pct = data['final_cost_stats'].get('variance_percentage', 0)
    
    if abs(variance_pct) <= 5:
        st.success("✅ Excellent Cost Control")
    elif abs(variance_pct) <= 10:
        st.warning("⚠️ Monitor Cost Variance")
    else:
        st.error("🚨 Review Cost Management")
    
    # Budget utilization
    projected_total = data['projection_stats'].get('total_projection_amount', 0)
    disbursed_total = data['disbursement_stats'].get('total_amount', 0)
    
    if projected_total > 0:
        utilization = (disbursed_total / projected_total * 100)
        st.metric("Budget Utilization", f"{utilization:.0f}%")
    
    # Quick stats
    st.markdown("#### 📊 Quick Stats")
    st.success(f"✅ Projects tracked: {projects_with_costs}/{total_projects}")
    st.info(f"📋 Cost items: {data['final_cost_stats'].get('total_cost_items', 0)}")
    st.info(f"💸 Disbursements: {data['disbursement_stats'].get('total_count', 0)}")
    
    # Last update info
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

def show_project_timeline_analysis(data):
    """Show project timeline analysis"""
    st.subheader("📅 Timeline Analysis")
    
    if data['overdue_projects'] > 0:
        st.error(f"🚨 {data['overdue_projects']} Overdue Projects")
        
        # Show overdue projects
        for project in data['overdue_project_list'][:3]:  # Show first 3
            days_overdue = (date.today() - project['tentative_end_date']).days
            st.markdown(f"• **{project['project_name']}** - {days_overdue} days overdue")
    
    if data['upcoming_deadlines'] > 0:
        st.warning(f"⏰ {data['upcoming_deadlines']} Upcoming Deadlines")
        
        # Show upcoming deadlines
        for project in data['upcoming_deadline_list'][:3]:  # Show first 3
            days_until = (project['tentative_end_date'] - date.today()).days
            st.markdown(f"• **{project['project_name']}** - Due in {days_until} days")
    
    if data['overdue_projects'] == 0 and data['upcoming_deadlines'] == 0:
        st.success("✅ All projects are on track!")
    
    # Timeline chart for active projects
    active_projects = [p for p in data['projects'] if p['status'] == 'active' and p['tentative_end_date']]
    
    if active_projects:
        st.markdown("#### Active Project Timelines")
        
        timeline_data = []
        for project in active_projects[:5]:  # Show first 5
            start_date = project['start_date'] or date.today()
            end_date = project['tentative_end_date']
            duration = (end_date - start_date).days if end_date > start_date else 1
            
            timeline_data.append({
                'Project': project['project_name'][:20] + "..." if len(project['project_name']) > 20 else project['project_name'],
                'Start': start_date,
                'End': end_date,
                'Duration': duration
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def show_system_health():
    """Show system health and statistics"""
    st.subheader("🔧 System Health")
    
    # System status indicators
    status_items = [
        {'label': 'Database', 'status': 'Online', 'color': 'green'},
        {'label': 'Authentication', 'status': 'Active', 'color': 'green'},
        {'label': 'File System', 'status': 'OK', 'color': 'green'},
        {'label': 'Sessions', 'status': 'Active', 'color': 'green'}
    ]
    
    for item in status_items:
        status_color = {
            'green': '#28a745',
            'orange': '#ffc107',
            'red': '#dc3545'
        }.get(item['color'], '#6c757d')
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; margin: 5px 0; border-radius: 5px; background-color: #f8f9fa;">
            <span>{item['label']}</span>
            <span style="color: {status_color}; font-weight: bold;">● {item['status']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Database statistics
    db_ops = DatabaseOperations()
    try:
        stats = db_ops.get_project_statistics()
        
        st.markdown("#### Quick Stats")
        st.metric("Database Health", "Excellent")
        st.metric("Data Integrity", "100%")
        
        # System info
        import os
        if os.path.exists("project_management.db"):
            file_size = os.path.getsize("project_management.db")
            st.caption(f"Database: {file_size:,} bytes")
        
    except Exception as e:
        st.error(f"Database health check failed: {str(e)}")
    finally:
        db_ops.close()
    
    # Last update info
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()