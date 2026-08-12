"""
Streamlit approval dashboard for design review.
Run with: streamlit run ui/approval_dashboard.py
"""
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

from db.database import SessionLocal
from db.models import Trend, Design, DesignStatus, TrendStatus
from pipeline.generate_designs import approve_design, reject_design, regenerate_design


# Page config
st.set_page_config(
    page_title="Viral Merch - Design Approval",
    page_icon="🎨",
    layout="wide"
)


def load_pending_designs():
    """Load all designs pending approval"""
    session = SessionLocal()
    try:
        designs = (
            session.query(Design)
            .filter(Design.status == DesignStatus.PENDING_APPROVAL)
            .order_by(Design.generated_at.desc())
            .all()
        )
        
        # Convert to dicts for Streamlit
        return [
            {
                "id": d.id,
                "trend_id": d.trend_id,
                "trend_text": d.trend.text,
                "trend_source": d.trend.source,
                "virality_score": d.trend.virality_score,
                "image_url": d.image_url,
                "prompt": d.prompt,
                "design_type": d.design_type,
                "generated_at": d.generated_at,
            }
            for d in designs
        ]
    finally:
        session.close()


def load_recent_decisions(days: int = 7):
    """Load recently approved/rejected designs"""
    session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        designs = (
            session.query(Design)
            .filter(
                Design.status.in_([DesignStatus.APPROVED, DesignStatus.REJECTED]),
                Design.updated_at >= cutoff
            )
            .order_by(Design.updated_at.desc())
            .limit(20)
            .all()
        )
        
        return [
            {
                "id": d.id,
                "trend_text": d.trend.text,
                "status": d.status.value,
                "image_url": d.image_url,
                "notes": d.approval_notes,
                "decided_at": d.approved_at or d.rejected_at,
            }
            for d in designs
        ]
    finally:
        session.close()


def main():
    st.title("🎨 Viral Merch Design Approval Dashboard")
    
    # Sidebar stats
    st.sidebar.header("📊 Stats")
    session = SessionLocal()
    try:
        total_designs = session.query(Design).count()
        pending = session.query(Design).filter(Design.status == DesignStatus.PENDING_APPROVAL).count()
        approved = session.query(Design).filter(Design.status == DesignStatus.APPROVED).count()
        
        st.sidebar.metric("Total Designs", total_designs)
        st.sidebar.metric("Pending Approval", pending, delta=f"{pending} waiting")
        st.sidebar.metric("Approved", approved)
    finally:
        session.close()
    
    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Pending Approvals", "📋 Recent Decisions"])
    
    # TAB 1: Pending approvals
    with tab1:
        pending_designs = load_pending_designs()
        
        if not pending_designs:
            st.success("✅ No designs pending approval!")
            st.balloons()
        else:
            st.header(f"Pending Approvals ({len(pending_designs)})")
            
            for design in pending_designs:
                with st.expander(f"🎨 Design #{design['id']} - {design['trend_text'][:60]}...", expanded=True):
                    col1, col2 = st.columns([1, 2])
                    
                    # Left column: Image
                    with col1:
                        if Path(design['image_url']).exists():
                            st.image(design['image_url'], use_container_width=True)
                        else:
                            st.warning(f"Image not found: {design['image_url']}")
                    
                    # Right column: Details and actions
                    with col2:
                        st.subheader("Trend Details")
                        st.write(f"**Source:** {design['trend_source']}")
                        st.write(f"**Virality Score:** {design['virality_score']:.2f}")
                        st.write(f"**Generated:** {design['generated_at'].strftime('%Y-%m-%d %H:%M')}")
                        
                        st.subheader("Design Details")
                        st.write(f"**Type:** {design['design_type']}")
                        with st.expander("View DALL-E Prompt"):
                            st.text(design['prompt'])
                        
                        st.subheader("Trend Text")
                        st.info(design['trend_text'])
                        
                        # Approval form
                        st.subheader("Decision")
                        notes = st.text_area(
                            "Notes (optional)",
                            key=f"notes_{design['id']}",
                            placeholder="Add any feedback or modifications..."
                        )
                        
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            if st.button("✅ Approve", key=f"approve_{design['id']}", type="primary"):
                                approve_design(design['id'], notes=notes)
                                st.success(f"Design {design['id']} approved!")
                                st.rerun()
                        
                        with col_b:
                            if st.button("❌ Reject", key=f"reject_{design['id']}"):
                                reject_design(design['id'], notes=notes)
                                st.warning(f"Design {design['id']} rejected")
                                st.rerun()
                        
                        with col_c:
                            if st.button("🔄 Regenerate", key=f"regen_{design['id']}"):
                                new_id = regenerate_design(design['id'])
                                st.info(f"New design created: {new_id}")
                                st.rerun()
                    
                    st.divider()
    
    # TAB 2: Recent decisions
    with tab2:
        st.header("Recent Decisions (Last 7 Days)")
        
        recent = load_recent_decisions()
        
        if not recent:
            st.info("No decisions in the last 7 days")
        else:
            for decision in recent:
                status_emoji = "✅" if decision['status'] == 'approved' else "❌"
                
                with st.expander(f"{status_emoji} Design #{decision['id']} - {decision['trend_text'][:50]}..."):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if Path(decision['image_url']).exists():
                            st.image(decision['image_url'], use_container_width=True)
                    
                    with col2:
                        st.write(f"**Status:** {decision['status'].upper()}")
                        st.write(f"**Decided:** {decision['decided_at'].strftime('%Y-%m-%d %H:%M')}")
                        
                        if decision['notes']:
                            st.write(f"**Notes:** {decision['notes']}")


if __name__ == "__main__":
    main()
