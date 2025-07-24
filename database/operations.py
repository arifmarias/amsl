from sqlalchemy.orm import Session
from database.connection import SessionLocal, engine
from database.models import *
import bcrypt
from datetime import datetime

class DatabaseOperations:
    """Database operations class for common CRUD operations"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def close(self):
        """Close database session"""
        self.db.close()
    
    # User Operations
    def create_user(self, username: str, password: str, role: str, full_name: str, email: str):
        """Create a new user"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user = User(
                username=username,
                password_hash=password_hash.decode('utf-8'),
                role=role,
                full_name=full_name,
                email=email,
                is_active=True
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise e
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate user login"""
        try:
            user = self.db.query(User).filter(User.username == username, User.is_active == True).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return user
            return None
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
    
    def get_all_users(self):
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).all()
    
    # Enhanced Company Operations
    def create_company(self, name: str, company_type: str, address: str = None, 
                      phone: str = None, email: str = None, contact_person: str = None, 
                      designation: str = None):
        """Create a new company (backward compatibility)"""
        try:
            company = Company(
                name=name,
                company_type=company_type,
                address=address,
                phone=phone,
                email=email,
                contact_person=contact_person,
                designation=designation
            )
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_enhanced_company(self, name: str, company_type: str, address: str = None, 
                               city: str = None, postal_code: str = None, phone: str = None, 
                               email: str = None, website: str = None, contact_person: str = None, 
                               designation: str = None, tax_id: str = None, notes: str = None):
        """Create a new company with enhanced fields"""
        try:
            company = Company(
                name=name,
                company_type=company_type,
                address=address,
                phone=phone,
                email=email,
                contact_person=contact_person,
                designation=designation
            )
            
            # Add enhanced fields (these will be stored in address field as JSON for now)
            # In a full implementation, you'd add these columns to the Company model
            enhanced_data = {
                'city': city,
                'postal_code': postal_code,
                'website': website,
                'tax_id': tax_id,
                'notes': notes
            }
            
            # Store enhanced data (simplified approach)
            company.address = f"{address}\nCity: {city}\nPostal: {postal_code}" if address else f"City: {city}\nPostal: {postal_code}"
            
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_company_by_id(self, company_id: int):
        """Get company by ID"""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def update_company(self, company_id: int, name: str, company_type: str, address: str = None,
                      city: str = None, postal_code: str = None, phone: str = None, 
                      email: str = None, website: str = None, contact_person: str = None,
                      designation: str = None, tax_id: str = None, notes: str = None):
        """Update a company"""
        try:
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if company:
                company.name = name
                company.company_type = company_type
                company.address = f"{address}\nCity: {city}\nPostal: {postal_code}" if address else f"City: {city}\nPostal: {postal_code}"
                company.phone = phone
                company.email = email
                company.contact_person = contact_person
                company.designation = designation
                company.updated_at = datetime.utcnow()
                
                self.db.commit()
                return company
            return None
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_company(self, company_id: int):
        """Delete a company"""
        try:
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if company:
                self.db.delete(company)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_projects_by_company(self, company_id: int):
        """Get projects that use this company"""
        return self.db.query(Project).filter(
            (Project.po_issuing_company_id == company_id) | 
            (Project.supplier_company_id == company_id)
        ).all()
    
    def get_companies_by_type(self, company_type: str):
        """Get companies by type (customer/supplier)"""
        return self.db.query(Company).filter(Company.company_type == company_type).all()
    
    def get_all_companies(self):
        """Get all companies"""
        return self.db.query(Company).all()
    
    # Enhanced Task Description Operations
    def create_task_description(self, task_name: str, description: str = None):
        """Create a new task description (backward compatibility)"""
        try:
            task = TaskDescription(
                task_name=task_name,
                description=description,
                is_active=True
            )
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_enhanced_task_description(self, task_name: str, description: str = None, 
                                   default_percentage: float = 0.0, is_active: bool = True):
        """Create a new task description with enhanced fields"""
        try:
            # Store the description separately from percentage info
            clean_description = description if description else ""
            
            task = TaskDescription(
                task_name=task_name,
                description=clean_description,
                is_active=is_active
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            # Store percentage in a separate way (we'll add this as a custom attribute)
            # For now, we'll use a simple approach with the task object
            task.default_percentage = default_percentage
            
            return task
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_task_description_by_id(self, task_id: int):
        """Get task description by ID"""
        return self.db.query(TaskDescription).filter(TaskDescription.id == task_id).first()
    
    def update_task_description(self, task_id: int, task_name: str, description: str = None,
                           default_percentage: float = 0.0, is_active: bool = True):
        """Update a task description"""
        try:
            task = self.db.query(TaskDescription).filter(TaskDescription.id == task_id).first()
            if task:
                task.task_name = task_name
                task.description = description if description else ""
                task.is_active = is_active
                task.updated_at = datetime.utcnow()
                
                # Add default percentage as custom attribute
                task.default_percentage = default_percentage
                
                self.db.commit()
                return task
            return None
        except Exception as e:
            self.db.rollback()
            raise e
        
    def get_all_task_descriptions_with_percentage(self):
        """Get all task descriptions with default percentage extracted"""
        tasks = self.db.query(TaskDescription).all()
        
        # Add default_percentage attribute to each task
        for task in tasks:
            # Extract percentage from description if it exists
            if task.description and "Default:" in task.description:
                try:
                    # Extract percentage from description
                    lines = task.description.split('\n')
                    percentage_line = [line for line in lines if line.startswith('Default:')]
                    if percentage_line:
                        percentage_str = percentage_line[0].replace('Default:', '').replace('%', '').strip()
                        task.default_percentage = float(percentage_str)
                        # Clean the description by removing the percentage line
                        clean_lines = [line for line in lines if not line.startswith('Default:')]
                        task.clean_description = '\n'.join(clean_lines).strip()
                    else:
                        task.default_percentage = 0.0
                        task.clean_description = task.description
                except:
                    task.default_percentage = 0.0
                    task.clean_description = task.description
            else:
                task.default_percentage = 0.0
                task.clean_description = task.description or ""
        
        return tasks
    
    def delete_task_description(self, task_id: int):
        """Delete a task description"""
        try:
            task = self.db.query(TaskDescription).filter(TaskDescription.id == task_id).first()
            if task:
                self.db.delete(task)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_profit_configs_by_task(self, task_id: int):
        """Get profit sharing configs that use this task"""
        return self.db.query(ProfitSharingConfig).filter(ProfitSharingConfig.task_description_id == task_id).all()
    
    def get_active_task_descriptions(self):
        """Get all active task descriptions"""
        return self.db.query(TaskDescription).filter(TaskDescription.is_active == True).all()
    
    def get_all_task_descriptions(self):
        """Get all task descriptions"""
        return self.db.query(TaskDescription).all()
    
    # Project Operations (unchanged)
    def create_project(self, project_name: str, po_number: str = None, 
                      po_issuing_company_id: int = None, supplier_company_id: int = None,
                      start_date = None, tentative_end_date = None):
        """Create a new project"""
        try:
            project = Project(
                project_name=project_name,
                po_number=po_number,
                po_issuing_company_id=po_issuing_company_id,
                supplier_company_id=supplier_company_id,
                start_date=start_date,
                tentative_end_date=tentative_end_date,
                status="new"
            )
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            return project
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_all_projects(self):
        """Get all projects with company relationships"""
        return self.db.query(Project).all()
    
    def get_project_by_id(self, project_id: int):
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def update_project_status(self, project_id: int, status: str):
        """Update project status"""
        try:
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = status
                project.updated_at = datetime.utcnow()
                self.db.commit()
                return project
            return None
        except Exception as e:
            self.db.rollback()
            raise e
    
    # Statistics and Dashboard
    def get_project_statistics(self):
        """Get project statistics for dashboard"""
        try:
            total_projects = self.db.query(Project).count()
            active_projects = self.db.query(Project).filter(Project.status == "active").count()
            completed_projects = self.db.query(Project).filter(Project.status == "completed").count()
            total_revenue = self.db.query(func.sum(Project.final_po_value)).scalar() or 0
            
            return {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "total_revenue": total_revenue
            }
        except Exception as e:
            print(f"Statistics error: {str(e)}")
            return {
                "total_projects": 0,
                "active_projects": 0,
                "completed_projects": 0,
                "total_revenue": 0
            }
    #----
    def get_all_task_descriptions_with_percentage(self):
        """Get all task descriptions with default percentage extracted"""
        tasks = self.db.query(TaskDescription).all()
        
        # Add default_percentage attribute to each task
        for task in tasks:
            # Extract percentage from description if it exists
            if task.description and "Default:" in task.description:
                try:
                    # Extract percentage from description
                    lines = task.description.split('\n')
                    percentage_line = [line for line in lines if line.startswith('Default:')]
                    if percentage_line:
                        percentage_str = percentage_line[0].replace('Default:', '').replace('%', '').strip()
                        task.default_percentage = float(percentage_str)
                        # Clean the description by removing the percentage line
                        clean_lines = [line for line in lines if not line.startswith('Default:')]
                        task.clean_description = '\n'.join(clean_lines).strip()
                    else:
                        task.default_percentage = 0.0
                        task.clean_description = task.description
                except:
                    task.default_percentage = 0.0
                    task.clean_description = task.description
            else:
                task.default_percentage = 0.0
                task.clean_description = task.description or ""
        
        return tasks

    def get_enhanced_project_statistics(self):
        """Get enhanced project statistics for dashboard"""
        try:
            projects = self.db.query(Project).all()
            companies = self.db.query(Company).all()
            
            if not projects:
                return {
                    "total_projects": 0,
                    "active_projects": 0,
                    "completed_projects": 0,
                    "total_revenue": 0,
                    "projects_this_month": 0,
                    "average_project_value": 0,
                    "completion_rate": 0
                }
            
            # Basic counts
            total_projects = len(projects)
            active_projects = len([p for p in projects if p.status == "active"])
            completed_projects = len([p for p in projects if p.status == "completed"])
            new_projects = len([p for p in projects if p.status == "new"])
            
            # Financial calculations
            total_revenue = sum(p.final_po_value or 0 for p in projects)
            completed_revenue = sum(p.final_po_value or 0 for p in projects if p.status == "completed")
            average_project_value = total_revenue / total_projects if total_projects > 0 else 0
            
            # Time-based calculations
            from datetime import datetime, timedelta
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            projects_this_month = len([p for p in projects if p.created_at and p.created_at >= current_month_start])
            
            # Completion rate
            completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
            
            # Company statistics
            customer_count = len([c for c in companies if c.company_type == "customer"])
            supplier_count = len([c for c in companies if c.company_type == "supplier"])
            
            return {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "new_projects": new_projects,
                "total_revenue": total_revenue,
                "completed_revenue": completed_revenue,
                "average_project_value": average_project_value,
                "projects_this_month": projects_this_month,
                "completion_rate": completion_rate,
                "customer_count": customer_count,
                "supplier_count": supplier_count,
                "total_companies": len(companies)
            }
            
        except Exception as e:
            print(f"Enhanced statistics error: {str(e)}")
            return {
                "total_projects": 0,
                "active_projects": 0,
                "completed_projects": 0,
                "total_revenue": 0,
                "projects_this_month": 0,
                "average_project_value": 0,
                "completion_rate": 0,
                "customer_count": 0,
                "supplier_count": 0,
                "total_companies": 0
            }

    def get_projects_by_date_range(self, start_date, end_date):
        """Get projects created within a date range"""
        try:
            return self.db.query(Project).filter(
                Project.created_at >= start_date,
                Project.created_at <= end_date
            ).all()
        except Exception as e:
            print(f"Date range query error: {str(e)}")
            return []

    def get_overdue_projects(self):
        """Get projects that are overdue"""
        try:
            from datetime import date
            current_date = date.today()
            
            return self.db.query(Project).filter(
                Project.tentative_end_date < current_date,
                Project.status.in_(['new', 'active'])
            ).all()
        except Exception as e:
            print(f"Overdue projects error: {str(e)}")
            return []

    def get_upcoming_deadline_projects(self, days_ahead=30):
        """Get projects with upcoming deadlines"""
        try:
            from datetime import date, timedelta
            current_date = date.today()
            future_date = current_date + timedelta(days=days_ahead)
            
            return self.db.query(Project).filter(
                Project.tentative_end_date >= current_date,
                Project.tentative_end_date <= future_date,
                Project.status.in_(['new', 'active'])
            ).all()
        except Exception as e:
            print(f"Upcoming deadlines error: {str(e)}")
            return []

    def get_project_status_distribution(self):
        """Get distribution of project statuses"""
        try:
            from sqlalchemy import func
            
            status_distribution = self.db.query(
                Project.status,
                func.count(Project.id).label('count')
            ).group_by(Project.status).all()
            
            return {status: count for status, count in status_distribution}
        except Exception as e:
            print(f"Status distribution error: {str(e)}")
            return {}

    def get_monthly_project_creation_stats(self):
        """Get monthly project creation statistics"""
        try:
            from sqlalchemy import func, extract
            
            monthly_stats = self.db.query(
                extract('year', Project.created_at).label('year'),
                extract('month', Project.created_at).label('month'),
                func.count(Project.id).label('count')
            ).group_by(
                extract('year', Project.created_at),
                extract('month', Project.created_at)
            ).order_by(
                extract('year', Project.created_at),
                extract('month', Project.created_at)
            ).all()
            
            return [(int(year), int(month), count) for year, month, count in monthly_stats]
            
        except Exception as e:
            print(f"Monthly stats error: {str(e)}")
            return []

    def get_revenue_by_status(self):
        """Get revenue breakdown by project status"""
        try:
            from sqlalchemy import func
            
            revenue_by_status = self.db.query(
                Project.status,
                func.sum(Project.final_po_value).label('total_revenue')
            ).group_by(Project.status).all()
            
            return {status: float(revenue or 0) for status, revenue in revenue_by_status}
        except Exception as e:
            print(f"Revenue by status error: {str(e)}")
            return {}

    def get_top_clients_by_revenue(self, limit=5):
        """Get top clients by total project revenue"""
        try:
            from sqlalchemy import func
            
            top_clients = self.db.query(
                Company.name,
                func.sum(Project.final_po_value).label('total_revenue'),
                func.count(Project.id).label('project_count')
            ).join(
                Project, Company.id == Project.po_issuing_company_id
            ).group_by(
                Company.id, Company.name
            ).order_by(
                func.sum(Project.final_po_value).desc()
            ).limit(limit).all()
            
            return [(name, float(revenue or 0), count) for name, revenue, count in top_clients]
        except Exception as e:
            print(f"Top clients error: {str(e)}")
            return []

    def get_project_duration_analysis(self):
        """Analyze project durations"""
        try:
            projects_with_dates = self.db.query(Project).filter(
                Project.start_date.isnot(None),
                Project.tentative_end_date.isnot(None)
            ).all()
            
            durations = []
            for project in projects_with_dates:
                duration = (project.tentative_end_date - project.start_date).days
                durations.append({
                    'project_name': project.project_name,
                    'duration_days': duration,
                    'status': project.status
                })
            
            return durations
        except Exception as e:
            print(f"Duration analysis error: {str(e)}")
            return []
    #----
    def create_initial_projection(self, project_id: int, sl_no: int, particulars: str, 
                             days: float = 0.0, qty: float = 0.0, unit_price: float = 0.0, 
                             amount: float = 0.0):
        """Create a new initial financial projection item"""
        try:
            projection = InitialFinancialProjection(
                project_id=project_id,
                sl_no=sl_no,
                particulars=particulars,
                days=days,
                qty=qty,
                unit_price=unit_price,
                amount=amount
            )
            self.db.add(projection)
            self.db.commit()
            self.db.refresh(projection)
            # Auto-update project status when first projection is created
            projections_count = len(self.get_initial_projections_by_project(project_id))
            if projections_count == 1:  # First projection created
                self.update_project_status_automatically(project_id, 'projection_created')
            return projection
        except Exception as e:
            self.db.rollback()
            raise e

    def get_initial_projections_by_project(self, project_id: int):
        """Get all initial projections for a project"""
        return self.db.query(InitialFinancialProjection).filter(
            InitialFinancialProjection.project_id == project_id
        ).order_by(InitialFinancialProjection.sl_no).all()

    def get_initial_projection_by_id(self, projection_id: int):
        """Get initial projection by ID"""
        return self.db.query(InitialFinancialProjection).filter(
            InitialFinancialProjection.id == projection_id
        ).first()

    def update_initial_projection(self, projection_id: int, particulars: str = None, 
                                days: float = None, qty: float = None, 
                                unit_price: float = None, amount: float = None):
        """Update an initial projection"""
        try:
            projection = self.db.query(InitialFinancialProjection).filter(
                InitialFinancialProjection.id == projection_id
            ).first()
            
            if projection:
                if particulars is not None:
                    projection.particulars = particulars
                if days is not None:
                    projection.days = days
                if qty is not None:
                    projection.qty = qty
                if unit_price is not None:
                    projection.unit_price = unit_price
                if amount is not None:
                    projection.amount = amount
                
                projection.updated_at = datetime.now()
                self.db.commit()
                return projection
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_initial_projection(self, projection_id: int):
        """Delete an initial projection"""
        try:
            projection = self.db.query(InitialFinancialProjection).filter(
                InitialFinancialProjection.id == projection_id
            ).first()
            
            if projection:
                self.db.delete(projection)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_initial_projections_by_project(self, project_id: int):
        """Delete all initial projections for a project"""
        try:
            projections = self.db.query(InitialFinancialProjection).filter(
                InitialFinancialProjection.project_id == project_id
            ).all()
            
            for projection in projections:
                self.db.delete(projection)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def get_total_projection_amount_by_project(self, project_id: int):
        """Get total projection amount for a project"""
        try:
            from sqlalchemy import func
            total = self.db.query(func.sum(InitialFinancialProjection.amount)).filter(
                InitialFinancialProjection.project_id == project_id
            ).scalar()
            return total or 0.0
        except Exception as e:
            print(f"Error getting total projection: {str(e)}")
            return 0.0

    def get_projects_with_projections(self):
        """Get all projects that have initial projections"""
        try:
            from sqlalchemy import func
            
            projects_with_projections = self.db.query(
                Project,
                func.count(InitialFinancialProjection.id).label('projection_count'),
                func.sum(InitialFinancialProjection.amount).label('total_projection')
            ).outerjoin(
                InitialFinancialProjection, Project.id == InitialFinancialProjection.project_id
            ).group_by(Project.id).all()
            
            return projects_with_projections
        except Exception as e:
            print(f"Error getting projects with projections: {str(e)}")
            return []

    def get_financial_summary_by_project(self, project_id: int):
        """Get comprehensive financial summary for a project"""
        try:
            from sqlalchemy import func
            
            # Get project details
            project = self.db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                return None
            
            # Get projection summary
            projection_summary = self.db.query(
                func.count(InitialFinancialProjection.id).label('item_count'),
                func.sum(InitialFinancialProjection.amount).label('total_amount')
            ).filter(InitialFinancialProjection.project_id == project_id).first()
            
            # Get disbursement summary (placeholder for future implementation)
            # disbursement_summary = self.db.query(func.sum(Disbursement.amount)).filter(
            #     Disbursement.project_id == project_id
            # ).scalar() or 0.0
            
            return {
                'project': project,
                'projection_items': projection_summary.item_count or 0,
                'projection_total': projection_summary.total_amount or 0.0,
                'po_value': project.total_po_value or 0.0,
                'final_po_value': project.final_po_value or 0.0,
                # 'total_disbursements': disbursement_summary
            }
        except Exception as e:
            print(f"Error getting financial summary: {str(e)}")
            return None

    def get_all_financial_projections_summary(self):
        """Get summary of all financial projections"""
        try:
            from sqlalchemy import func
            
            summary = self.db.query(
                func.count(InitialFinancialProjection.id).label('total_items'),
                func.sum(InitialFinancialProjection.amount).label('total_amount'),
                func.count(func.distinct(InitialFinancialProjection.project_id)).label('projects_with_projections')
            ).first()
            
            total_projects = self.db.query(Project).count()
            
            return {
                'total_projection_items': summary.total_items or 0,
                'total_projection_amount': summary.total_amount or 0.0,
                'projects_with_projections': summary.projects_with_projections or 0,
                'total_projects': total_projects,
                'projects_without_projections': total_projects - (summary.projects_with_projections or 0)
            }
        except Exception as e:
            print(f"Error getting projections summary: {str(e)}")
            return {
                'total_projection_items': 0,
                'total_projection_amount': 0.0,
                'projects_with_projections': 0,
                'total_projects': 0,
                'projects_without_projections': 0
            }

    def copy_projections_to_final_costs(self, project_id: int):
        """Copy initial projections to final costs table (for future implementation)"""
        try:
            projections = self.get_initial_projections_by_project(project_id)
            
            # Delete existing final costs for this project
            existing_costs = self.db.query(FinalFinancialCost).filter(
                FinalFinancialCost.project_id == project_id
            ).all()
            
            for cost in existing_costs:
                self.db.delete(cost)
            
            # Copy projections to final costs
            for proj in projections:
                final_cost = FinalFinancialCost(
                    project_id=project_id,
                    sl_no=proj.sl_no,
                    particulars=proj.particulars,
                    days=proj.days,
                    qty=proj.qty,
                    unit_price=proj.unit_price,
                    amount=proj.amount,
                    real_cost=0.0  # To be filled by finance users
                )
                self.db.add(final_cost)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error copying projections to final costs: {str(e)}")
            return False
    #----
    def create_disbursement(self, project_id: int = None, disbursement_type: str = None, 
                       amount: float = 0.0, disbursement_date = None, description: str = None,
                       created_by: int = None):
        """Create a new disbursement"""
        try:
            disbursement = Disbursement(
                project_id=project_id,
                disbursement_type=disbursement_type,
                amount=amount,
                disbursement_date=disbursement_date,
                description=description,
                created_by=created_by
            )
            self.db.add(disbursement)
            self.db.commit()
            self.db.refresh(disbursement)
            # Auto-update project status when disbursements are made
            self.update_project_status_automatically(project_id, 'disbursement_created')
            return disbursement
        except Exception as e:
            self.db.rollback()
            raise e

    def create_money_receipt(self, project_id: int = None, disbursement_id: int = None,
                            receipt_number: str = None, amount: float = 0.0,
                            received_from: str = None, received_by: str = None,
                            receipt_date = None):
        """Create a new money receipt"""
        try:
            receipt = MoneyReceipt(
                project_id=project_id,
                disbursement_id=disbursement_id,
                receipt_number=receipt_number,
                amount=amount,
                received_from=received_from,
                received_by=received_by,
                receipt_date=receipt_date
            )
            self.db.add(receipt)
            self.db.commit()
            self.db.refresh(receipt)
            return receipt
        except Exception as e:
            self.db.rollback()
            raise e

    def get_disbursement_by_id(self, disbursement_id: int):
        """Get disbursement by ID with project relationship"""
        return self.db.query(Disbursement).filter(Disbursement.id == disbursement_id).first()

    def get_money_receipt_by_disbursement(self, disbursement_id: int):
        """Get money receipt by disbursement ID"""
        return self.db.query(MoneyReceipt).filter(MoneyReceipt.disbursement_id == disbursement_id).first()

    def get_disbursements_with_receipts(self, filter_type="All"):
        """Get disbursements with their associated money receipts"""
        try:
            query = self.db.query(Disbursement, MoneyReceipt).outerjoin(
                MoneyReceipt, Disbursement.id == MoneyReceipt.disbursement_id
            )
            
            if filter_type != "All":
                query = query.filter(Disbursement.disbursement_type == filter_type)
            
            results = query.order_by(Disbursement.disbursement_date.desc()).all()
            return results
        except Exception as e:
            print(f"Error getting disbursements with receipts: {str(e)}")
            return []

    def get_projects_for_disbursement(self):
        """Get projects that can have disbursements (not cancelled)"""
        return self.db.query(Project).filter(Project.status != 'cancelled').all()

    def get_disbursement_statistics(self):
        """Get comprehensive disbursement statistics"""
        try:
            from sqlalchemy import func
            
            # Total statistics
            total_stats = self.db.query(
                func.count(Disbursement.id).label('total_count'),
                func.sum(Disbursement.amount).label('total_amount')
            ).first()
            
            # Statistics by type
            type_stats = self.db.query(
                Disbursement.disbursement_type,
                func.count(Disbursement.id).label('count'),
                func.sum(Disbursement.amount).label('amount')
            ).group_by(Disbursement.disbursement_type).all()
            
            # Build result dictionary
            result = {
                'total_count': total_stats.total_count or 0,
                'total_amount': total_stats.total_amount or 0.0,
                'advance_count': 0,
                'advance_amount': 0.0,
                'project_cost_count': 0,
                'project_cost_amount': 0.0,
                'personal_loan_count': 0,
                'personal_loan_amount': 0.0
            }
            
            # Fill in type-specific data
            for disbursement_type, count, amount in type_stats:
                if disbursement_type == 'advance':
                    result['advance_count'] = count
                    result['advance_amount'] = amount or 0.0
                elif disbursement_type == 'project_cost':
                    result['project_cost_count'] = count
                    result['project_cost_amount'] = amount or 0.0
                elif disbursement_type == 'personal_loan':
                    result['personal_loan_count'] = count
                    result['personal_loan_amount'] = amount or 0.0
            
            return result
            
        except Exception as e:
            print(f"Error getting disbursement statistics: {str(e)}")
            return {
                'total_count': 0, 'total_amount': 0.0,
                'advance_count': 0, 'advance_amount': 0.0,
                'project_cost_count': 0, 'project_cost_amount': 0.0,
                'personal_loan_count': 0, 'personal_loan_amount': 0.0
            }

    def get_disbursements_by_project(self, project_id: int):
        """Get all disbursements for a specific project"""
        return self.db.query(Disbursement).filter(Disbursement.project_id == project_id).all()

    def get_total_disbursements_by_project(self, project_id: int):
        """Get total disbursement amount for a project"""
        try:
            from sqlalchemy import func
            total = self.db.query(func.sum(Disbursement.amount)).filter(
                Disbursement.project_id == project_id
            ).scalar()
            return total or 0.0
        except Exception as e:
            print(f"Error getting total disbursements: {str(e)}")
            return 0.0

    def get_disbursements_by_type_and_project(self, project_id: int, disbursement_type: str):
        """Get disbursements by type for a specific project"""
        return self.db.query(Disbursement).filter(
            Disbursement.project_id == project_id,
            Disbursement.disbursement_type == disbursement_type
        ).all()

    def get_money_receipts_by_project(self, project_id: int):
        """Get all money receipts for a project"""
        return self.db.query(MoneyReceipt).filter(MoneyReceipt.project_id == project_id).all()

    def update_disbursement(self, disbursement_id: int, amount: float = None, 
                        description: str = None, disbursement_date = None):
        """Update a disbursement"""
        try:
            disbursement = self.db.query(Disbursement).filter(Disbursement.id == disbursement_id).first()
            
            if disbursement:
                if amount is not None:
                    disbursement.amount = amount
                    # Update associated money receipt amount
                    receipt = self.db.query(MoneyReceipt).filter(MoneyReceipt.disbursement_id == disbursement_id).first()
                    if receipt:
                        receipt.amount = amount
                
                if description is not None:
                    disbursement.description = description
                
                if disbursement_date is not None:
                    disbursement.disbursement_date = disbursement_date
                    # Update associated money receipt date
                    receipt = self.db.query(MoneyReceipt).filter(MoneyReceipt.disbursement_id == disbursement_id).first()
                    if receipt:
                        receipt.receipt_date = disbursement_date.date()
                
                self.db.commit()
                return disbursement
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_disbursement(self, disbursement_id: int):
        """Delete a disbursement and its associated money receipt"""
        try:
            # Delete money receipt first (foreign key constraint)
            receipt = self.db.query(MoneyReceipt).filter(MoneyReceipt.disbursement_id == disbursement_id).first()
            if receipt:
                self.db.delete(receipt)
            
            # Delete disbursement
            disbursement = self.db.query(Disbursement).filter(Disbursement.id == disbursement_id).first()
            if disbursement:
                self.db.delete(disbursement)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def get_financial_summary_with_disbursements(self, project_id: int):
        """Get comprehensive financial summary including disbursements"""
        try:
            from sqlalchemy import func
            
            # Get project details
            project = self.db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                return None
            
            # Get projection summary
            projection_summary = self.db.query(
                func.count(InitialFinancialProjection.id).label('item_count'),
                func.sum(InitialFinancialProjection.amount).label('total_amount')
            ).filter(InitialFinancialProjection.project_id == project_id).first()
            
            # Get disbursement summary
            disbursement_summary = self.db.query(
                func.count(Disbursement.id).label('total_disbursements'),
                func.sum(Disbursement.amount).label('total_disbursed')
            ).filter(Disbursement.project_id == project_id).first()
            
            # Get disbursement by type
            disbursements_by_type = self.db.query(
                Disbursement.disbursement_type,
                func.sum(Disbursement.amount).label('amount')
            ).filter(Disbursement.project_id == project_id).group_by(Disbursement.disbursement_type).all()
            
            # Build disbursement breakdown
            disbursement_breakdown = {
                'advance': 0.0,
                'project_cost': 0.0,
                'personal_loan': 0.0
            }
            
            for disb_type, amount in disbursements_by_type:
                disbursement_breakdown[disb_type] = amount or 0.0
            
            return {
                'project': project,
                'projection_items': projection_summary.item_count or 0,
                'projection_total': projection_summary.total_amount or 0.0,
                'total_disbursements': disbursement_summary.total_disbursements or 0,
                'total_disbursed': disbursement_summary.total_disbursed or 0.0,
                'disbursement_breakdown': disbursement_breakdown,
                'po_value': project.total_po_value or 0.0,
                'final_po_value': project.final_po_value or 0.0,
                'remaining_budget': (project.final_po_value or 0.0) - (disbursement_summary.total_disbursed or 0.0)
            }
        except Exception as e:
            print(f"Error getting financial summary with disbursements: {str(e)}")
            return None

    def get_all_money_receipts(self):
        """Get all money receipts"""
        return self.db.query(MoneyReceipt).order_by(MoneyReceipt.receipt_date.desc()).all()

    def get_money_receipt_by_number(self, receipt_number: str):
        """Get money receipt by receipt number"""
        return self.db.query(MoneyReceipt).filter(MoneyReceipt.receipt_number == receipt_number).first()

    def get_disbursement_trends(self, days: int = 30):
        """Get disbursement trends for the last X days"""
        try:
            from datetime import datetime, timedelta
            from sqlalchemy import func
            
            start_date = datetime.now() - timedelta(days=days)
            
            trends = self.db.query(
                func.date(Disbursement.disbursement_date).label('date'),
                func.count(Disbursement.id).label('count'),
                func.sum(Disbursement.amount).label('total_amount')
            ).filter(
                Disbursement.disbursement_date >= start_date
            ).group_by(
                func.date(Disbursement.disbursement_date)
            ).order_by('date').all()
            
            return [(date, count, amount) for date, count, amount in trends]
        except Exception as e:
            print(f"Error getting disbursement trends: {str(e)}")
            return []
    # ----
    # Add these methods to your database/operations.py file:

    def get_disbursements_with_receipts_filtered(self, type_filter="All", project_filter=None, 
                                            date_filter="All Time", amount_filter="All Amounts"):
        """Get filtered disbursements with their associated money receipts"""
        try:
            from datetime import datetime, timedelta
            
            query = self.db.query(Disbursement, MoneyReceipt).outerjoin(
                MoneyReceipt, Disbursement.id == MoneyReceipt.disbursement_id
            )
            
            # Type filter
            if type_filter != "All":
                query = query.filter(Disbursement.disbursement_type == type_filter)
            
            # Project filter
            if project_filter:
                query = query.filter(Disbursement.project_id == project_filter)
            
            # Date filter
            if date_filter != "All Time":
                days_map = {
                    "Last 7 Days": 7,
                    "Last 30 Days": 30,
                    "Last 90 Days": 90
                }
                if date_filter in days_map:
                    cutoff_date = datetime.now() - timedelta(days=days_map[date_filter])
                    query = query.filter(Disbursement.disbursement_date >= cutoff_date)
            
            # Amount filter
            if amount_filter != "All Amounts":
                if amount_filter == "< ৳10,000":
                    query = query.filter(Disbursement.amount < 10000)
                elif amount_filter == "৳10,000 - ৳50,000":
                    query = query.filter(Disbursement.amount >= 10000, Disbursement.amount <= 50000)
                elif amount_filter == "> ৳50,000":
                    query = query.filter(Disbursement.amount > 50000)
            
            results = query.order_by(Disbursement.disbursement_date.desc()).all()
            return results
        except Exception as e:
            print(f"Error getting filtered disbursements: {str(e)}")
            return []

    def get_project_advance_summary(self, project_id: int):
        """Get advance summary for a project"""
        try:
            from sqlalchemy import func
            
            # Get total advance disbursements for this project
            total_disbursed = self.db.query(func.sum(Disbursement.amount)).filter(
                Disbursement.project_id == project_id,
                Disbursement.disbursement_type == 'advance'
            ).scalar() or 0.0
            
            # Get count of advance disbursements
            disbursement_count = self.db.query(func.count(Disbursement.id)).filter(
                Disbursement.project_id == project_id,
                Disbursement.disbursement_type == 'advance'
            ).scalar() or 0
            
            return {
                'total_disbursed': total_disbursed,
                'disbursement_count': disbursement_count
            }
        except Exception as e:
            print(f"Error getting advance summary: {str(e)}")
            return {'total_disbursed': 0.0, 'disbursement_count': 0}

    def update_project_advance_amount(self, project_id: int, advance_amount: float, advance_percentage: float = None):
        """Update project advance amount"""
        try:
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.project_advance_amount = advance_amount
                if advance_percentage:
                    project.project_advance_percentage = advance_percentage
                project.updated_at = datetime.now()
                self.db.commit()
                return project
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def get_projects_advance_overview(self):
        """Get advance overview for all projects"""
        try:
            from sqlalchemy import func
            
            # Get projects with their advance information
            projects_query = self.db.query(
                Project.id,
                Project.project_name,
                Project.project_advance_amount,
                Project.project_advance_percentage,
                func.coalesce(func.sum(Disbursement.amount), 0).label('total_disbursed')
            ).outerjoin(
                Disbursement, 
                (Project.id == Disbursement.project_id) & (Disbursement.disbursement_type == 'advance')
            ).group_by(
                Project.id, Project.project_name, Project.project_advance_amount, Project.project_advance_percentage
            ).all()
            
            return projects_query
        except Exception as e:
            print(f"Error getting projects advance overview: {str(e)}")
            return []
    
    #-------
    def create_final_financial_cost(self, project_id: int, sl_no: int, particulars: str, 
                                days: float = 0.0, qty: float = 0.0, unit_price: float = 0.0, 
                                amount: float = 0.0, real_cost: float = 0.0):
        """Create a new final financial cost item"""
        try:
            final_cost = FinalFinancialCost(
                project_id=project_id,
                sl_no=sl_no,
                particulars=particulars,
                days=days,
                qty=qty,
                unit_price=unit_price,
                amount=amount,  # From initial projection
                real_cost=real_cost  # Actual cost
            )
            self.db.add(final_cost)
            self.db.commit()
            self.db.refresh(final_cost)
            # Auto-update project status when final costs are added
            self.update_project_status_automatically(project_id, 'final_costs_added')
            return final_cost
        except Exception as e:
            self.db.rollback()
            raise e

    def get_final_costs_by_project(self, project_id: int):
        """Get all final costs for a project"""
        return self.db.query(FinalFinancialCost).filter(
            FinalFinancialCost.project_id == project_id
        ).order_by(FinalFinancialCost.sl_no).all()

    def get_final_cost_by_id(self, cost_id: int):
        """Get final cost by ID"""
        return self.db.query(FinalFinancialCost).filter(
            FinalFinancialCost.id == cost_id
        ).first()

    def update_final_cost(self, cost_id: int, particulars: str = None, 
                        days: float = None, qty: float = None, 
                        unit_price: float = None, amount: float = None,
                        real_cost: float = None):
        """Update a final cost"""
        try:
            final_cost = self.db.query(FinalFinancialCost).filter(
                FinalFinancialCost.id == cost_id
            ).first()
            
            if final_cost:
                if particulars is not None:
                    final_cost.particulars = particulars
                if days is not None:
                    final_cost.days = days
                if qty is not None:
                    final_cost.qty = qty
                if unit_price is not None:
                    final_cost.unit_price = unit_price
                if amount is not None:
                    final_cost.amount = amount
                if real_cost is not None:
                    final_cost.real_cost = real_cost
                
                final_cost.updated_at = datetime.now()
                self.db.commit()
                return final_cost
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_final_cost(self, cost_id: int):
        """Delete a final cost"""
        try:
            final_cost = self.db.query(FinalFinancialCost).filter(
                FinalFinancialCost.id == cost_id
            ).first()
            
            if final_cost:
                self.db.delete(final_cost)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_final_costs_by_project(self, project_id: int):
        """Delete all final costs for a project"""
        try:
            final_costs = self.db.query(FinalFinancialCost).filter(
                FinalFinancialCost.project_id == project_id
            ).all()
            
            for cost in final_costs:
                self.db.delete(cost)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def copy_initial_to_final_costs(self, project_id: int):
        """Copy initial projections to final costs for editing"""
        try:
            # Get initial projections
            initial_projections = self.get_initial_projections_by_project(project_id)
            
            if not initial_projections:
                return False, "No initial projections found for this project"
            
            # Delete existing final costs
            self.delete_final_costs_by_project(project_id)
            
            # Copy projections to final costs
            for proj in initial_projections:
                final_cost = FinalFinancialCost(
                    project_id=project_id,
                    sl_no=proj.sl_no,
                    particulars=proj.particulars,
                    days=proj.days,
                    qty=proj.qty,
                    unit_price=proj.unit_price,
                    amount=proj.amount,  # From projection
                    real_cost=0.0  # To be filled by user
                )
                self.db.add(final_cost)
            
            self.db.commit()
            return True, f"Copied {len(initial_projections)} items to final costs"
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_cost_variance_analysis(self, project_id: int):
        """Get comprehensive cost variance analysis"""
        try:
            # Get project details
            project = self.get_project_by_id(project_id)
            if not project:
                return None
            
            # Get initial projections and final costs
            initial_projections = self.get_initial_projections_by_project(project_id)
            final_costs = self.get_final_costs_by_project(project_id)
            
            # Calculate totals
            initial_total = sum(p.amount for p in initial_projections)
            final_total = sum(f.real_cost for f in final_costs)
            
            # Calculate variance
            variance_amount = final_total - initial_total
            variance_percentage = (variance_amount / initial_total * 100) if initial_total > 0 else 0
            
            # Get disbursements
            disbursements = self.get_disbursements_by_project(project_id)
            total_disbursed = sum(d.amount for d in disbursements)
            
            return {
                'project': project,
                'initial_projection_total': initial_total,
                'final_cost_total': final_total,
                'variance_amount': variance_amount,
                'variance_percentage': variance_percentage,
                'total_disbursed': total_disbursed,
                'budget_remaining': (project.final_po_value or 0) - total_disbursed,
                'initial_projections': initial_projections,
                'final_costs': final_costs,
                'disbursements': disbursements
            }
            
        except Exception as e:
            print(f"Error getting variance analysis: {str(e)}")
            return None

    def get_projects_with_final_costs(self):
        """Get all projects that have final costs"""
        try:
            from sqlalchemy import func
            
            projects_with_costs = self.db.query(
                Project,
                func.count(FinalFinancialCost.id).label('cost_count'),
                func.sum(FinalFinancialCost.real_cost).label('total_real_cost'),
                func.sum(FinalFinancialCost.amount).label('total_projected_cost')
            ).outerjoin(
                FinalFinancialCost, Project.id == FinalFinancialCost.project_id
            ).group_by(Project.id).all()
            
            return projects_with_costs
            
        except Exception as e:
            print(f"Error getting projects with final costs: {str(e)}")
            return []

    def get_final_cost_summary(self):
        """Get summary of all final costs"""
        try:
            from sqlalchemy import func
            
            summary = self.db.query(
                func.count(FinalFinancialCost.id).label('total_items'),
                func.sum(FinalFinancialCost.amount).label('total_projected'),
                func.sum(FinalFinancialCost.real_cost).label('total_real_cost'),
                func.count(func.distinct(FinalFinancialCost.project_id)).label('projects_with_costs')
            ).first()
            
            total_projects = self.db.query(Project).count()
            
            projected_total = summary.total_projected or 0.0
            real_total = summary.total_real_cost or 0.0
            variance = real_total - projected_total
            variance_percentage = (variance / projected_total * 100) if projected_total > 0 else 0
            
            return {
                'total_cost_items': summary.total_items or 0,
                'total_projected_cost': projected_total,
                'total_real_cost': real_total,
                'variance_amount': variance,
                'variance_percentage': variance_percentage,
                'projects_with_costs': summary.projects_with_costs or 0,
                'total_projects': total_projects,
                'projects_without_costs': total_projects - (summary.projects_with_costs or 0)
            }
            
        except Exception as e:
            print(f"Error getting final cost summary: {str(e)}")
            return {
                'total_cost_items': 0,
                'total_projected_cost': 0.0,
                'total_real_cost': 0.0,
                'variance_amount': 0.0,
                'variance_percentage': 0.0,
                'projects_with_costs': 0,
                'total_projects': 0,
                'projects_without_costs': 0
            }
    # ------

    def create_profit_sharing_config(self, project_id: int, task_description_id: int, 
                                    profit_percentage: float, assigned_person_company: str):
        """Create a new profit sharing configuration"""
        try:
            config = ProfitSharingConfig(
                project_id=project_id,
                task_description_id=task_description_id,
                profit_percentage=profit_percentage,
                assigned_person_company=assigned_person_company
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            return config
        except Exception as e:
            self.db.rollback()
            raise e

    def get_profit_sharing_configs_by_project(self, project_id: int):
        """Get all profit sharing configurations for a project"""
        return self.db.query(ProfitSharingConfig).filter(
            ProfitSharingConfig.project_id == project_id
        ).all()

    def get_profit_sharing_config_by_id(self, config_id: int):
        """Get profit sharing configuration by ID"""
        return self.db.query(ProfitSharingConfig).filter(
            ProfitSharingConfig.id == config_id
        ).first()

    def update_profit_sharing_config(self, config_id: int, task_description_id: int = None,
                                    profit_percentage: float = None, 
                                    assigned_person_company: str = None):
        """Update a profit sharing configuration"""
        try:
            config = self.db.query(ProfitSharingConfig).filter(
                ProfitSharingConfig.id == config_id
            ).first()
            
            if config:
                if task_description_id is not None:
                    config.task_description_id = task_description_id
                if profit_percentage is not None:
                    config.profit_percentage = profit_percentage
                if assigned_person_company is not None:
                    config.assigned_person_company = assigned_person_company
                
                config.updated_at = datetime.now()
                self.db.commit()
                return config
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_profit_sharing_config(self, config_id: int):
        """Delete a profit sharing configuration"""
        try:
            config = self.db.query(ProfitSharingConfig).filter(
                ProfitSharingConfig.id == config_id
            ).first()
            
            if config:
                self.db.delete(config)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_profit_sharing_configs_by_project(self, project_id: int):
        """Delete all profit sharing configurations for a project"""
        try:
            configs = self.db.query(ProfitSharingConfig).filter(
                ProfitSharingConfig.project_id == project_id
            ).all()
            
            for config in configs:
                self.db.delete(config)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def copy_default_profit_sharing(self, project_id: int):
        """Copy default profit sharing percentages from task descriptions to project"""
        try:
            # Get all active task descriptions with default percentages
            tasks = self.get_all_task_descriptions_with_percentage()
            
            if not tasks:
                return False, "No task descriptions found"
            
            # Delete existing profit sharing configs for this project
            self.delete_profit_sharing_configs_by_project(project_id)
            
            # Create profit sharing configs based on task defaults
            created_count = 0
            for task in tasks:
                if task.is_active:
                    default_percentage = getattr(task, 'default_percentage', 0.0)
                    
                    if default_percentage > 0:
                        # Create config with default company name (can be edited later)
                        config = ProfitSharingConfig(
                            project_id=project_id,
                            task_description_id=task.id,
                            profit_percentage=default_percentage,
                            assigned_person_company="To be assigned"  # Default placeholder
                        )
                        self.db.add(config)
                        created_count += 1
            
            self.db.commit()
            return True, f"Created {created_count} profit sharing configurations from task defaults"
            
        except Exception as e:
            self.db.rollback()
            raise e

    def calculate_project_profit(self, project_id: int):
        """Calculate comprehensive project profit analysis - ENHANCED VERSION"""
        try:
            # Get project details
            project = self.get_project_by_id(project_id)
            if not project:
                return None
            
            # Get financial data
            initial_projections = self.get_initial_projections_by_project(project_id)
            final_costs = self.get_final_costs_by_project(project_id)
            disbursements = self.get_disbursements_by_project(project_id)
            profit_configs = self.get_profit_sharing_configs_by_project(project_id)
            
            # Calculate revenue (project value after VAT and AIT)
            total_revenue = project.final_po_value or 0.0
            
            # Calculate costs
            total_projected_cost = sum(p.amount for p in initial_projections)
            total_actual_cost = sum(f.real_cost for f in final_costs) if final_costs else 0.0
            
            # Use actual costs if available, otherwise use projected costs
            cost_basis = total_actual_cost if total_actual_cost > 0 else total_projected_cost
            
            # Calculate gross profit
            gross_profit = total_revenue - cost_basis
            profit_margin_percentage = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Calculate disbursements by type
            advance_disbursements = sum(d.amount for d in disbursements if d.disbursement_type == 'advance')
            project_cost_disbursements = sum(d.amount for d in disbursements if d.disbursement_type == 'project_cost')
            personal_loan_disbursements = sum(d.amount for d in disbursements if d.disbursement_type == 'personal_loan')
            
            # Total operational disbursements (excluding personal loans)
            operational_disbursements = advance_disbursements + project_cost_disbursements
            
            # Calculate profit distribution
            profit_distribution = []
            total_percentage_allocated = 0
            
            for config in profit_configs:
                profit_amount = (gross_profit * config.profit_percentage) / 100
                profit_distribution.append({
                    'task_id': config.task_description_id,
                    'task_name': config.task_description.task_name,
                    'assigned_to': config.assigned_person_company,
                    'percentage': config.profit_percentage,
                    'amount': profit_amount,
                    'config_id': config.id
                })
                total_percentage_allocated += config.profit_percentage
            
            # Calculate unallocated profit
            unallocated_percentage = 100 - total_percentage_allocated
            unallocated_amount = (gross_profit * unallocated_percentage) / 100
            
            # Calculate cash flow
            total_collected = operational_disbursements  # Money actually disbursed from project
            cash_flow_balance = total_revenue - total_collected
            
            # Cost efficiency metrics
            cost_efficiency = (cost_basis / total_revenue * 100) if total_revenue > 0 else 0
            
            # Project financial health score (0-100)
            health_score = 0
            if profit_margin_percentage > 20:
                health_score += 40
            elif profit_margin_percentage > 10:
                health_score += 30
            elif profit_margin_percentage > 0:
                health_score += 20
            
            if cost_efficiency < 70:
                health_score += 30
            elif cost_efficiency < 80:
                health_score += 20
            elif cost_efficiency < 90:
                health_score += 10
            
            if total_percentage_allocated >= 90:
                health_score += 30
            elif total_percentage_allocated >= 70:
                health_score += 20
            elif total_percentage_allocated >= 50:
                health_score += 10
            
            return {
                'project': project,
                'financial_summary': {
                    'total_revenue': total_revenue,
                    'total_projected_cost': total_projected_cost,
                    'total_actual_cost': total_actual_cost,
                    'cost_basis': cost_basis,
                    'gross_profit': gross_profit,
                    'profit_margin_percentage': profit_margin_percentage,
                    'cost_efficiency_percentage': cost_efficiency
                },
                'disbursement_summary': {
                    'advance_disbursements': advance_disbursements,
                    'project_cost_disbursements': project_cost_disbursements,
                    'personal_loan_disbursements': personal_loan_disbursements,
                    'operational_disbursements': operational_disbursements,
                    'total_disbursements': sum(d.amount for d in disbursements)
                },
                'cash_flow': {
                    'total_collected': total_collected,
                    'cash_flow_balance': cash_flow_balance,
                    'collection_rate': (total_collected / total_revenue * 100) if total_revenue > 0 else 0
                },
                'profit_distribution': profit_distribution,
                'allocation_summary': {
                    'total_percentage_allocated': total_percentage_allocated,
                    'unallocated_percentage': unallocated_percentage,
                    'unallocated_amount': unallocated_amount,
                    'total_distributed': sum(d['amount'] for d in profit_distribution)
                },
                'metrics': {
                    'financial_health_score': health_score,
                    'cost_variance': total_actual_cost - total_projected_cost if total_actual_cost > 0 else 0,
                    'cost_variance_percentage': ((total_actual_cost - total_projected_cost) / total_projected_cost * 100) if total_projected_cost > 0 and total_actual_cost > 0 else 0
                },
                'profit_configs': profit_configs,
                'raw_data': {
                    'initial_projections': initial_projections,
                    'final_costs': final_costs,
                    'disbursements': disbursements
                }
            }
            
        except Exception as e:
            print(f"Error calculating project profit: {str(e)}")
            return None

    def get_profit_sharing_summary(self):
        """Get summary of profit sharing across all projects"""
        try:
            from sqlalchemy import func
            
            # Get projects with profit sharing configurations
            projects_with_configs = self.db.query(
                Project.id,
                Project.project_name,
                Project.final_po_value,
                func.count(ProfitSharingConfig.id).label('config_count'),
                func.sum(ProfitSharingConfig.profit_percentage).label('total_percentage')
            ).outerjoin(
                ProfitSharingConfig, Project.id == ProfitSharingConfig.project_id
            ).group_by(
                Project.id, Project.project_name, Project.final_po_value
            ).all()
            
            # Calculate summary statistics
            total_projects = self.db.query(Project).count()
            projects_with_profit_sharing = len([p for p in projects_with_configs if p.config_count > 0])
            
            return {
                'total_projects': total_projects,
                'projects_with_profit_sharing': projects_with_profit_sharing,
                'projects_without_profit_sharing': total_projects - projects_with_profit_sharing,
                'projects_with_configs': projects_with_configs
            }
            
        except Exception as e:
            print(f"Error getting profit sharing summary: {str(e)}")
            return {
                'total_projects': 0,
                'projects_with_profit_sharing': 0,
                'projects_without_profit_sharing': 0,
                'projects_with_configs': []
            }

    def get_task_profit_analytics(self):
        """Get analytics on profit distribution by task types"""
        try:
            from sqlalchemy import func
            
            # Get profit distribution by task
            task_analytics = self.db.query(
                TaskDescription.task_name,
                func.count(ProfitSharingConfig.id).label('usage_count'),
                func.avg(ProfitSharingConfig.profit_percentage).label('avg_percentage'),
                func.sum(ProfitSharingConfig.profit_percentage).label('total_percentage')
            ).join(
                ProfitSharingConfig, TaskDescription.id == ProfitSharingConfig.task_description_id
            ).group_by(
                TaskDescription.id, TaskDescription.task_name
            ).all()
            
            return [{
                'task_name': task.task_name,
                'usage_count': task.usage_count,
                'avg_percentage': round(task.avg_percentage or 0, 1),
                'total_percentage': round(task.total_percentage or 0, 1)
            } for task in task_analytics]
            
        except Exception as e:
            print(f"Error getting task profit analytics: {str(e)}")
            return []

    def validate_profit_sharing_percentages(self, project_id: int):
        """Validate that profit sharing percentages don't exceed 100%"""
        try:
            configs = self.get_profit_sharing_configs_by_project(project_id)
            total_percentage = sum(config.profit_percentage for config in configs)
            
            return {
                'valid': total_percentage <= 100,
                'total_percentage': total_percentage,
                'excess_percentage': max(0, total_percentage - 100),
                'config_count': len(configs)
            }
            
        except Exception as e:
            print(f"Error validating profit sharing percentages: {str(e)}")
            return {
                'valid': False,
                'total_percentage': 0,
                'excess_percentage': 0,
                'config_count': 0
            }

    def get_company_profit_summary(self, company_name: str = None):
        """Get profit summary for a specific company or all companies"""
        try:
            from sqlalchemy import func
            
            query = self.db.query(
                ProfitSharingConfig.assigned_person_company,
                func.count(ProfitSharingConfig.id).label('project_count'),
                func.avg(ProfitSharingConfig.profit_percentage).label('avg_percentage'),
                func.sum(ProfitSharingConfig.profit_percentage).label('total_percentage')
            )
            
            if company_name:
                query = query.filter(ProfitSharingConfig.assigned_person_company == company_name)
            
            company_summary = query.group_by(
                ProfitSharingConfig.assigned_person_company
            ).all()
            
            return [{
                'company_name': summary.assigned_person_company,
                'project_count': summary.project_count,
                'avg_percentage': round(summary.avg_percentage or 0, 1),
                'total_percentage': round(summary.total_percentage or 0, 1)
            } for summary in company_summary]
            
        except Exception as e:
            print(f"Error getting company profit summary: {str(e)}")
            return []
    # -----
    def update_project_status_automatically(self, project_id: int, trigger: str = None):
        """Automatically update project status based on activities - NEW FUNCTION"""
        try:
            project = self.get_project_by_id(project_id)
            if not project:
                return False
            
            # Don't auto-update if project is already completed or cancelled
            if project.status in ['completed', 'cancelled']:
                return False
            
            # Determine new status based on project activities
            new_status = self._determine_project_status(project_id, trigger)
            
            if new_status and new_status != project.status:
                old_status = project.status
                project.status = new_status
                project.updated_at = datetime.now()
                self.db.commit()
                
                print(f"✅ Project #{project_id} status updated: {old_status} → {new_status}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating project status: {str(e)}")
            return False

    def _determine_project_status(self, project_id: int, trigger: str = None):
        """Determine appropriate project status based on activities"""
        try:
            # Check for various project activities
            has_projections = len(self.get_initial_projections_by_project(project_id)) > 0
            has_final_costs = len(self.get_final_costs_by_project(project_id)) > 0
            has_disbursements = len(self.get_disbursements_by_project(project_id)) > 0
            has_profit_sharing = len(self.get_profit_sharing_configs_by_project(project_id)) > 0
            
            # Get project for current status
            project = self.get_project_by_id(project_id)
            current_status = project.status
            
            # Status determination logic
            if trigger == 'invoice_created':
                return 'invoice_submitted'
            elif trigger == 'final_bill_collected':
                return 'completed'
            elif has_final_costs and has_disbursements:
                return 'active'
            elif has_projections:
                return 'active'
            elif current_status == 'new':
                # Keep as new until projections are created
                return 'new'
            else:
                return None  # No status change needed
                
        except Exception as e:
            print(f"Error determining project status: {str(e)}")
            return None

    def get_project_status_history(self, project_id: int):
        """Get project status change history - PLACEHOLDER for future enhancement"""
        # This would require a new table to track status changes
        # For now, return current status info
        try:
            project = self.get_project_by_id(project_id)
            if project:
                return [{
                    'status': project.status,
                    'changed_at': project.updated_at or project.created_at,
                    'changed_by': 'System'
                }]
            return []
        except Exception as e:
            print(f"Error getting status history: {str(e)}")
            return []

    def trigger_status_update(self, project_id: int, trigger: str):
        """Manually trigger a status update with specific trigger"""
        return self.update_project_status_automatically(project_id, trigger)
