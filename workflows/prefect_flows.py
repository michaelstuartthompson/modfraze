"""
Prefect workflows for orchestrating the viral merch pipeline.
Run with: python workflows/prefect_flows.py
"""
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
from datetime import timedelta
import os

from db.database import init_db
from pipeline.ingest_tiktok import main as ingest_tiktok
from pipeline.generate_designs import generate_designs_for_top_trends
from pipeline.manage_campaigns import CampaignManager


# ============================================================================
# TASKS
# ============================================================================

@task(name="Initialize Database", retries=2)
def initialize_database():
    """Ensure database is initialized"""
    init_db()
    return True


@task(name="Ingest TikTok Trends", retries=3, retry_delay_seconds=60)
def task_ingest_tiktok():
    """Scrape trending TikTok content"""
    ingest_tiktok()
    return True


@task(name="Ingest Reddit Trends", retries=3, retry_delay_seconds=60)
def task_ingest_reddit():
    """Scrape trending Reddit content"""
    # TODO: Implement when ready
    print("⏭️  Reddit ingestion - coming soon")
    return True


@task(name="Ingest Twitter Trends", retries=3, retry_delay_seconds=60)
def task_ingest_twitter():
    """Scrape trending Twitter content"""
    # TODO: Implement when ready
    print("⏭️  Twitter ingestion - coming soon")
    return True


@task(name="Generate Designs for Top Trends", retries=2)
def task_generate_designs(limit: int = 5, min_score: float = 0.6):
    """Generate designs for trending topics"""
    results = generate_designs_for_top_trends(
        limit=limit,
        min_virality_score=min_score,
        designs_per_trend=1
    )
    return results


@task(name="Monitor and Optimize Campaigns", retries=2)
def task_monitor_campaigns():
    """Monitor active campaigns and apply kill/boost logic"""
    manager = CampaignManager()
    results = manager.monitor_and_optimize_campaigns()
    return results


@task(name="Send Notification", retries=2)
def task_send_notification(message: str):
    """Send notification (email/Slack/etc.)"""
    # TODO: Implement notification system
    print(f"📧 NOTIFICATION: {message}")
    return True


# ============================================================================
# FLOWS
# ============================================================================

@flow(
    name="Trend Detection Flow",
    description="Scrape social platforms and detect viral trends",
    task_runner=ConcurrentTaskRunner()
)
def trend_detection_flow():
    """
    Main flow for trend detection.
    Runs on schedule (every 4 hours recommended).
    """
    
    print("\n" + "="*60)
    print("🔍 TREND DETECTION FLOW STARTED")
    print("="*60 + "\n")
    
    # Initialize database
    initialize_database()
    
    # Run scrapers in parallel
    tiktok_result = task_ingest_tiktok.submit()
    reddit_result = task_ingest_reddit.submit()
    twitter_result = task_ingest_twitter.submit()
    
    # Wait for all scrapers
    tiktok_result.wait()
    reddit_result.wait()
    twitter_result.wait()
    
    print("\n✅ Trend detection flow completed\n")
    
    return {
        "tiktok": tiktok_result.result(),
        "reddit": reddit_result.result(),
        "twitter": twitter_result.result()
    }


@flow(
    name="Design Generation Flow",
    description="Generate designs for top viral trends"
)
def design_generation_flow(limit: int = 5, min_score: float = 0.6):
    """
    Flow for generating designs.
    Runs after trend detection or on schedule.
    """
    
    print("\n" + "="*60)
    print("🎨 DESIGN GENERATION FLOW STARTED")
    print("="*60 + "\n")
    
    # Generate designs
    results = task_generate_designs(limit=limit, min_score=min_score)
    
    # Send notification if designs created
    if results["designs_created"] > 0:
        message = (
            f"🎨 {results['designs_created']} new designs ready for approval!\n"
            f"Trends processed: {results['trends_processed']}\n"
            f"View at: http://localhost:8501"
        )
        task_send_notification(message)
    
    print("\n✅ Design generation flow completed\n")
    
    return results


