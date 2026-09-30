#!/usr/bin/env python3
"""
CSIR-SWA OS Unified Appliance CLI (csir-ctl / csir-appliance)
Provides administrative commands matching the appliance lifecycle.
"""

import sys
import argparse
import json
import httpx

API_BASE = "http://127.0.0.1:8000/api/v1"

def cmd_status(args):
    try:
        r = httpx.get(f"{API_BASE}/system/status")
        if r.status_code == 200:
            data = r.json()
            print("==========================================================")
            print("         CSIR SECURE WEB APPLIANCE OS STATUS")
            print("==========================================================")
            print(f" Hostname:        {data['hostname']}")
            print(f" Organisation:    {data['organisation']}")
            print(f" OS Version:      {data['os_version']}")
            print(f" Update Channel:  {data['channel']}")
            print(f" Active Snapshot: #{data['active_snapshot']}")
            print(f" Staged Snapshot: #{data['staged_snapshot'] or 'None (Clean)'}")
            print(f" Health Status:   {data['health_status'].upper()}")
            print(f" CPU / Mem / Disk:{data['cpu_usage_percent']}% / {data['memory_usage_percent']}% / {data['disk_usage_percent']}%")
            print("==========================================================")
        else:
            print(f"Failed to fetch status: HTTP {r.status_code}")
    except Exception as e:
        print(f"Error communicating with local control plane: {e}")

def cmd_apps(args):
    if args.app_action == "list":
        r = httpx.get(f"{API_BASE}/applications")
        if r.status_code == 200:
            apps = r.json()
            print(f"{'APP ID':<16} {'NAME':<20} {'STATUS':<10} {'WAF':<10} {'DOMAIN':<25}")
            print("-" * 85)
            for a in apps:
                print(f"{a['app_id']:<16} {a['name']:<20} {a['status']:<10} {a['waf_mode']:<10} {a['domain']:<25}")
    elif args.app_action == "deploy":
        payload = {
            "name": args.name,
            "image": args.image,
            "port": args.port,
            "domain": args.domain,
            "waf_mode": "strict",
            "cpu_limit": 50,
            "memory_mb": 512
        }
        r = httpx.post(f"{API_BASE}/applications", json=payload)
        if r.status_code in [200, 201]:
            res = r.json()
            print(f"[✓] Application {res['name']} ({res['app_id']}) deployed successfully via Quadlet.")
        else:
            print(f"[!] Deployment failed: {r.text}")

def cmd_snapshot(args):
    if args.snap_action == "create":
        r = httpx.post(f"{API_BASE}/backups/snapshots", json={"description": args.desc or "Manual CLI Snapshot", "cleanup_type": "timeline"})
        if r.status_code == 200:
            res = r.json()
            print(f"[✓] Btrfs snapshot #{res['snapshot_number']} created: {res['description']}")
        else:
            print(f"[!] Snapshot failed: {r.text}")
    elif args.snap_action == "list":
        r = httpx.get(f"{API_BASE}/backups/snapshots")
        if r.status_code == 200:
            snaps = r.json()
            print(f"{'SNAP #':<8} {'SUBVOLUME':<12} {'TYPE':<12} {'DESCRIPTION':<35}")
            print("-" * 70)
            for s in snaps:
                print(f"{s['snapshot_number']:<8} {s['subvolume']:<12} {s['cleanup_type']:<12} {s['description']:<35}")

def cmd_rollback(args):
    r = httpx.post(f"{API_BASE}/updates/rollback")
    if r.status_code == 200:
        res = r.json()
        print(f"[✓] {res['message']}")
    else:
        print(f"[!] Rollback request failed: {r.text}")

def cmd_backup(args):
    if args.backup_action == "run":
        r = httpx.post(f"{API_BASE}/backups/runs/trigger")
        if r.status_code == 200:
            res = r.json()
            print(f"[✓] Restic backup completed: ID {res['backup_id']} ({res['bytes_transferred']} bytes)")
    elif args.backup_action == "dr-drill":
        r = httpx.post(f"{API_BASE}/backups/dr-tests/trigger")
        if r.status_code == 200:
            res = r.json()
            print(f"[✓] DR Restore drill PASSED: RTO={res['measured_rto_seconds']}s, RPO={res['measured_rpo_seconds']}s")

def cmd_audit(args):
    if args.audit_action == "verify":
        r = httpx.get(f"{API_BASE}/audit/verify")
        if r.status_code == 200:
            res = r.json()
            status_symbol = "[✓]" if res["is_valid"] else "[✗]"
            print(f"{status_symbol} {res['message']}")
            print(f"    Total Hash-Chained Entries: {res['total_entries']}")
            print(f"    Current Ledger Head:        {res['head_hash']}")
    elif args.audit_action == "cert-in":
        r = httpx.get(f"{API_BASE}/audit/cert-in-export")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))

def cmd_bundle(args):
    r = httpx.post(f"{API_BASE}/system/support-bundle")
    if r.status_code == 200:
        res = r.json()
        print(f"[✓] Generated signed support bundle: {res['bundle_filename']}")
        print(f"    SHA-256:   {res['sha256']}")
        print(f"    Signature: {res['signature']}")

def main():
    parser = argparse.ArgumentParser(description="CSIR Secure Web Appliance OS Administration CLI")
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Display appliance health and version status")

    # apps
    p_apps = subparsers.add_parser("apps", help="Manage container applications")
    sub_apps = p_apps.add_subparsers(dest="app_action")
    sub_apps.add_parser("list", help="List all deployed workloads")
    p_deploy = sub_apps.add_parser("deploy", help="Deploy new workload")
    p_deploy.add_argument("--name", required=True)
    p_deploy.add_argument("--image", required=True)
    p_deploy.add_argument("--port", type=int, required=True)
    p_deploy.add_argument("--domain", required=True)

    # snapshot
    p_snap = subparsers.add_parser("snapshot", help="Manage Btrfs/Snapper snapshots")
    sub_snap = p_snap.add_subparsers(dest="snap_action")
    p_snap_create = sub_snap.add_parser("create", help="Create new snapshot")
    p_snap_create.add_argument("--desc", help="Snapshot description")
    sub_snap.add_parser("list", help="List all snapshots")

    # rollback
    subparsers.add_parser("rollback", help="Trigger rollback to previous verified snapshot")

    # backup
    p_backup = subparsers.add_parser("backup", help="Manage encrypted backups and DR drills")
    sub_backup = p_backup.add_subparsers(dest="backup_action")
    sub_backup.add_parser("run", help="Trigger deduplicated encrypted backup")
    sub_backup.add_parser("dr-drill", help="Execute sandbox disaster recovery test")

    # audit
    p_audit = subparsers.add_parser("audit", help="Audit ledger and CERT-In compliance")
    sub_audit = p_audit.add_subparsers(dest="audit_action")
    sub_audit.add_parser("verify", help="Verify cryptographic hash-chain integrity")
    sub_audit.add_parser("cert-in", help="Export CERT-In compliant audit dossier")

    # support bundle
    subparsers.add_parser("support-bundle", help="Generate signed diagnostics and support archive")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args)
    elif args.command == "apps":
        cmd_apps(args)
    elif args.command == "snapshot":
        cmd_snapshot(args)
    elif args.command == "rollback":
        cmd_rollback(args)
    elif args.command == "backup":
        cmd_backup(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "support-bundle":
        cmd_bundle(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