#----

# Test function for disbursement operations
def test_disbursement_operations():
    """Test disbursement and money receipt operations"""
    print("Testing disbursement operations...")
    
    db_ops = DatabaseOperations()
    
    try:
        # Get a test project
        projects = db_ops.get_all_projects()
        if not projects:
            print("❌ No projects found for testing")
            return
        
        test_project = projects[0]
        print(f"✅ Using test project: {test_project.project_name}")
        
        # Create test disbursement
        disbursement = db_ops.create_disbursement(
            project_id=test_project.id,
            disbursement_type="project_cost",
            amount=50000.0,
            disbursement_date=datetime.now(),
            description="Test project cost disbursement",
            created_by=1  # Assuming admin user ID
        )
        print(f"✅ Created disbursement: #{disbursement.id}")
        
        # Create test money receipt
        receipt = db_ops.create_money_receipt(
            project_id=test_project.id,
            disbursement_id=disbursement.id,
            receipt_number="MR-20250724-001",
            amount=50000.0,
            received_from="Test Company Ltd.",
            received_by="John Doe",
            receipt_date=datetime.now().date()
        )
        print(f"✅ Created money receipt: {receipt.receipt_number}")
        
        # Test retrieval
        retrieved_disbursement = db_ops.get_disbursement_by_id(disbursement.id)
        print(f"✅ Retrieved disbursement: {retrieved_disbursement.description}")
        
        retrieved_receipt = db_ops.get_money_receipt_by_disbursement(disbursement.id)
        print(f"✅ Retrieved receipt: {retrieved_receipt.receipt_number}")
        
        # Test statistics
        stats = db_ops.get_disbursement_statistics()
        print(f"✅ Disbursement statistics: {stats}")
        
        # Test financial summary
        summary = db_ops.get_financial_summary_with_disbursements(test_project.id)
        if summary:
            print(f"✅ Financial summary: Total disbursed: ৳{summary['total_disbursed']:,.2f}")
        
        print("✅ Disbursement operations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Disbursement operations test failed: {str(e)}")
    
    finally:
        db_ops.close()
        
