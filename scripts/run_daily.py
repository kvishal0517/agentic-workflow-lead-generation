import argparse
import asyncio
import yaml
import os
from loguru import logger
from dotenv import load_dotenv
from src.agents.graph import create_lead_hunter_graph
from src.database.models import SessionLocal, Run
from datetime import datetime
import httpx

load_dotenv()

async def notify_slack(summary: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={"text": summary})
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")

async def run_pipeline(dry_run: bool = False):
    logger.info(f"Starting Lead Hunter Pipeline (Dry Run: {dry_run})")
    
    # 1. Load ICP
    with open("config/icp.yaml", "r") as f:
        icp_config = yaml.safe_load(f)
    
    # 2. Initialize DB Run
    db = SessionLocal()
    run = Run(status="running", start_time=datetime.utcnow())
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # 3. Create Initial State
    initial_state = {
        "run_id": run.id,
        "icp_config": icp_config,
        "queries": [],
        "raw_leads": [],
        "enriched_leads": [],
        "validated_leads": [],
        "scored_leads": [],
        "final_leads": [],
        "error": None,
        "dry_run": dry_run
    }
    
    # 4. Run Graph
    graph = create_lead_hunter_graph()
    try:
        final_state = await graph.ainvoke(initial_state)
        
        if final_state.get("error"):
            logger.error(f"Pipeline error: {final_state['error']}")
            summary = f"❌ Lead Hunter Run #{run.id} FAILED: {final_state['error']}"
        else:
            summary = f"✅ Lead Hunter Run #{run.id} COMPLETED\n- Leads Found: {len(final_state['final_leads'])}\n- Drafts Created: {len([l for l in final_state['final_leads'] if l.subject])}"
            if dry_run:
                summary = "[DRY RUN] " + summary
                
        logger.success(summary)
        await notify_slack(summary)
        
        # Print table for demo if dry-run
        if dry_run:
            print("\n--- MOCK LEADS PREVIEW ---")
            print(f"{'Company':<25} | {'Email':<25} | {'Score':<5} | {'Subject'}")
            print("-" * 80)
            for lead in final_state['final_leads']:
                print(f"{str(lead.company_name)[:25]:<25} | {str(lead.email)[:25]:<25} | {lead.score:<5.1f} | {lead.subject}")
                
    except Exception as e:
        logger.exception(f"Pipeline crashed: {e}")
        run.status = "failed"
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without creating real Gmail drafts")
    parser.add_argument("--live", action="store_true", help="Run the full pipeline")
    args = parser.parse_args()
    
    if args.dry_run or not args.live:
        asyncio.run(run_pipeline(dry_run=True))
    else:
        asyncio.run(run_pipeline(dry_run=False))
