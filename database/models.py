from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # admin, user, finance
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    company_type = Column(String(20), nullable=False)  # customer, supplier
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    contact_person = Column(String(100))
    designation = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    po_issuing_projects = relationship("Project", foreign_keys="Project.po_issuing_company_id", back_populates="po_issuing_company")
    supplier_projects = relationship("Project", foreign_keys="Project.supplier_company_id", back_populates="supplier_company")

class TaskDescription(Base):
    __tablename__ = "task_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profit_sharing_configs = relationship("ProfitSharingConfig", back_populates="task_description")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(200), nullable=False)
    po_number = Column(String(100))
    po_issuing_company_id = Column(Integer, ForeignKey("companies.id"))
    supplier_company_id = Column(Integer, ForeignKey("companies.id"))
    start_date = Column(Date)
    tentative_end_date = Column(Date)
    actual_end_date = Column(Date)
    status = Column(String(20), default="new")  # new, active, invoice_submitted, completed, cancelled, on_hold
    total_po_value = Column(Float, default=0.0)
    vat_rate = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)
    ait_rate = Column(Float, default=0.0)
    ait_amount = Column(Float, default=0.0)
    final_po_value = Column(Float, default=0.0)
    project_advance_percentage = Column(Float, default=0.0)
    project_advance_amount = Column(Float, default=0.0)
    invoice_submission_date = Column(Date)
    final_bill_collection_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    po_issuing_company = relationship("Company", foreign_keys=[po_issuing_company_id], back_populates="po_issuing_projects")
    supplier_company = relationship("Company", foreign_keys=[supplier_company_id], back_populates="supplier_projects")
    documents = relationship("ProjectDocument", back_populates="project")
    initial_projections = relationship("InitialFinancialProjection", back_populates="project")
    final_costs = relationship("FinalFinancialCost", back_populates="project")
    disbursements = relationship("Disbursement", back_populates="project")
    profit_sharing_configs = relationship("ProfitSharingConfig", back_populates="project")
    money_receipts = relationship("MoneyReceipt", back_populates="project")

class ProjectDocument(Base):
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_type = Column(String(50), nullable=False)  # po, generated_doc, receipt, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    uploader = relationship("User")

class InitialFinancialProjection(Base):
    __tablename__ = "initial_financial_projection"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    sl_no = Column(Integer, nullable=False)
    particulars = Column(String(500), nullable=False)
    days = Column(Float, default=0.0)
    qty = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="initial_projections")

class FinalFinancialCost(Base):
    __tablename__ = "final_financial_cost"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    sl_no = Column(Integer, nullable=False)
    particulars = Column(String(500), nullable=False)
    days = Column(Float, default=0.0)
    qty = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)  # From initial projection
    real_cost = Column(Float, default=0.0)  # Actual cost
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="final_costs")

class Disbursement(Base):
    __tablename__ = "disbursements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    disbursement_type = Column(String(30), nullable=False)  # advance, project_cost, personal_loan
    amount = Column(Float, nullable=False)
    disbursement_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="disbursements")
    creator = relationship("User")
    money_receipt = relationship("MoneyReceipt", back_populates="disbursement", uselist=False)

class ProfitSharingConfig(Base):
    __tablename__ = "profit_sharing_config"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    task_description_id = Column(Integer, ForeignKey("task_descriptions.id"))
    profit_percentage = Column(Float, nullable=False)
    assigned_person_company = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="profit_sharing_configs")
    task_description = relationship("TaskDescription", back_populates="profit_sharing_configs")

class MoneyReceipt(Base):
    __tablename__ = "money_receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    disbursement_id = Column(Integer, ForeignKey("disbursements.id"))
    receipt_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    received_from = Column(String(200), nullable=False)
    received_by = Column(String(200), nullable=False)
    receipt_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="money_receipts")
    disbursement = relationship("Disbursement", back_populates="money_receipt")