# Test function for financial projections
def test_financial_projections():
    """Test financial projection operations"""
    print("Testing financial projection operations...")
    
    db_ops = DatabaseOperations()
    
    try:
        # Get a test project
        projects = db_ops.get_all_projects()
        if not projects:
            print("❌ No projects found for testing")
            return
        
        test_project = projects[0]
        print(f"✅ Using test project: {test_project.project_name}")
        
        # Create test projections
        projections_data = [
            {'sl_no': 1, 'particulars': 'Project Management', 'days': 30, 'qty': 1, 'unit_price': 1000, 'amount': 30000},
            {'sl_no': 2, 'particulars': 'Design Work', 'days': 15, 'qty': 2, 'unit_price': 1500, 'amount': 45000},
            {'sl_no': 3, 'particulars': 'Development', 'days': 45, 'qty': 1, 'unit_price': 2000, 'amount': 90000}
        ]
        
        # Delete existing projections first
        db_ops.delete_initial_projections_by_project(test_project.id)
        
        # Create new projections
        for proj_data in projections_data:
            projection = db_ops.create_initial_projection(
                project_id=test_project.id,
                **proj_data
            )
            print(f"✅ Created projection: {projection.particulars}")
        
        # Test retrieval
        projections = db_ops.get_initial_projections_by_project(test_project.id)
        print(f"✅ Retrieved {len(projections)} projections")
        
        # Test total calculation
        total = db_ops.get_total_projection_amount_by_project(test_project.id)
        print(f"✅ Total projection amount: ৳{total:,.2f}")
        
        # Test summary
        summary = db_ops.get_all_financial_projections_summary()
        print(f"✅ Financial summary: {summary}")
        
        print("✅ Financial projection operations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Financial projection test failed: {str(e)}")
    
    finally:
        db_ops.close()
        
