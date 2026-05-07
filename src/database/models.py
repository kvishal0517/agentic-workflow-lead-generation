from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Run(Base):
    __tablename__ = 'runs'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String)  # completed, failed, dry-run
    leads_found = Column(Integer, default=0)
    drafts_created = Column(Integer, default=0)

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('runs.id'))
    domain = Column(String, unique=True)
    company_name = Column(String)
    industry = Column(String)
    website_url = Column(String)
    description = Column(Text)
    
    # Enrichment
    email = Column(String)
    decision_maker_name = Column(String)
    decision_maker_role = Column(String)
    
    # Validation & Scoring
    is_valid = Column(Boolean, default=False)
    validation_reason = Column(String)
    score = Column(Float)
    score_breakdown = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    run = relationship("Run", back_populates="leads")
    draft = relationship("Draft", uselist=False, back_populates="lead")
    evidence = relationship("Evidence", back_populates="lead")

Run.leads = relationship("Lead", order_by=Lead.id, back_populates="run")

class Draft(Base):
    __tablename__ = 'drafts'
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    gmail_draft_id = Column(String)
    subject = Column(String)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="draft")

class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    source_url = Column(String)
    content_snippet = Column(Text)
    evidence_type = Column(String) # search_result, scraping, llm_inference
    
    lead = relationship("Lead", back_populates="evidence")
