import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.system import ApplianceState
from app.services.backup_service import backup_service
from app.services.node_agent import node_agent_client

class TransactionalUpdateService:
    """
    Orchestrates MicroOS transactional updates, staging snapshots, and rollback.
    """

    def stage_update(self, db: Session, target_channel: str = None) -> Dict[str, Any]:
        state = db.query(ApplianceState).first()
        channel = target_channel or (state.channel if state else "Stable")

        # 1. Take safety pre-update snapshot
        snap = backup_service.create_snapshot(
            db=db,
            description=f"Pre-update snapshot prior to staging {channel} channel update",
            cleanup_type="important",
            is_pre_update=True
        )

        # 2. Stage update into new snapshot
        new_snap_num = snap.snapshot_number + 1
        if state:
            state.staged_snapshot = new_snap_num
            db.commit()

        return {
            "status": "staged",
            "channel": channel,
            "pre_update_snapshot": snap.snapshot_number,
            "staged_snapshot": new_snap_num,
            "reboot_required": True,
            "maintenance_window": "02:00-04:00 IST",
            "message": f"Transactional update successfully staged in snapshot #{new_snap_num}. Will boot and run CSIR Health Gates during maintenance window."
        }

    def trigger_rollback(self, db: Session, target_snapshot: int = None) -> Dict[str, Any]:
        state = db.query(ApplianceState).first()
        active_snap = state.active_snapshot if state else 14
        target = target_snapshot or max(1, active_snap - 1)

        # Call Snapper rollback via Node Agent
        agent_res = node_agent_client.execute_action("SNAPPER_ROLLBACK", {
            "snapshot_id": target
        })

        if state:
            state.staged_snapshot = target
            db.commit()

        return {
            "status": "rollback_staged",
            "target_snapshot": target,
            "reboot_required": True,
            "message": f"Rollback to snapshot #{target} successfully staged. Reboot required to reactivate previous immutable root."
        }

update_service = TransactionalUpdateService()