# Add this test function at the end
def test_enhanced_dashboard_operations():
    """Test enhanced dashboard operations"""
    print("Testing enhanced dashboard operations...")
    
    db_ops = DatabaseOperations()
    
    try:
        # Test enhanced statistics
        stats = db_ops.get_enhanced_project_statistics()
        print(f"✅ Enhanced statistics: {stats}")
        
        # Test overdue projects
        overdue = db_ops.get_overdue_projects()
        print(f"✅ Overdue projects: {len(overdue)}")
        
        # Test upcoming deadlines
        upcoming = db_ops.get_upcoming_deadline_projects()
        print(f"✅ Upcoming deadlines: {len(upcoming)}")
        
        # Test status distribution
        status_dist = db_ops.get_project_status_distribution()
        print(f"✅ Status distribution: {status_dist}")
        
        # Test monthly stats
        monthly = db_ops.get_monthly_project_creation_stats()
        print(f"✅ Monthly creation stats: {len(monthly)} months")
        
        # Test revenue by status
        revenue_status = db_ops.get_revenue_by_status()
        print(f"✅ Revenue by status: {revenue_status}")
        
        # Test top clients
        top_clients = db_ops.get_top_clients_by_revenue()
        print(f"✅ Top clients: {len(top_clients)}")
        
        print("✅ Enhanced dashboard operations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Enhanced dashboard operations test failed: {str(e)}")
    
    finally:
        db_ops.close()

