"""
Design generation pipeline.
Generates designs from trending topics using DALL-E.
"""
import os
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

from db.database import SessionLocal
from db.models import Trend, Design, DesignStatus, TrendStatus
from tools.dalle_client import DALLEClient

load_dotenv()


def generate_designs_for_trend(
    trend_id: int,
    num_designs: int = 1,
    design_type: str = "graphic",
    style: str = "bold"
) -> List[int]:
    """
    Generate designs for a specific trend.
    
    Args:
        trend_id: Trend database ID
        num_designs: Number of design variations to generate
        design_type: Type of design (graphic, text, hybrid)
        style: Design style (bold, minimalist, retro, modern)
        
    Returns:
        List of created design IDs
    """
    
    session = SessionLocal()
    design_ids = []
    
    try:
        # Get trend
        trend = session.query(Trend).filter(Trend.id == trend_id).first()
        if not trend:
            raise ValueError(f"Trend {trend_id} not found")
        
        # Update trend status
        trend.status = TrendStatus.DESIGN_PENDING
        session.commit()
        
        print(f"\n🎨 Generating {num_designs} design(s) for trend: {trend.text[:60]}")
        
        # Initialize DALL-E client
        dalle = DALLEClient()
        
        # Generate designs
        for i in range(num_designs):
            print(f"\n--- Design {i+1}/{num_designs} ---")
            
            try:
                # Generate design
                prompt, image_path = dalle.generate_merch_design(
                    trend_text=trend.text,
                    design_type=design_type,
                    style=style
                )
                
                # Create design record
                design = Design(
                    trend_id=trend_id,
                    prompt=prompt,
                    image_url=image_path,
                    design_type=design_type,
                    status=DesignStatus.PENDING_APPROVAL,
                    generated_at=datetime.utcnow()
                )
                
                session.add(design)
                session.commit()
                session.refresh(design)
                
                design_ids.append(design.id)
                print(f"✅ Design created: ID {design.id}")
                
            except Exception as e:
                print(f"❌ Failed to generate design {i+1}: {e}")
                continue
        
        # Update trend status
        if design_ids:
            trend.status = TrendStatus.DESIGN_GENERATED
        session.commit()
        
        print(f"\n✅ Generated {len(design_ids)} design(s) for trend {trend_id}")
        
    finally:
        session.close()
    
    return design_ids


def generate_designs_for_top_trends(
    limit: int = 5,
    min_virality_score: float = 0.6,
    designs_per_trend: int = 1
) -> dict:
    """
    Generate designs for top trending topics.
    
    Args:
        limit: Max number of trends to process
        min_virality_score: Minimum virality score threshold
        designs_per_trend: Number of design variations per trend
        
    Returns:
        Dict with trends processed and designs created
    """
    
    session = SessionLocal()
    results = {
        "trends_processed": 0,
        "designs_created": 0,
        "design_ids": []
    }
    
    try:
        # Get top trends that don't have designs yet
        trends = (
            session.query(Trend)
            .filter(
                Trend.virality_score >= min_virality_score,
                Trend.status.in_([TrendStatus.DETECTED, TrendStatus.ANALYZING])
            )
            .order_by(Trend.virality_score.desc())
            .limit(limit)
            .all()
        )
        
        print(f"\n🔍 Found {len(trends)} trends above virality threshold {min_virality_score}")
        
        for trend in trends:
            print(f"\n{'='*60}")
            print(f"Processing trend {trend.id}: {trend.text[:80]}")
            print(f"Virality score: {trend.virality_score:.2f}")
            
            try:
                design_ids = generate_designs_for_trend(
                    trend_id=trend.id,
                    num_designs=designs_per_trend
                )
                
                results["trends_processed"] += 1
                results["designs_created"] += len(design_ids)
                results["design_ids"].extend(design_ids)
                
            except Exception as e:
                print(f"❌ Error processing trend {trend.id}: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ SUMMARY:")
        print(f"   Trends processed: {results['trends_processed']}")
        print(f"   Designs created: {results['designs_created']}")
        
    finally:
        session.close()
    
    return results


def regenerate_design(design_id: int, style: Optional[str] = None) -> int:
    """
    Regenerate a design (e.g., if user requests different style).
    
    Args:
        design_id: Design to regenerate
        style: New style to use (optional)
        
    Returns:
        New design ID
    """
    
    session = SessionLocal()
    
    try:
        # Get original design
        original = session.query(Design).filter(Design.id == design_id).first()
        if not original:
            raise ValueError(f"Design {design_id} not found")
        
        trend = original.trend
        
        print(f"\n🔄 Regenerating design {design_id}")
        
        # Generate new design
        dalle = DALLEClient()
        prompt, image_path = dalle.generate_merch_design(
            trend_text=trend.text,
            design_type=original.design_type,
            style=style or "bold"
        )
        
        # Create new design record
        new_design = Design(
            trend_id=trend.id,
            prompt=prompt,
            image_url=image_path,
            design_type=original.design_type,
            status=DesignStatus.PENDING_APPROVAL,
            generated_at=datetime.utcnow()
        )
        
        session.add(new_design)
        session.commit()
        session.refresh(new_design)
        
        print(f"✅ New design created: ID {new_design.id}")
        
        return new_design.id
        
    finally:
        session.close()


def approve_design(design_id: int, notes: Optional[str] = None) -> bool:
    """
    Approve a design for production.
    
    Args:
        design_id: Design to approve
        notes: Optional approval notes
        
    Returns:
        True if successful
    """
    
    session = SessionLocal()
    
    try:
        design = session.query(Design).filter(Design.id == design_id).first()
        if not design:
            raise ValueError(f"Design {design_id} not found")
        
        design.status = DesignStatus.APPROVED
        design.approved_at = datetime.utcnow()
        design.approval_notes = notes
        
        session.commit()
        
        print(f"✅ Design {design_id} approved")
        return True
        
    finally:
        session.close()


def reject_design(design_id: int, notes: Optional[str] = None) -> bool:
    """
    Reject a design.
    
    Args:
        design_id: Design to reject
        notes: Optional rejection reason
        
    Returns:
        True if successful
    """
    
    session = SessionLocal()
    
    try:
        design = session.query(Design).filter(Design.id == design_id).first()
        if not design:
            raise ValueError(f"Design {design_id} not found")
        
        design.status = DesignStatus.REJECTED
        design.rejected_at = datetime.utcnow()
        design.approval_notes = notes
        
        session.commit()
        
        print(f"✅ Design {design_id} rejected")
        return True
        
    finally:
        session.close()


# Command-line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_designs.py top [limit]")
        print("  python generate_designs.py trend <trend_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "top":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = generate_designs_for_top_trends(limit=limit)
        
    elif command == "trend":
        if len(sys.argv) < 3:
            print("Error: trend_id required")
            sys.exit(1)
        
        trend_id = int(sys.argv[2])
        design_ids = generate_designs_for_trend(trend_id=trend_id)
        print(f"\nCreated designs: {design_ids}")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
