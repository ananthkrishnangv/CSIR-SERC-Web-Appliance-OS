"""
CSIR Secure Web Appliance OS (CSIR-SWA OS)
Comprehensive Presentation Deck Generator (HTML5, PDF, PPTX)

Features:
- Glassmorphism UI styling inspired by modern SaaS operations dashboards.
- Montserrat font for headings, Noto Sans for UI and body text.
- Comprehensive feature coverage: Native Web Hosting, Virtual Host Management,
  Reverse Proxy & Upstream Pools, SSL/TLS Key Vault, Podman Quadlets,
  Coraza WAF, Local AI Security Center, Data Protection, CERT-In Audit Ledger.
- Individual dedicated slides for EVERY qualification screenshot (Single screenshot per page).
"""

import os
import sys
import zipfile
import html
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
ASSETS_DIR = BASE_DIR / "installer" / "assets" / "branding"
ISO_BUILDER_DIR = BASE_DIR / "iso-builder"
SCREENSHOTS_DIR = DOCS_DIR / "screenshots" / "web_console"

OUTPUT_PPTX = DOCS_DIR / "CSIR-SWA-OS-Product-Features-and-Deployment.pptx"
OUTPUT_HTML = DOCS_DIR / "CSIR-SWA-OS-Product-Features-and-Deployment.html"
OUTPUT_PDF = DOCS_DIR / "CSIR-SWA-OS-Product-Features-and-Deployment-Slides.pdf"

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not Path(EDGE_PATH).exists():
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def xml_escape(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

# ==============================================================================
# 1. PPTX BUILDER (ECMA-376 OpenXML Standards)
# ==============================================================================

class PPTXBuilder:
    def __init__(self, filename: Path):
        self.filename = filename
        self.slides = []
        self.media_files = {}

    def add_media(self, file_path: Path) -> str:
        file_path = Path(file_path)
        if not file_path.exists():
            return ""
        name = file_path.name
        if name not in self.media_files:
            self.media_files[name] = file_path
        return name

    def add_slide(self, bg_color: str, title: str, category: str, elements: list):
        self.slides.append({
            "bg_color": bg_color,
            "title": title,
            "category": category,
            "elements": elements
        })

    def build_slide_xml(self, slide_idx: int, slide_data: dict) -> tuple:
        bg = slide_data.get("bg_color", "FFFFFF")
        title = slide_data.get("title", "")
        category = slide_data.get("category", "")
        elements = slide_data.get("elements", [])

        shapes_xml = []
        rels_xml = []
        shape_id = 2
        rel_id = 1

        # Background shape
        shapes_xml.append(f"""
        <p:sp>
          <p:nvSpPr>
            <p:cNvPr id="{shape_id}" name="Background"/>
            <p:cNvSpPr/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm>
              <a:off x="0" y="0"/>
              <a:ext cx="12192000" cy="6858000"/>
            </a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            <a:solidFill><a:srgbClr val="{bg}"/></a:solidFill>
          </p:spPr>
        </p:sp>
        """)
        shape_id += 1

        # Header Title and Category if present
        if title:
            is_dark = (bg in ["071321", "0B132B", "0F172A"])
            cat_color = "38BDF8" if is_dark else "0284C7"
            title_color = "F8FAFC" if is_dark else "0F172A"

            shapes_xml.append(f"""
            <p:sp>
              <p:nvSpPr>
                <p:cNvPr id="{shape_id}" name="SlideHeader"/>
                <p:cNvSpPr/>
                <p:nvPr/>
              </p:nvSpPr>
              <p:spPr>
                <a:xfrm>
                  <a:off x="731520" y="457200"/>
                  <a:ext cx="10725120" cy="1005840"/>
                </a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                <a:noFill/>
              </p:spPr>
              <p:txBody>
                <a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0"/>
                <a:p>
                  <a:r>
                    <a:rPr lang="en-US" sz="1100" b="1">
                      <a:solidFill><a:srgbClr val="{cat_color}"/></a:solidFill>
                      <a:latin typeface="Montserrat"/>
                    </a:rPr>
                    <a:t>{xml_escape(category.upper())}</a:t>
                  </a:r>
                </a:p>
                <a:p>
                  <a:r>
                    <a:rPr lang="en-US" sz="2200" b="1">
                      <a:solidFill><a:srgbClr val="{title_color}"/></a:solidFill>
                      <a:latin typeface="Montserrat"/>
                    </a:rPr>
                    <a:t>{xml_escape(title)}</a:t>
                  </a:r>
                </a:p>
              </p:txBody>
            </p:sp>
            """)
            shape_id += 1

        # Render elements
        for el in elements:
            el_type = el.get("type", "card")
            x = el.get("x", 731520)
            y = el.get("y", 1828800)
            cx = el.get("cx", 5166360)
            cy = el.get("cy", 4389120)

            if el_type == "card":
                card_bg = el.get("bg", "FFFFFF")
                card_border = el.get("border", "CBD5E1")
                card_title = el.get("title", "")
                card_title_color = el.get("title_color", "0F172A")
                bullets = el.get("bullets", [])

                p_tags = []
                if card_title:
                    p_tags.append(f"""
                    <a:p>
                      <a:r>
                        <a:rPr lang="en-US" sz="1400" b="1">
                          <a:solidFill><a:srgbClr val="{card_title_color}"/></a:solidFill>
                          <a:latin typeface="Montserrat"/>
                        </a:rPr>
                        <a:t>{xml_escape(card_title)}</a:t>
                      </a:r>
                    </a:p>
                    """)

                for b in bullets:
                    p_tags.append(f"""
                    <a:p>
                      <a:pPr marL="288000" indent="-288000">
                        <a:buFont typeface="Arial"/>
                        <a:buChar char="â€¢"/>
                      </a:pPr>
                      <a:r>
                        <a:rPr lang="en-US" sz="1100">
                          <a:solidFill><a:srgbClr val="334155"/></a:solidFill>
                          <a:latin typeface="Noto Sans"/>
                        </a:rPr>
                        <a:t>{xml_escape(b)}</a:t>
                      </a:r>
                    </a:p>
                    """)

                shapes_xml.append(f"""
                <p:sp>
                  <p:nvSpPr>
                    <p:cNvPr id="{shape_id}" name="CardBox"/>
                    <p:cNvSpPr/>
                    <p:nvPr/>
                  </p:nvSpPr>
                  <p:spPr>
                    <a:xfrm>
                      <a:off x="{x}" y="{y}"/>
                      <a:ext cx="{cx}" cy="{cy}"/>
                    </a:xfrm>
                    <a:prstGeom prst="roundRect">
                      <a:avLst><a:gd name="adj" fmla="val 2000"/></a:avLst>
                    </a:prstGeom>
                    <a:solidFill><a:srgbClr val="{card_bg}"/></a:solidFill>
                    <a:ln w="19050"><a:solidFill><a:srgbClr val="{card_border}"/></a:solidFill></a:ln>
                  </p:spPr>
                  <p:txBody>
                    <a:bodyPr lIns="200000" tIns="200000" rIns="200000" bIns="200000"/>
                    {''.join(p_tags)}
                  </p:txBody>
                </p:sp>
                """)
                shape_id += 1

            elif el_type == "image":
                m_name = el.get("media_name", "")
                if m_name and m_name in self.media_files:
                    rId = f"rId{rel_id}"
                    rel_id += 1
                    rels_xml.append(f'<Relationship Id="{rId}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{m_name}"/>')

                    shapes_xml.append(f"""
                    <p:pic>
                      <p:nvPicPr>
                        <p:cNvPr id="{shape_id}" name="{m_name}"/>
                        <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
                        <p:nvPr/>
                      </p:nvPicPr>
                      <p:blipFill>
                        <a:blip r:embed="{rId}"/>
                        <a:stretch><a:fillRect/></a:stretch>
                      </p:blipFill>
                      <p:spPr>
                        <a:xfrm>
                          <a:off x="{x}" y="{y}"/>
                          <a:ext cx="{cx}" cy="{cy}"/>
                        </a:xfrm>
                        <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 1500"/></a:avLst></a:prstGeom>
                        <a:ln w="25400"><a:solidFill><a:srgbClr val="0284C7"/></a:solidFill></a:ln>
                      </p:spPr>
                    </p:pic>
                    """)
                    shape_id += 1

        # Footer shape
        shapes_xml.append(f"""
        <p:sp>
          <p:nvSpPr>
            <p:cNvPr id="{shape_id}" name="Footer"/>
            <p:cNvSpPr/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm>
              <a:off x="731520" y="6350000"/>
              <a:ext cx="10725120" cy="300000"/>
            </a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            <a:noFill/>
          </p:spPr>
          <p:txBody>
            <a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0"/>
            <a:p>
              <a:r>
                <a:rPr lang="en-US" sz="900">
                  <a:solidFill><a:srgbClr val="64748B"/></a:solidFill>
                  <a:latin typeface="Noto Sans"/>
                </a:rPr>
                <a:t>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0 | Slide {slide_idx} of {len(self.slides)}</a:t>
              </a:r>
            </a:p>
          </p:txBody>
        </p:sp>
        """)

        slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {''.join(shapes_xml)}
    </p:spTree>
  </p:cSld>
</p:sld>"""

        rel_doc = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  {''.join(rels_xml)}
</Relationships>"""

        return slide_xml, rel_doc

    def save(self):
        with zipfile.ZipFile(self.filename, "w", zipfile.ZIP_DEFLATED) as z:
            # 1. Content Types
            ct_slides = [f'<Override PartName="/ppt/slides/slide{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(len(self.slides))]
            ct_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  {''.join(ct_slides)}
</Types>"""
            z.writestr("[Content_Types].xml", ct_xml)

            # 2. Package Rels
            pkg_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""
            z.writestr("_rels/.rels", pkg_rels)

            # 3. Presentation Rels & XML
            pres_rels_slides = [f'<Relationship Id="rIdSld{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>' for i in range(len(self.slides))]
            pres_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdMst1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {''.join(pres_rels_slides)}
</Relationships>"""
            z.writestr("ppt/_rels/presentation.xml.rels", pres_rels)

            sld_ids = [f'<p:sldId id="{256+i}" r:id="rIdSld{i+1}"/>' for i in range(len(self.slides))]
            pres_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMst1"/></p:sldMasterIdLst>
  <p:sldIdLst>{''.join(sld_ids)}</p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""
            z.writestr("ppt/presentation.xml", pres_xml)

            # 4. Slide Master & Layout Minimal
            master_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rIdLay1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""
            z.writestr("ppt/slideMasters/slideMaster1.xml", master_xml)
            master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdLay1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)

            layout_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:sldLayout>"""
            z.writestr("ppt/slideLayouts/slideLayout1.xml", layout_xml)
            layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdMst1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""
            z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)

            # 5. Media
            for m_name, m_path in self.media_files.items():
                with open(m_path, "rb") as mf:
                    z.writestr(f"ppt/media/{m_name}", mf.read())

            # 6. Slides
            for i, s_data in enumerate(self.slides):
                s_xml, s_rels = self.build_slide_xml(i+1, s_data)
                z.writestr(f"ppt/slides/slide{i+1}.xml", s_xml)
                z.writestr(f"ppt/slides/_rels/slide{i+1}.xml.rels", s_rels)

# ==============================================================================
# 2. DEFINITION OF ALL SLIDES (31 Comprehensive Widescreen Slides)
# ==============================================================================

def build_all_slides_data(builder: PPTXBuilder = None):
    # Register media in builder if given
    def reg(p):
        return builder.add_media(p) if builder else Path(p).name

    # Paths
    img_boot = reg(ISO_BUILDER_DIR / "vm_boot_menu_v2.jpg")
    img_yast = reg(ISO_BUILDER_DIR / "vm_step4_yast.jpg")
    img_net  = reg(ISO_BUILDER_DIR / "vm_step5_yast_net.jpg")
    img_part = reg(ISO_BUILDER_DIR / "vm_step8_partitioning.jpg")
    img_conf = reg(ISO_BUILDER_DIR / "vm_final_gui_proof_ready2.jpg")
    img_tty3 = reg(ISO_BUILDER_DIR / "vm_tty3_log.jpg")

    img_c_ov   = reg(SCREENSHOTS_DIR / "web_console_01_overview.png")
    img_c_vh   = reg(SCREENSHOTS_DIR / "web_console_02_vhosts.png")
    img_c_px   = reg(SCREENSHOTS_DIR / "web_console_03_proxy.png")
    img_c_ssl  = reg(SCREENSHOTS_DIR / "web_console_04_ssl.png")
    img_c_app  = reg(SCREENSHOTS_DIR / "web_console_05_applications.png")
    img_c_waf  = reg(SCREENSHOTS_DIR / "web_console_06_security_waf.png")
    img_c_ai   = reg(SCREENSHOTS_DIR / "web_console_07_ai_security_center.png")
    img_c_dr   = reg(SCREENSHOTS_DIR / "web_console_08_data_protection_backups.png")
    img_c_comp = reg(SCREENSHOTS_DIR / "web_console_09_compliance_audit_ledger.png")
    img_c_upd  = reg(SCREENSHOTS_DIR / "web_console_10_transactional_updates.png")
    img_c_term = reg(SCREENSHOTS_DIR / "web_console_11_boot_screen_console.png")

    slides = []

    # --------------------------------------------------------------------------
    # SLIDE 1: Title & Executive Introduction
    # --------------------------------------------------------------------------
    slides.append({
        "type": "title",
        "bg": "071321",
        "category": "SOVEREIGN GOVERNMENT CLOUD",
        "title": "CSIR Secure Web Appliance OS (CSIR-SWA OS)",
        "subtitle": "Next-Generation Hardened, Immutable, and Containerized Web Hosting Appliance",
        "bullets": [
            "Engineered for classified research laboratories, government web portals, and critical public infrastructure.",
            "Immutable openSUSE MicroOS transactional engine with zero-malware persistence.",
            "Integrated multi-tenant Web Hosting, Virtual Host Management, Reverse Proxy, and ACME SSL Key Vault."
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 2: Sovereign Mission Statement
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Strategic Imperatives",
        "title": "Institutional Objectives & Sovereign Control",
        "card1": {
            "title": "Challenges in Government Web Hosting",
            "bullets": [
                "Commercial Vendor Lock-in: Heavy recurring licensing costs for enterprise operating systems, commercial WAFs, and load balancers.",
                "High Vulnerability Surface: Standard mutable Linux distros allow unauthorized file tampering, backdoor persistence, and malware footholds.",
                "Compliance Bottlenecks: Complex CERT-In 6-hour incident disclosure rules require tedious manual log parsing."
            ]
        },
        "card2": {
            "title": "The CSIR-SWA OS Solution",
            "bullets": [
                "Zero Licensing Overhead: 100% open-source sovereign software stack saves millions in proprietary software budgets.",
                "Immutable System Integrity: Read-only Btrfs root (/) ensures that unauthorized changes cannot persist across reboots.",
                "One-Click CERT-In Compliance: Append-only SHA-256 cryptographic audit ledger guarantees 180-day retention and certified audit export."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 3: Architecture Overview
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Core Architecture",
        "title": "Layered Sovereign Defense Architecture",
        "card1": {
            "title": "System Foundation & Isolation",
            "bullets": [
                "Layer 1: Bare-Metal Hardware with TPM 2.0 cryptographic attestation.",
                "Layer 2: openSUSE MicroOS Immutable Core with Transactional Update engine.",
                "Layer 3: Btrfs subvolumes (@, @/var, @/srv) providing isolated atomic snapshots.",
                "Layer 4: Rootless Podman Quadlets running with dropped Linux capabilities."
            ]
        },
        "card2": {
            "title": "Edge Defense & Operations",
            "bullets": [
                "Layer 5: nftables default-deny ingress packet filtering and Indian NPL Stratum 1 NTP sync.",
                "Layer 6: Coraza Sovereign WAF with OWASP Core Rule Set (CRS 4.x) inspection.",
                "Layer 7: HAProxy L7 Dynamic Reverse Proxy & Virtual Host Management.",
                "Layer 8: Local AI Security Center providing zero-cloud threat correlation and ChatOps."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 4: Web Hosting & Virtual Host Architecture
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Native Web Hosting",
        "title": "Multi-Tenant Virtual Host & Web Serving Subsystem",
        "card1": {
            "title": "Comprehensive Virtual Host Features",
            "bullets": [
                "Multi-Tenant Isolation: Independent document roots allocated under /srv/www/vhosts/<domain>/.",
                "Multi-Runtime Support: Native execution pools for PHP 8.2-FPM, Node.js 20 SSR, Python ASGI (Uvicorn), and static web assets.",
                "High-Performance Protocols: Strict HTTP/2 and modern HTTP/3 (QUIC) multiplexing enabled by default.",
                "Quota & Resource Governance: Per-vhost storage quotas, bandwidth caps, and segregated access/error logs."
            ]
        },
        "card2": {
            "title": "Sovereign Web Serving Benefits",
            "bullets": [
                "Eliminates dependency on third-party commercial control panels (cPanel/Plesk).",
                "Full integration with systemd socket activation for on-demand worker spin-up.",
                "Automated subvolume snapshot binding per virtual host for instantaneous rollback.",
                "Direct inspection by Coraza WAF prior to reaching any web worker processes."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 5: Reverse Proxy & Upstream Pools
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Traffic Orchestration",
        "title": "Dynamic Reverse Proxy & Layer 7 Load Balancer",
        "card1": {
            "title": "Upstream Management & Algorithms",
            "bullets": [
                "HAProxy Sovereign Router: Sub-millisecond latency edge ingress and path-based routing.",
                "Dynamic Load Balancing: Round-Robin, Weighted Round-Robin, Least Connections, and IP-Hash session pinning.",
                "Granular Path Matching: Route rules such as /api/v1/* to API clusters and /ingest/* to high-rate sensor nodes.",
                "Deep Health Probing: Active HTTP/TCP health checks with configurable fail counters and automated failover."
            ]
        },
        "card2": {
            "title": "Operational Resilience & Scaling",
            "bullets": [
                "Circuit Breaker Engine: Automatically trips failing backends to prevent cascading cluster outages.",
                "Transparent Streaming: Native support for long-lived WebSockets, HTTP/2 Server Push, and gRPC channels.",
                "Header Security Injection: Automated enforcement of HSTS, CSP, X-Frame-Options, and Referrer-Policy.",
                "Zero Downtime Reloads: Graceful state transfer during upstream pool reconfiguration."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 6: SSL/TLS Key Vault & ACME
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Cryptographic Protection",
        "title": "Sovereign SSL/TLS Certificate Vault & Key Management",
        "card1": {
            "title": "Automated Certificate Lifecycle",
            "bullets": [
                "ACME Let's Encrypt Integration: Fully automated issuance and 30-day pre-expiry renewal via HTTP-01/DNS-01.",
                "Wildcard & Multi-SAN Support: Seamless deployment of *.serc.res.in and research domain certificates.",
                "Custom Sovereign Key Import: Secure vault for institutional certificates and HSM-backed private keys.",
                "CSR Generator: In-browser generation of RFC-compliant CSRs with SHA-384 / ECDSA secp384r1 curves."
            ]
        },
        "card2": {
            "title": "Hardened Cipher Suites & CERT-In Standards",
            "bullets": [
                "Strict TLS 1.3 Mandate: Deprecated protocols (TLS 1.0, 1.1, and legacy ciphers) are strictly disabled.",
                "OCSP Stapling: High-speed certificate revocation checking with zero DNS/privacy leakage.",
                "Tamper-Evident Key Vault: Encrypted storage with rootless access controls and TPM endorsement keys.",
                "Cryptographic Compliance: 100% compliant with Indian National Cyber Security Directives."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 7: Container Quadlets
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Workload Isolation",
        "title": "Rootless Podman Quadlets & Systemd Integration",
        "card1": {
            "title": "Daemonless System Architecture",
            "bullets": [
                "Systemd-Native Quadlets: Workloads defined as declarative .container and .network systemd unit files.",
                "Rootless Security: Containers execute entirely inside unprivileged user namespaces (UserNS).",
                "Dropped Capabilities: High-risk Linux privileges (CAP_SYS_ADMIN, CAP_NET_ADMIN) dropped by default.",
                "Read-Only Root Filesystems: Container roots are mounted read-only, preventing runtime infection."
            ]
        },
        "card2": {
            "title": "Cryptographic Image Provenance",
            "bullets": [
                "Cosign Digital Signatures: Only images signed by trusted CSIR institutional keys are permitted to boot.",
                "Digest Pinning: All container images are strictly bound by immutable SHA-256 digests.",
                "SBOM Validation: Automated validation of Software Bill of Materials against CVE databases.",
                "Hard Resource Quotas: Deterministic CPU, RAM, and I/O limits prevent noisy-neighbor starvation."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 8: Coraza WAF & Sovereign Defense
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Perimeter Defense",
        "title": "Coraza Sovereign WAF & nftables Network Shield",
        "card1": {
            "title": "Real-Time Threat Neutralization",
            "bullets": [
                "OWASP Core Rule Set (CRS 4.x): Deep packet inspection for SQL Injection, XSS, Remote Code Execution, and LFI.",
                "Zero False-Positive Engine: Dynamic anomaly scoring with adjustable paranoia levels (PL1 &ndash; PL4).",
                "Ingress Rate Limiting: High-frequency token bucket limiting prevents brute-force credential stuffing.",
                "Bot & Scanner Neutralization: Automated drop policies for illicit vulnerability scanners and crawlers."
            ]
        },
        "card2": {
            "title": "Automated Threat Escalation",
            "bullets": [
                "nftables Integration: WAF block events immediately escalate offensive subnets into kernel packet drop sets.",
                "24-Hour Adaptive Isolation: Repeat offenders quarantined without incurring user-space CPU overhead.",
                "Complete Sovereign Telemetry: Full visibility into rule triggers, target endpoints, and payload decodes.",
                "Zero Third-Party Data Leakage: All inspection is 100% on-premises without external telemetry phone-home."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 9: Local AI Security Center
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Autonomous Operations",
        "title": "Local AI Security & Operations Center (Zero Cloud)",
        "card1": {
            "title": "Autonomous Threat Narrative Synthesis",
            "bullets": [
                "Air-Gapped Local LLM: Security telemetry analyzed locally without transmitting data to external clouds.",
                "Plain-English Threat Narratives: Converts thousands of raw WAF logs into clear executive incident briefings.",
                "Root Cause Analysis (RCA): Autonomous diagnostics pinpoint application database bottlenecks and query contention.",
                "Capacity Telemetry: Proactive forecasting of storage subvolume consumption and compute spikes."
            ]
        },
        "card2": {
            "title": "Sovereign Human Governance Gate",
            "bullets": [
                "Strict Advisory Role: AI can propose remediation actions but can NEVER autonomously execute high-impact commands.",
                "Human Authorization Barrier: Critical patches, firewall modifications, and rollbacks require verified admin sign-off.",
                "Integrated ChatOps Assistant: Natural-language command interface for telemetry querying and maintenance staging.",
                "Immutable Audit Trail: All AI recommendations and human decisions are permanently recorded in the SHA-256 ledger."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 10: Data Protection & Backups
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Business Continuity",
        "title": "Data Protection, Btrfs Snapshots & DR Drills",
        "card1": {
            "title": "Subvolume Tree Protection",
            "bullets": [
                "Copy-on-Write Snapshots: Zero-overhead instantaneous Btrfs snapshots across @, @/var, and @/srv.",
                "Automated Snapper Timeline: Hourly, daily, and pre-update snapshots retained according to policy.",
                "Encrypted Restic Repositories: Off-site, deduplicated, and cryptographically encrypted secondary backups.",
                "Ransomware Immunity: Read-only snapshot trees prevent crypto-locker manipulation or deletion."
            ]
        },
        "card2": {
            "title": "Automated DR Verification Drills",
            "bullets": [
                "Scheduled Sandbox Drills: Automated recovery verification tests executed in isolated network namespaces.",
                "Verified RTO & RPO: Exact measurement of Recovery Time Objective (12s &ndash; 23s) and Recovery Point Objective.",
                "Cryptographic Integrity Checks: Full SHA-256 verification of restored database tables and application datasets.",
                "Audit-Ready Certification: Automated generation of DR readiness scorecards for audit inspections."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 11: CERT-In Compliance
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Regulatory Compliance",
        "title": "CERT-In Section 70B Cryptographic Audit Ledger",
        "card1": {
            "title": "Regulatory Mandate Compliance",
            "bullets": [
                "Mandatory 180-Day Retention: Immutable system logs locked against premature truncation or alteration.",
                "Directions under Section 70B: Comprehensive tracking of cybersecurity incidents, system changes, and access attempts.",
                "Indian NPL Stratum 1 Clock Sync: Strict microsecond clock discipline synchronized directly to National Physical Laboratory Delhi.",
                "Cryptographic Hash Chaining: Every audit record contains SHA256(prev_hash | payload_hash | timestamp | actor)."
            ]
        },
        "card2": {
            "title": "Rapid Incident Disclosure",
            "bullets": [
                "6-Hour Statutory Window: One-click export of certified incident dossiers formatted for CERT-In reporting.",
                "Tamper-Evident Ledger: Mathematical verification detects any row alteration, sequence omission, or DB manipulation.",
                "Chain of Custody Assurance: Forensically sound log bundles admissible for government and legal compliance.",
                "Automated Dossier Generation: Eliminates manual evidence gathering during critical incident response windows."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 12: Transactional Updates
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Platform Lifecycle",
        "title": "openSUSE MicroOS Transactional Updates",
        "card1": {
            "title": "Atomic Staging & Zero Risk",
            "bullets": [
                "Transactional Update Engine: OS patches and kernel updates install into a fresh, isolated Btrfs snapshot.",
                "Zero Runtime Interruption: Active running system remains 100% read-only and unaffected during package downloads.",
                "Clean Atomic Switchover: New snapshot becomes active only after a successful reboot into the target snapshot.",
                "Eliminates Inconsistent States: Broken package installations or aborted upgrades can never corrupt the running node."
            ]
        },
        "card2": {
            "title": "Automated Health-Gated Rollback",
            "bullets": [
                "Systemd Health Probes: Automated verification of network interfaces, web servers, and WAF services post-boot.",
                "Automatic Fallback: If health checks fail post-boot, the system immediately reboots into the known-good snapshot.",
                "One-Click Manual Rollback: Administrative console allows immediate reversion to previous system states.",
                "100% Uptime Confidence: Critical security patches can be applied with absolute operational assurance."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 13: Multi-Mode Deployment Architecture
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F8FAFC",
        "category": "Deployment Modalities",
        "title": "Turn-Key Sovereign Deployment Modalities",
        "card1": {
            "title": "Monolithic Offline DVD ISO",
            "bullets": [
                "Production Release: csir-swa-os-1.0.0-fullstack-x86_64.iso (2.73 GB).",
                "Zero Internet Required: All RPM packages, container images, WAF rules, and web assets bundled offline.",
                "Combustion & AutoYaST: Fully automated bare-metal and hypervisor provisioning in under 4 minutes.",
                "Dual Boot Support: Complete compatibility with UEFI Secure Boot and legacy BIOS hardware."
            ]
        },
        "card2": {
            "title": "Online Bootstrap & MicroOS Converter",
            "bullets": [
                "Universal Online Remote Bootstrap: Simple one-liner deployment: curl -sSL .../install.sh | sudo bash.",
                "Dedicated MicroOS Converter: installer/convert-microos.sh transforms standard MicroOS into CSIR appliance.",
                "Air-Gapped Facility Hardening: Pre-configured offline RPM repositories and local container caches.",
                "VirtualBox & Hyper-V Ready: Turn-key scripts for immediate testbed qualification and evaluation."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # DEDICATED VISUAL QUALIFICATION GALLERY (SINGLE SCREENSHOT PER SLIDE)
    # --------------------------------------------------------------------------

    # SLIDE 14: Figure 1 - GRUB2 Boot Menu
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Installation",
        "title": "Figure 1: Official CSIR-SERC High-Resolution GRUB2 Boot Menu",
        "image_file": img_boot,
        "caption": "Figure 1: Official CSIR-SERC GRUB2 Bootloader with Graphical Easy Installer & Automated Express Installation entries.",
        "specs": [
            "Resolution: 1024x768 TrueColor graphical frame-buffer.",
            "CSIR-SERC Official Institutional Seal and branding embedded.",
            "Menu Options: Automated Express Install, Easy Interactive Install, RAM Test, Hardware Probing.",
            "Dual-Architecture: Native UEFI Secure Boot (x86_64-efi) and Legacy BIOS MBR support."
        ]
    })

    # SLIDE 15: Figure 2 - YaST Initialization
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Installation",
        "title": "Figure 2: Graphical YaST Installer Engine Initialization",
        "image_file": img_yast,
        "caption": "Figure 2: Graphical YaST Installer Engine Initialization & Combustion Automation Hooks.",
        "specs": [
            "Combustion Subsystem: Automated execution of first-boot configuration scripts.",
            "Memory Optimization: Automatic detection of hardware RAM (&ge; 4096 MB for full GUI mode).",
            "Hardened Defaults: Pre-selected transactional MicroOS server profile with zero bloatware.",
            "Cryptographic Verification: All installer packages verified against CSIR GPG Release Key."
        ]
    })

    # SLIDE 16: Figure 3 - Network Discovery
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Installation",
        "title": "Figure 3: Automated Network Discovery & Addressing",
        "image_file": img_net,
        "caption": "Figure 3: Automated Network Interface Discovery & Indian NPL NTP Server Configuration.",
        "specs": [
            "Hardware Probing: Deterministic identification of 10G/1G physical Ethernet and virtual interfaces.",
            "Dual-Stack Support: IPv4 and IPv6 automatic address acquisition with static override capability.",
            "Indian Sovereign Time Sync: Chrony configured directly for Indian NPL Stratum 1 NTP servers.",
            "Default-Deny Ingress: Ingress firewall rules activated prior to network link state transition."
        ]
    })

    # SLIDE 17: Figure 4 - Btrfs Partitioning
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Installation",
        "title": "Figure 4: Immutable Btrfs Subvolume Layout (@, @/var, @/srv)",
        "image_file": img_part,
        "caption": "Figure 4: Immutable Btrfs Subvolume Partitioning Scheme with Granular Subvolume Separation.",
        "specs": [
            "Root Subvolume (@): Mounted strictly read-only (ro) to ensure complete malware immunity.",
            "Data Subvolume (@/srv): Segregated read-write subvolume for virtual hosts, web roots, and containers.",
            "Logging Subvolume (@/var): Dedicated subvolume for CERT-In 180-day append-only audit ledgers.",
            "Snapshot Hierarchy: Granular Snapper policies preventing logs from inflating system backups."
        ]
    })

    # SLIDE 18: Figure 5 - Installation Confirmation
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Installation",
        "title": "Figure 5: Automated Installation Confirmation & Payload Verification",
        "image_file": img_conf,
        "caption": "Figure 5: YaST Final Automated Installation Confirmation with Full CSIR Sovereign Feature Payload.",
        "specs": [
            "Package Validation: Complete installation of Coraza WAF, HAProxy, Podman, and UX4G Console.",
            "Target Hardening: Disabling of non-essential services, root password hashing (SHA-512 crypt).",
            "Storage Commitment: Atomic Btrfs formatting and snapshot tree baseline generation.",
            "Bootloader Installation: Signed GRUB2 binary committed to EFI System Partition (ESP)."
        ]
    })

    # SLIDE 19: Figure 6 - TTY3 Diagnostic Console
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Installation",
        "title": "Figure 6: Diagnostic Linuxrc Installation Console & TTY3 Shell",
        "image_file": img_tty3,
        "caption": "Figure 6: TTY3 Real-Time Linuxrc Installation Log & Storage Mounting Diagnostics.",
        "specs": [
            "Real-Time Kernel Telemetry: Direct monitoring of driver probing and storage initialization.",
            "Storage Attachment: SATA/NVMe controller discovery and LUKS container initialization.",
            "Diagnostic Access: Unprivileged audit shell accessible via Ctrl+Alt+F3 during deployment.",
            "Fail-Safe Recovery: Immediate logging of any disk or memory probing bottlenecks."
        ]
    })

    # SLIDE 20: Figure 7 - Web Console Overview
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 7: UX4G Central Health & Operations Overview Dashboard",
        "image_file": img_c_ov,
        "caption": "Figure 7: Modern Glassmorphic Operations & Health Dashboard with 4 Trend Metrics, Workloads & Smart Alerts.",
        "specs": [
            "Executive Health KPI: 98.4% cluster operational health score across 24 microservices.",
            "Real-Time Ingress Telemetry: 1,842 req/s proxy throughput with sub-10ms p95 response time.",
            "Coraza Threat Shield: 1,429 attacks blocked with 100% drop rate and zero false positives.",
            "Smart Alerts & ChatOps: Integrated timeline alerts and interactive sovereign AI assistant."
        ]
    })

    # SLIDE 21: Figure 8 - Web Hosting & Virtual Hosts
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 8: Native Web Hosting & Multi-Tenant Virtual Host Management",
        "image_file": img_c_vh,
        "caption": "Figure 8: Native Virtual Host Management with PHP/Node/Static Runtimes, Document Roots & Quota Bars.",
        "specs": [
            "Active Domains: Complete management of serc.res.in, wind.serc.res.in, sensors.serc.res.in.",
            "Document Root Security: Enforced path mapping under /srv/www/vhosts with strict file permissions.",
            "Multi-Runtime Isolation: PHP 8.2-FPM, Node.js 20 SSR, Python ASGI, and static caching runtimes.",
            "Resource Quota Tracking: Real-time visual tracking of disk consumption and bandwidth quotas."
        ]
    })

    # SLIDE 22: Figure 9 - Reverse Proxy & Upstreams
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 9: Dynamic Reverse Proxy & Upstream Load Balancer",
        "image_file": img_c_px,
        "caption": "Figure 9: HAProxy Sovereign Router with Upstream Server Pools, Route Paths, Latency & Health Checks.",
        "specs": [
            "Upstream Server Pools: Dedicated target pools for Structural Health, Wind Tunnel, and Local AI.",
            "Load Balancing Algorithms: Round-Robin, Least-Connections, and IP-Hash session pinning.",
            "Health Check Probes: Active HTTP ping checks every 3&ndash;10s with automatic circuit breaking.",
            "Edge Security Enforcements: Strict HTTP&rarr;HTTPS redirect, WebSocket passthrough, and DDoS rate limits."
        ]
    })

    # SLIDE 23: Figure 10 - SSL / TLS Key Vault
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 10: SSL / TLS Certificate Vault & ACME Key Management",
        "image_file": img_c_ssl,
        "caption": "Figure 10: Sovereign SSL/TLS Vault with ACME Auto-Renewal, ECDSA 384-bit Keys & OCSP Stapling.",
        "specs": [
            "Automated ACME Lifecycle: Automated renewal for *.serc.res.in 30 days prior to expiration.",
            "High-Grade Cryptography: ECDSA secp384r1 and RSA 4096-bit institutional private keys.",
            "Strict TLS 1.3 Standards: Hardened cipher suites with zero legacy fallback vulnerabilities.",
            "Sovereign CSR Tool: Integrated generator for certified government certificate signing requests."
        ]
    })

    # SLIDE 24: Figure 11 - Container Quadlets
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 11: Rootless Podman Quadlet Container Workloads",
        "image_file": img_c_app,
        "caption": "Figure 11: Rootless Podman Quadlet Workloads with Signed Image Digests & UserNS Isolation.",
        "specs": [
            "Cosign Verification: Cryptographic signature validation prior to workload execution.",
            "UserNS Rootless Isolation: Zero root privileges inside containers, mitigating breakout attacks.",
            "Hard Resource Allocations: Enforced memory quotas (256MB &ndash; 1024MB) and 50% CPU ceilings.",
            "Systemd Supervision: Automatic health monitoring and instant restart on worker exceptions."
        ]
    })

    # SLIDE 25: Figure 12 - Coraza Sovereign WAF
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 12: Coraza Sovereign WAF & nftables Network Defense",
        "image_file": img_c_waf,
        "caption": "Figure 12: Real-Time Coraza OWASP CRS Rule Toggles & Default-Deny nftables Firewall Policies.",
        "specs": [
            "OWASP CRS Toggles: Active enforcement of SQLi (942100), XSS (941100), RCE (932100), and LFI (930100).",
            "Paranoia Level 2: Strict inspection of administrative endpoints without disrupting legitimate users.",
            "nftables Kernel Filter: Default-deny ingress policies with whitelisted management ports.",
            "Zero External Telemetry: Complete on-premises inspection preserving institutional data confidentiality."
        ]
    })

    # SLIDE 26: Figure 13 - Local AI Security Center
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 13: Local AI Security Center & ChatOps Telemetry",
        "image_file": img_c_ai,
        "caption": "Figure 13: Local AI Security Center with Plain-English Incident Briefings & Governance Approval Gates.",
        "specs": [
            "Plain-English Briefings: Autonomous synthesis of coordinated scanner attempts (Narrative NAR-882).",
            "Human Sign-Off Gate: Mandatory human approval required before AI-suggested optimizations apply.",
            "Infrastructure RCA: Diagnostic identification of unindexed queries and PgBouncer pool sizing.",
            "Sovereign ChatOps: Interactive administrative query bar for natural language system management."
        ]
    })

    # SLIDE 27: Figure 14 - Data Protection & Backups
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 14: Data Protection, Btrfs Snapshots & Sandbox DR Restore Drills",
        "image_file": img_c_dr,
        "caption": "Figure 14: Snapper Btrfs Subvolume Trees, Restic Backup Runs & Automated Sandbox DR Verification Drills.",
        "specs": [
            "Subvolume Tree: Granular snapshot history across root (@), data (@/srv), and logs (@/var).",
            "Verified DR Drills: Measured RTO (12s &ndash; 23s) and RPO (15s &ndash; 45s) for critical portals.",
            "Cryptographic Hash Verification: Complete SHA-256 data verification ensuring zero post-restore corruption.",
            "Ransomware Protection: Immutable snapshot trees provide instant recovery against malicious encryption."
        ]
    })

    # SLIDE 28: Figure 15 - CERT-In Audit Ledger
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 15: CERT-In Section 70B Cryptographic SHA-256 Audit Ledger",
        "image_file": img_c_comp,
        "caption": "Figure 15: CERT-In Section 70B Tamper-Evident SHA-256 Audit Ledger with 180-Day Retention Lock.",
        "specs": [
            "Cryptographic Hash Chaining: SHA256(prev_hash | entry_hash) guarantees mathematical tamper-evidence.",
            "Direction 70B Adherence: Every state change, user action, and WAF modification recorded.",
            "Indian Sovereign Time Sync: Precise timestamping disciplined by Indian NPL Stratum 1 NTP servers.",
            "One-Click Dossier Export: Instant generation of certified incident packages for statutory disclosure."
        ]
    })

    # SLIDE 29: Figure 16 - Transactional Updates
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Web Console",
        "title": "Figure 16: Transactional Updates & Operating System Lifecycle",
        "image_file": img_c_upd,
        "caption": "Figure 16: MicroOS Transactional-Update Engine with Read-Only Root Snapshot #14 & Rollback Engine.",
        "specs": [
            "Read-Only Active Snapshot: Operating system executes from immutable snapshot #14.",
            "Atomic Update Staging: Package downloads apply to isolated staging snapshots without runtime disruption.",
            "Health-Gated Reversion: Automatic reboot rollback if post-boot health probes encounter degradation.",
            "One-Click Rollback: Immediate manual reversion button to restore baseline snapshots instantly."
        ]
    })

    # SLIDE 30: Figure 17 - Boot Screen Console
    slides.append({
        "type": "screenshot_page",
        "bg": "F8FAFC",
        "category": "Visual Qualification: Hardware Console",
        "title": "Figure 17: Bare-Metal Hardware & Diagnostic Terminal Console",
        "image_file": img_c_term,
        "caption": "Figure 17: Bare-Metal Hardware & Diagnostic Terminal Console Banner (Section 6 Specification).",
        "specs": [
            "ASCII Management Banner: Official CSIR-SERC console banner displayed upon hardware boot.",
            "Hardware Diagnostic Checklist: Validation of TPM 2.0, Secure Boot, encrypted disks, and NTP sync.",
            "Emergency Recovery Hotkeys: F2 for hardware console, F8 for emergency immutable snapshot recovery.",
            "Statutory Access Warning: Clear legal notice restricting access to authorized personnel only."
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 31: Institutional ROI & Deliverables
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "071321",
        "category": "Executive Conclusion",
        "title": "Institutional Impact & Production Deliverables",
        "card1": {
            "title": "Measurable Value & ROI",
            "bullets": [
                "Zero Software License Costs: 100% open-source software stack eliminates millions in commercial software fees.",
                "80% Attack Surface Elimination: Read-only Btrfs root, rootless Podman UserNS, and Coraza WAF neutralize common attack vectors.",
                "90% Faster CERT-In Reporting: Automated 6-hour dossier generation eliminates emergency compliance panic.",
                "Zero Downtime Maintenance: Atomic transactional updates guarantee that maintenance will never corrupt running nodes."
            ]
        },
        "card2": {
            "title": "Production Deliverables Catalog",
            "bullets": [
                "Offline DVD ISO: csir-swa-os-1.0.0-fullstack-x86_64.iso (2.73 GB).",
                "Online Bootstrap Launcher: curl -sSL .../install.sh | sudo bash.",
                "openSUSE MicroOS Converter: installer/convert-microos.sh.",
                "Full Technical Documentation PDF: docs/CSIR-SWA-OS-Complete-Documentation.pdf (27 Pages, 1.81 MB).",
                "Widescreen Slide Deck Suite: Native PPTX, Interactive HTML5 Deck, and Slide PDF Presentation.",
                "Council of Scientific and Industrial Research | CSIR-SERC Engineering Working Group."
            ]
        }
    })

    return slides

# ==============================================================================
# 3. INTERACTIVE HTML5 PRESENTATION DECK GENERATOR
# ==============================================================================

def generate_interactive_html(slides: list) -> str:
    total_slides = len(slides)
    slides_html = []

    for i, s in enumerate(slides):
        slide_num = i + 1
        s_type = s.get("type", "content_2col")
        bg = s.get("bg", "F8FAFC")
        category = s.get("category", "")
        title = s.get("title", "")
        is_dark = (bg in ["071321", "0B132B", "0F172A"])

        dark_class = "slide-dark" if is_dark else ""
        title_color = "#38bdf8" if is_dark else "#0f172a"
        cat_color = "#38bdf8" if is_dark else "#0284c7"

        content_html = ""

        if s_type == "title":
            subtitle = s.get("subtitle", "")
            bullets = s.get("bullets", [])
            bullets_li = "".join([f"<li class='flex items-start gap-3 text-slate-300 text-base'><span class='w-2 h-2 rounded-full bg-sky-400 mt-2 shrink-0'></span><span>{b}</span></li>" for b in bullets])

            content_html = f"""
            <div class="h-full flex flex-col justify-between p-12">
                <div>
                    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-sky-950/80 border border-sky-500/40 text-sky-400 font-heading font-extrabold text-xs uppercase tracking-widest mb-6">
                        <i class="fa-solid fa-shield-halved"></i> {category}
                    </div>
                    <h1 class="font-heading font-extrabold text-4xl sm:text-5xl text-white tracking-tight leading-tight max-w-4xl">
                        {title}
                    </h1>
                    <p class="font-heading font-medium text-xl text-sky-300/90 mt-4 max-w-3xl leading-relaxed">
                        {subtitle}
                    </p>
                </div>

                <div class="glass-card-dark rounded-2xl p-8 border border-sky-500/30 max-w-4xl my-6">
                    <div class="text-xs font-heading font-bold text-sky-400 uppercase tracking-wider mb-4">Core Architectural Mandate</div>
                    <ul class="space-y-3">
                        {bullets_li}
                    </ul>
                </div>

                <div class="flex items-center justify-between text-xs font-mono text-slate-400 border-t border-slate-800 pt-4">
                    <span>Council of Scientific &amp; Industrial Research (CSIR-SERC)</span>
                    <span>Version 1.0.0 Stable Channel</span>
                </div>
            </div>
            """

        elif s_type == "content_2col":
            c1 = s.get("card1", {})
            c2 = s.get("card2", {})

            b1_li = "".join([f"<li class='text-sm text-slate-600 leading-relaxed'><strong class='text-slate-900'>{b.split(':')[0]}:</strong>{b.split(':', 1)[1] if ':' in b else ''}</li>" for b in c1.get("bullets", [])])
            b2_li = "".join([f"<li class='text-sm text-slate-600 leading-relaxed'><strong class='text-slate-900'>{b.split(':')[0]}:</strong>{b.split(':', 1)[1] if ':' in b else ''}</li>" for b in c2.get("bullets", [])])

            content_html = f"""
            <div class="h-full flex flex-col justify-between p-10">
                <div class="slide-header">
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 text-sky-700 border border-sky-200 text-xs font-heading font-extrabold uppercase tracking-wider mb-2">
                        {category}
                    </div>
                    <h2 class="font-heading font-extrabold text-2xl sm:text-3xl text-slate-900 tracking-tight">
                        {title}
                    </h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 my-auto">
                    <div class="glass-card rounded-2xl p-7 border-l-4 border-l-sky-600 flex flex-col justify-between">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-slate-900 mb-4">{c1.get('title', '')}</h3>
                            <ul class="space-y-3.5 list-disc list-inside">
                                {b1_li}
                            </ul>
                        </div>
                    </div>
                    <div class="glass-card rounded-2xl p-7 border-l-4 border-l-emerald-600 flex flex-col justify-between">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-slate-900 mb-4">{c2.get('title', '')}</h3>
                            <ul class="space-y-3.5 list-disc list-inside">
                                {b2_li}
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-400 border-t border-slate-200 pt-3">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0</span>
                    <span class="font-mono">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "screenshot_page":
            img_file = s.get("image_file", "")
            caption = s.get("caption", "")
            specs = s.get("specs", [])
            specs_li = "".join([f"<li class='text-xs text-slate-600 leading-relaxed'><i class='fa-solid fa-check text-emerald-500 mr-2'></i>{sp}</li>" for sp in specs])

            # Relative path from docs/
            if "screenshots" in str(img_file) or "web_console" in str(img_file):
                rel_img_src = f"screenshots/web_console/{Path(img_file).name}"
            else:
                rel_img_src = f"../iso-builder/{Path(img_file).name}"

            content_html = f"""
            <div class="h-full flex flex-col justify-between p-8">
                <!-- Header -->
                <div class="slide-header flex items-center justify-between">
                    <div>
                        <div class="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-sky-50 text-sky-700 border border-sky-200 text-[11px] font-heading font-extrabold uppercase tracking-wider">
                            <i class="fa-solid fa-camera"></i> {category}
                        </div>
                        <h2 class="font-heading font-extrabold text-xl sm:text-2xl text-slate-900 tracking-tight mt-1">
                            {title}
                        </h2>
                    </div>
                    <span class="badge badge-sm badge-outline border-slate-300 font-mono text-slate-500">Dedicated Verification Slide</span>
                </div>

                <!-- 2-Column Showcase Layout (Left 32% Specs, Right 68% Full-Size Screenshot) -->
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 my-auto items-center">
                    
                    <!-- Left Spec Card (4 columns) -->
                    <div class="lg:col-span-4 glass-card rounded-2xl p-6 border-l-4 border-l-sky-600 space-y-4">
                        <div class="flex items-center gap-2 font-heading font-bold text-slate-900 text-sm">
                            <i class="fa-solid fa-list-check text-sky-600"></i>
                            <span>Technical Verification Specifications</span>
                        </div>
                        <ul class="space-y-3">
                            {specs_li}
                        </ul>
                        <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-500">
                            <strong>Qualification Protocol:</strong> Certified on bare-metal HP Pro Tower &amp; VirtualBox 7.x testbed.
                        </div>
                    </div>

                    <!-- Right Screenshot View (8 columns) -->
                    <div class="lg:col-span-8 flex flex-col items-center">
                        <div class="w-full glass-card p-2 rounded-2xl border border-sky-200/60 shadow-xl overflow-hidden bg-slate-900/5">
                            <img src="{rel_img_src}" alt="{title}" class="w-full rounded-xl object-contain max-h-[64vh] shadow-sm">
                        </div>
                        <div class="text-[11px] text-slate-500 font-medium text-center mt-2">
                            {caption}
                        </div>
                    </div>

                </div>

                <!-- Footer -->
                <div class="flex items-center justify-between text-xs text-slate-400 border-t border-slate-200 pt-2.5">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0 | Proof of Verification</span>
                    <span class="font-mono font-semibold text-slate-600">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        slides_html.append(f"""
        <section class="slide {dark_class}" id="slide-{slide_num}" style="background-color: #{bg};">
            {content_html}
        </section>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSIR Secure Web Appliance OS - Product Presentation &amp; Features</title>

<!-- Google Fonts: Montserrat for Headings, Noto Sans for UI and Body -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Tailwind & daisyUI -->
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css" rel="stylesheet" type="text/css" />

<style>
    @page {{
        size: A4 landscape;
        margin: 0;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
        font-family: 'Noto Sans', sans-serif;
        background: #0f172a;
        color: #0f172a;
        overflow-x: hidden;
    }}

    h1, h2, h3, h4, h5, h6, .font-heading {{
        font-family: 'Montserrat', sans-serif;
        letter-spacing: -0.02em;
    }}

    .slide {{
        width: 297mm;
        height: 210mm;
        margin: 0 auto;
        page-break-after: always;
        position: relative;
        overflow: hidden;
        background: #f8fafc;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }}

    @media screen {{
        body {{
            padding: 20px 0;
            background: #090d16;
        }}
        .slide {{
            margin-bottom: 30px;
            border-radius: 12px;
        }}
    }}

    .slide-dark {{
        background: #071321 !important;
        color: #f8fafc !important;
    }}

    /* Glassmorphism Classes */
    .glass-card {{
        background: rgba(255, 255, 255, 0.82);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.85);
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
    }}

    .glass-card-dark {{
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(56, 189, 248, 0.25);
    }}

    /* Sticky Presentation Controls */
    .deck-controls {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(12px);
        padding: 8px 16px;
        border-radius: 9999px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
</style>
</head>
<body>

<div id="deck">
    {''.join(slides_html)}
</div>

<!-- Floating Presentation Controls for Screen View -->
<div class="deck-controls hidden sm:flex">
    <button onclick="prevSlide()" class="btn btn-circle btn-xs btn-ghost text-white"><i class="fa-solid fa-chevron-left"></i></button>
    <span id="slideCounter" class="text-xs font-mono font-bold text-sky-400">1 / {total_slides}</span>
    <button onclick="nextSlide()" class="btn btn-circle btn-xs btn-ghost text-white"><i class="fa-solid fa-chevron-right"></i></button>
    <button onclick="window.print()" class="btn btn-xs btn-primary bg-sky-600 border-none rounded-full text-white ml-2"><i class="fa-solid fa-print"></i> PDF Export</button>
</div>

<script>
    let currentSlide = 1;
    const totalSlides = {total_slides};

    function updateCounter() {{
        const counter = document.getElementById('slideCounter');
        if (counter) counter.innerText = `${{currentSlide}} / ${{totalSlides}}`;
    }}

    function goToSlide(n) {{
        if (n < 1) n = 1;
        if (n > totalSlides) n = totalSlides;
        currentSlide = n;
        const target = document.getElementById(`slide-${{currentSlide}}`);
        if (target) {{
            target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
        updateCounter();
    }}

    function nextSlide() {{ goToSlide(currentSlide + 1); }}
    function prevSlide() {{ goToSlide(currentSlide - 1); }}

    window.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
            e.preventDefault();
            nextSlide();
        }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
            e.preventDefault();
            prevSlide();
        }} else if (e.key === 'Home') {{
            goToSlide(1);
        }} else if (e.key === 'End') {{
            goToSlide(totalSlides);
        }}
    }});