def get_db_operations():
    """Get database operations instance"""
    return DatabaseOperations()

# Enhanced test functions
def test_enhanced_operations():
    """Test enhanced database operations"""
    print("Testing enhanced database operations...")
    
    db_ops = DatabaseOperations()
    
    try:
        # Test creating an enhanced company
        company = db_ops.create_enhanced_company(
            name="Enhanced Test Company Ltd.",
            company_type="customer",
            address="123 Test Street",
            city="Dhaka",
            postal_code="1200",
            phone="+8801234567890",
            email="test@enhanced.com",
            website="https://enhanced.com",
            contact_person="John Enhanced",
            designation="Enhanced Manager",
            tax_id="123456789",
            notes="This is an enhanced company record"
        )
        print(f"✅ Created enhanced company: {company.name}")
        
        # Test updating the company
        updated = db_ops.update_company(
            company_id=company.id,
            name="Updated Enhanced Company",
            company_type="customer",
            address="456 Updated Street",
            city="Updated City",
            postal_code="1300"
        )
        print(f"✅ Updated company: {updated.name}")
        
        # Test creating an enhanced task
        task = db_ops.create_enhanced_task_description(
            task_name="Enhanced Project Management",
            description="Advanced project management with enhanced features",
            default_percentage=15.0,
            is_active=True
        )
        print(f"✅ Created enhanced task: {task.task_name}")
        
        # Test statistics
        stats = db_ops.get_project_statistics()
        print(f"✅ Statistics: {stats}")
        
        print("✅ Enhanced database operations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Enhanced database operations test failed: {str(e)}")
    
    finally:
        db_ops.close()

# Test functions (keep existing)
def test_database_operations():
    """Test basic database operations"""
    print("Testing database operations...")
    
    db_ops = DatabaseOperations()
    
    try:
        # Test creating a company
        company = db_ops.create_company(
            name="Test Company Ltd.",
            company_type="customer",
            address="123 Test Street",
            phone="+1234567890",
            email="test@company.com"
        )
        print(f"✅ Created company: {company.name}")
        
        # Test creating a task description
        task = db_ops.create_task_description(
            task_name="Project Management",
            description="Overall project management and coordination"
        )
        print(f"✅ Created task: {task.task_name}")
        
        # Test statistics
        stats = db_ops.get_project_statistics()
        print(f"✅ Statistics: {stats}")
        
        print("✅ Database operations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database operations test failed: {str(e)}")
    
    finally:
        db_ops.close()

if __name__ == "__main__":
    test_enhanced_dashboard_operations()
    test_database_operations()
    test_enhanced_operations()
    test_financial_projections()
    test_disbursement_operations()