@flow(
    name="Campaign Monitoring Flow",
    description="Monitor active campaigns and optimize performance"
)
def campaign_monitoring_flow():
    """
    Flow for campaign monitoring.
    Runs every 6 hours to check performance.
    """
    
    print("\n" + "="*60)
    print("📊 CAMPAIGN MONITORING FLOW STARTED")
    print("="*60 + "\n")
    
    # Monitor campaigns
    results = task_monitor_campaigns()
    
    # Send notification if actions taken
    if results["killed"] or results["boosted"]:
        message = (
            f"📊 Campaign monitoring complete:\n"
            f"Monitored: {results['monitored']}\n"
            f"Killed: {len(results['killed'])}\n"
            f"Boosted: {len(results['boosted'])}"
        )
        task_send_notification(message)
    
    print("\n✅ Campaign monitoring flow completed\n")
    
    return results


@flow(
    name="Daily Master Flow",
    description="Master orchestration flow - runs all pipeline stages"
)
def daily_master_flow():
    """
    Master flow that coordinates all pipeline stages.
    Run this on a daily schedule.
    """
    
    print("\n" + "="*80)
    print("🚀 DAILY MASTER FLOW STARTED")
    print("="*80 + "\n")
    
    # Stage 1: Detect trends
    trend_results = trend_detection_flow()
    
    # Stage 2: Generate designs for top trends
    design_results = design_generation_flow(limit=3, min_score=0.7)
    
    # Stage 3: Monitor campaigns
    campaign_results = campaign_monitoring_flow()
    
    # Summary
    summary = {
        "trends": trend_results,
        "designs": design_results,
        "campaigns": campaign_results,
        "timestamp": "2024-01-01 00:00:00"  # Prefect will add real timestamp
    }
    
    print("\n" + "="*80)
    print("✅ DAILY MASTER FLOW COMPLETED")
    print("="*80 + "\n")
    
    return summary


# ============================================================================
# DEPLOYMENT & SCHEDULING
# ============================================================================

def deploy_flows():
    """
    Deploy flows to Prefect Cloud for scheduling.
    Run once to set up deployments.
    """
    
    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import CronSchedule
    
    # Deploy trend detection (every 4 hours)
    trend_deployment = Deployment.build_from_flow(
        flow=trend_detection_flow,
        name="trend-detection-4h",
        schedule=CronSchedule(cron="0 */4 * * *"),  # Every 4 hours
        work_queue_name="default"
    )
    trend_deployment.apply()
    
    # Deploy design generation (every 6 hours)
    design_deployment = Deployment.build_from_flow(
        flow=design_generation_flow,
        name="design-generation-6h",
        schedule=CronSchedule(cron="0 */6 * * *"),  # Every 6 hours
        parameters={"limit": 5, "min_score": 0.6},
        work_queue_name="default"
    )
    design_deployment.apply()
    
    # Deploy campaign monitoring (every 6 hours)
    campaign_deployment = Deployment.build_from_flow(
        flow=campaign_monitoring_flow,
        name="campaign-monitoring-6h",
        schedule=CronSchedule(cron="0 */6 * * *"),  # Every 6 hours
        work_queue_name="default"
    )
    campaign_deployment.apply()
    
    # Deploy daily master (once per day at 8am)
    master_deployment = Deployment.build_from_flow(
        flow=daily_master_flow,
        name="daily-master-8am",
        schedule=CronSchedule(cron="0 8 * * *"),  # 8am daily
        work_queue_name="default"
    )
    master_deployment.apply()
    
    print("\n✅ All flows deployed to Prefect Cloud")
    print("\nSchedules:")
    print("  - Trend Detection: Every 4 hours")
    print("  - Design Generation: Every 6 hours")
    print("  - Campaign Monitoring: Every 6 hours")
    print("  - Daily Master: 8am daily")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python workflows/prefect_flows.py run trends")
        print("  python workflows/prefect_flows.py run designs")
        print("  python workflows/prefect_flows.py run campaigns")
        print("  python workflows/prefect_flows.py run daily")
        print("  python workflows/prefect_flows.py deploy")
        print("\nExamples:")
        print("  # Run trend detection once")
        print("  python workflows/prefect_flows.py run trends")
        print("\n  # Deploy to Prefect Cloud with schedules")
        print("  python workflows/prefect_flows.py deploy")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "run":
        if len(sys.argv) < 3:
            print("Error: Specify which flow to run")
            sys.exit(1)
        
        flow_name = sys.argv[2]
        
        if flow_name == "trends":
            trend_detection_flow()
        elif flow_name == "designs":
            design_generation_flow()
        elif flow_name == "campaigns":
            campaign_monitoring_flow()
        elif flow_name == "daily":
            daily_master_flow()
        else:
            print(f"Unknown flow: {flow_name}")
            sys.exit(1)
    
    elif command == "deploy":
        deploy_flows()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