</script>

</body>
</html>"""
    return full_html

# ==============================================================================
# 4. MAIN BUILDER FUNCTION
# ==============================================================================

def main():
    print("=" * 70)
    print(" CSIR Secure Web Appliance OS - Product Presentation & PDF Suite")
    print(" Enhanced with Web Hosting, VHosts, Reverse Proxy, and SSL Vault")
    print(" Single Dedicated Screenshot per Slide Layout")
    print("=" * 70)

    # 1. Build PPTX
    print("\n[*] Initializing PPTX Builder...")
    pptx_builder = PPTXBuilder(OUTPUT_PPTX)
    slides_data = build_all_slides_data(pptx_builder)

    for i, s in enumerate(slides_data):
        s_type = s.get("type", "content_2col")
        bg = s.get("bg", "FFFFFF")
        cat = s.get("category", "")
        title = s.get("title", "")

        elements = []
        if s_type == "title":
            elements.append({
                "type": "card",
                "x": 731520, "y": 1400000, "cx": 10725120, "cy": 4500000,
                "bg": "0F172A", "border": "0284C7",
                "title": s.get("title", ""),
                "title_color": "38BDF8",
                "bullets": [s.get("subtitle", "")] + s.get("bullets", [])
            })
        elif s_type == "content_2col":
            c1 = s.get("card1", {})
            c2 = s.get("card2", {})
            elements.append({
                "type": "card",
                "x": 731520, "y": 1828800, "cx": 5166360, "cy": 4389120,
                "bg": "FFFFFF", "border": "0284C7",
                "title": c1.get("title", ""),
                "title_color": "0284C7",
                "bullets": c1.get("bullets", [])
            })
            elements.append({
                "type": "card",
                "x": 6294120, "y": 1828800, "cx": 5166360, "cy": 4389120,
                "bg": "FFFFFF", "border": "10B981",
                "title": c2.get("title", ""),
                "title_color": "10B981",
                "bullets": c2.get("bullets", [])
            })
        elif s_type == "screenshot_page":
            m_name = Path(s.get("image_file", "")).name
            specs = s.get("specs", [])
            # Left Specs Card
            elements.append({
                "type": "card",
                "x": 731520, "y": 1828800, "cx": 3800000, "cy": 4389120,
                "bg": "FFFFFF", "border": "0284C7",
                "title": "Technical Specifications",
                "title_color": "0284C7",
                "bullets": specs
            })
            # Right Full Screenshot
            elements.append({
                "type": "image",
                "x": 4800000, "y": 1828800, "cx": 6600000, "cy": 4389120,
                "media_name": m_name
            })

        pptx_builder.add_slide(bg_color=bg, title=title, category=cat, elements=elements)

    print(f"[*] Saving Native PPTX to: {OUTPUT_PPTX} ({len(slides_data)} slides)...")
    pptx_builder.save()
    print(f"[OK] PPTX Saved: {OUTPUT_PPTX.stat().st_size:,} bytes")

    # 2. Build Interactive HTML5 Presentation Deck
    print(f"\n[*] Generating Interactive 16:9 HTML5 Presentation Deck: {OUTPUT_HTML}...")
    html_content = generate_interactive_html(slides_data)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] HTML5 Deck Saved: {OUTPUT_HTML.stat().st_size:,} bytes")

    # 3. Render Slide PDF Presentation via Headless Edge
    print(f"\n[*] Rendering Slide PDF Presentation via Microsoft Edge...")
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={str(OUTPUT_PDF)}",
        str(OUTPUT_HTML)
    ]
    subprocess.run(cmd, check=True)
    if OUTPUT_PDF.exists():
        print(f"[OK] Slide PDF Generated: {OUTPUT_PDF.stat().st_size:,} bytes ({len(slides_data)} landscape pages)")
    else:
        print("[!] Warning: PDF generation failed.")

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL PRESENTATION ASSETS GENERATED CLEANLY!")
    print(f" 1. Native PowerPoint: {OUTPUT_PPTX} ({OUTPUT_PPTX.stat().st_size:,} bytes)")
    print(f" 2. HTML5 Deck:       {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size:,} bytes)")
    print(f" 3. Slide PDF:        {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size:,} bytes, {len(slides_data)} pages)")
    print("=" * 70)

if __name__ == "__main__":
    main()
