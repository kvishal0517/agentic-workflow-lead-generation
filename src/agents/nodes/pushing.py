from src.agents.state import AgentState
from src.utils.gmail import gmail
from src.database.models import Base, Run, Lead, Draft, Evidence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from loguru import logger
from datetime import datetime

# Setup DB
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./morning_leads.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

async def pushing_node(state: AgentState) -> AgentState:
    logger.info("Starting Pushing Node")
    db = SessionLocal()
    
    try:
        run = db.query(Run).filter(Run.id == state['run_id']).first()
        
        for lead_schema in state['final_leads']:
            # Create Lead in DB
            db_lead = Lead(
                run_id=state['run_id'],
                domain=lead_schema.domain,
                company_name=lead_schema.company_name,
                website_url=lead_schema.website_url,
                description=lead_schema.description,
                email=lead_schema.email,
                decision_maker_name=lead_schema.decision_maker_name,
                decision_maker_role=lead_schema.decision_maker_role,
                is_valid=lead_schema.is_valid,
                score=lead_schema.score,
                score_breakdown=lead_schema.score_breakdown
            )
            db.add(db_lead)
            db.flush() # Get lead ID
            
            # Create Evidence in DB
            for ev in lead_schema.evidence:
                db_ev = Evidence(
                    lead_id=db_lead.id,
                    source_url=ev.get("url"),
                    content_snippet=ev.get("content"),
                    evidence_type=ev.get("type")
                )
                db.add(db_ev)
            
            # Create Gmail Draft
            if lead_schema.email and lead_schema.subject and lead_schema.body_html:
                draft_id = gmail.create_draft(
                    to=lead_schema.email,
                    subject=lead_schema.subject,
                    body_html=lead_schema.body_html,
                    dry_run=state['dry_run']
                )
                
                if draft_id:
                    db_draft = Draft(
                        lead_id=db_lead.id,
                        gmail_draft_id=draft_id,
                        subject=lead_schema.subject,
                        body=lead_schema.body_html
                    )
                    db.add(db_draft)
                    run.drafts_created += 1
            
            run.leads_found += 1
            
        run.end_time = datetime.utcnow()
        run.status = "completed" if not state['dry_run'] else "dry-run"
        db.commit()
        logger.success(f"Pushing Node: Created {run.drafts_created} drafts and saved leads to database")
        
    except Exception as e:
        logger.error(f"Pushing Node failed: {e}")
        db.rollback()
        state['error'] = str(e)
    finally:
        db.close()
        
    return state
