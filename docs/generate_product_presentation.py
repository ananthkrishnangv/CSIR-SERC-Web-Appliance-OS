"""
CSIR Secure Web Appliance OS (CSIR-SWA OS)
Comprehensive Presentation Deck Generator (HTML5, PDF, PPTX)

Features:
- Prompt Indigo AI SaaS UI Palette (#F5F3FF, #DDD6FE, #A78BFA, #6366F1, #312E81).
- Montserrat font for headings, Noto Sans for UI and body text.
- Comprehensive feature coverage: Native Web Hosting, Virtual Host Management,
  Reverse Proxy & Upstream Pools, SSL/TLS Key Vault, Podman Quadlets,
  Coraza WAF, Local AI Security Center, Data Protection, CERT-In Audit Ledger.
- TRUE DEDICATED FULL-WIDTH HERO SCREENSHOT PER SLIDE for all qualification views.
- Front and center 1:1 match for all 11 Web Management Console subsystems (Figure 1 to 11).
- Followed by 6 Appliance OS Bare-Metal & Hypervisor Provisioning Proof slides (Figure 12 to 17).
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
INSTALLER_SCREENSHOTS_DIR = DOCS_DIR / "screenshots" / "installer"

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
            is_dark = (bg in ["312E81", "1E1B4B", "071321", "0B132B", "0F172A"])
            cat_color = "A78BFA" if is_dark else "6366F1"
            title_color = "F5F3FF" if is_dark else "312E81"

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

        # Elements (Cards, Images)
        for el in elements:
            el_type = el.get("type", "card")
            x = el.get("x", 731520)
            y = el.get("y", 1500000)
            cx = el.get("cx", 5000000)
            cy = el.get("cy", 4000000)

            if el_type == "card":
                card_bg = el.get("bg", "FFFFFF")
                border = el.get("border", "DDD6FE")
                c_title = el.get("title", "")
                c_title_color = el.get("title_color", "312E81")
                bullets = el.get("bullets", [])

                p_tags = []
                if c_title:
                    p_tags.append(f"""
                    <a:p>
                      <a:pPr marL="0" indent="0"><a:buNone/></a:pPr>
                      <a:r>
                        <a:rPr lang="en-US" sz="1400" b="1">
                          <a:solidFill><a:srgbClr val="{c_title_color}"/></a:solidFill>
                          <a:latin typeface="Montserrat"/>
                        </a:rPr>
                        <a:t>{xml_escape(c_title)}</a:t>
                      </a:r>
                    </a:p>
                    """)

                for b in bullets:
                    b_str = str(b)
                    parts = b_str.split(":", 1)
                    if len(parts) == 2:
                        b_head, b_body = parts[0] + ":", parts[1]
                    else:
                        b_head, b_body = "", b_str

                    p_tags.append(f"""
                    <a:p>
                      <a:pPr marL="288000" indent="-288000">
                        <a:buClr><a:srgbClr val="6366F1"/></a:buClr>
                        <a:buSzPct val="100000"/>
                        <a:buFont typeface="Arial"/>
                        <a:buChar char="•"/>
                      </a:pPr>
                      <a:r>
                        <a:rPr lang="en-US" sz="1050" b="1">
                          <a:solidFill><a:srgbClr val="1E1B4B"/></a:solidFill>
                          <a:latin typeface="Noto Sans"/>
                        </a:rPr>
                        <a:t>{xml_escape(b_head)} </a:t>
                      </a:r>
                      <a:r>
                        <a:rPr lang="en-US" sz="1050">
                          <a:solidFill><a:srgbClr val="475569"/></a:solidFill>
                          <a:latin typeface="Noto Sans"/>
                        </a:rPr>
                        <a:t>{xml_escape(b_body)}</a:t>
                      </a:r>
                    </a:p>
                    """)

                shapes_xml.append(f"""
                <p:sp>
                  <p:nvSpPr>
                    <p:cNvPr id="{shape_id}" name="Card"/>
                    <p:cNvSpPr/>
                    <p:nvPr/>
                  </p:nvSpPr>
                  <p:spPr>
                    <a:xfrm>
                      <a:off x="{x}" y="{y}"/>
                      <a:ext cx="{cx}" cy="{cy}"/>
                    </a:xfrm>
                    <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 2000"/></a:avLst></a:prstGeom>
                    <a:solidFill><a:srgbClr val="{card_bg}"/></a:solidFill>
                    <a:ln w="25400"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>
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
                        <p:cNvPr id="{shape_id}" name="Picture"/>
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
                        <a:ln w="25400"><a:solidFill><a:srgbClr val="DDD6FE"/></a:solidFill></a:ln>
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
              <a:off x="731520" y="6400000"/>
              <a:ext cx="10725120" cy="300000"/>
            </a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            <a:noFill/>
          </p:spPr>
          <p:txBody>
            <a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0"/>
            <a:p>
              <a:r>
                <a:rPr lang="en-US" sz="850">
                  <a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill>
                  <a:latin typeface="Noto Sans"/>
                </a:rPr>
                <a:t>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0 | Prompt Indigo AI Edition</a:t>
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
        </p:sld>
        """

        rels_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
          {''.join(rels_xml)}
        </Relationships>
        """
        return slide_xml, rels_content

    def save(self):
        with zipfile.ZipFile(self.filename, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            # 1. Content Types
            ct_items = [
                '<Default Extension="xml" ContentType="application/xml"/>',
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                '<Default Extension="png" ContentType="image/png"/>',
                '<Default Extension="jpg" ContentType="image/jpeg"/>',
                '<Default Extension="jpeg" ContentType="image/jpeg"/>',
                '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
                '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
                '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
            ]
            for i in range(len(self.slides)):
                ct_items.append(f'<Override PartName="/ppt/slides/slide{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')

            z.writestr("[Content_Types].xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{"".join(ct_items)}</Types>')

            # 2. Package Relationships
            z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')

            # 3. Presentation XML
            sld_id_items = [f'<p:sldId id="{256+i}" r:id="rIdSld{i+1}"/>' for i in range(len(self.slides))]
            pres_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                            xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
              <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster1"/></p:sldMasterIdLst>
              <p:sldIdLst>{"".join(sld_id_items)}</p:sldIdLst>
              <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
              <p:notesSz cx="6858000" cy="9144000"/>
            </p:presentation>
            """
            z.writestr("ppt/presentation.xml", pres_xml)

            # Presentation Relationships
            pres_rels = [
                '<Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
            ]
            for i in range(len(self.slides)):
                pres_rels.append(f'<Relationship Id="rIdSld{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>')

            z.writestr("ppt/_rels/presentation.xml.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{"".join(pres_rels)}</Relationships>')

            # 4. Slide Master & Layout Minimal Stubs
            sm_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                         xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                         xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
              <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
              <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
            </p:sldMaster>"""
            z.writestr("ppt/slideMasters/slideMaster1.xml", sm_xml)
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>')

            sl_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                         xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                         xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                         type="blank">
              <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
            </p:sldLayout>"""
            z.writestr("ppt/slideLayouts/slideLayout1.xml", sl_xml)
            z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')

            # 5. Media files
            for m_name, m_path in self.media_files.items():
                z.write(m_path, f"ppt/media/{m_name}")

            # 6. Slides
            for i, s_data in enumerate(self.slides):
                s_xml, s_rels = self.build_slide_xml(i+1, s_data)
                z.writestr(f"ppt/slides/slide{i+1}.xml", s_xml)
                z.writestr(f"ppt/slides/_rels/slide{i+1}.xml.rels", s_rels)

# ==============================================================================
# 2. DEFINITION OF ALL SLIDES (1-to-1 Match with Latest Screenshots)
# ==============================================================================

def build_all_slides_data(builder: PPTXBuilder = None):
    def reg(p):
        return builder.add_media(p) if builder else Path(p).name

    # 14 LATEST WEB MANAGEMENT CONSOLE SCREENSHOTS
    img_c_ov       = reg(SCREENSHOTS_DIR / "web_console_01_overview.png")
    img_c_vh       = reg(SCREENSHOTS_DIR / "web_console_02_vhosts.png")
    img_c_vmodal   = reg(SCREENSHOTS_DIR / "web_console_02b_vhost_modal.png")
    img_c_px       = reg(SCREENSHOTS_DIR / "web_console_03_proxy.png")
    img_c_ssl      = reg(SCREENSHOTS_DIR / "web_console_04_ssl.png")
    img_c_app      = reg(SCREENSHOTS_DIR / "web_console_05_applications.png")
    img_c_kvm      = reg(SCREENSHOTS_DIR / "web_console_06_virtualization_kvm.png")
    img_c_kvm_wiz  = reg(SCREENSHOTS_DIR / "web_console_06b_kvm_setup_wizard.png")
    img_c_waf      = reg(SCREENSHOTS_DIR / "web_console_07_security_waf.png")
    img_c_ai       = reg(SCREENSHOTS_DIR / "web_console_08_ai_security_center.png")
    img_c_dr       = reg(SCREENSHOTS_DIR / "web_console_09_data_protection_backups.png")
    img_c_comp     = reg(SCREENSHOTS_DIR / "web_console_10_compliance_audit_ledger.png")
    img_c_upd      = reg(SCREENSHOTS_DIR / "web_console_11_transactional_updates.png")
    img_c_term     = reg(SCREENSHOTS_DIR / "web_console_12_boot_screen_console.png")

    # 6 APPLIANCE OS PROVISIONING & HYPERVISOR INSTALLATION SCREENSHOTS
    img_boot = reg(INSTALLER_SCREENSHOTS_DIR / "vm_boot_menu_v2.jpg")
    img_yast = reg(INSTALLER_SCREENSHOTS_DIR / "vm_step4_yast.jpg")
    img_net  = reg(INSTALLER_SCREENSHOTS_DIR / "vm_step5_yast_net.jpg")
    img_part = reg(INSTALLER_SCREENSHOTS_DIR / "vm_step8_partitioning.jpg")
    img_conf = reg(INSTALLER_SCREENSHOTS_DIR / "vm_final_gui_proof_ready2.jpg")
    img_tty3 = reg(INSTALLER_SCREENSHOTS_DIR / "vm_tty3_log.jpg")

    slides = []

    # --------------------------------------------------------------------------
    # SLIDE 1: Executive Cover Slide
    # --------------------------------------------------------------------------
    slides.append({
        "type": "title",
        "bg": "312E81",
        "category": "SOVEREIGN GOVERNMENT CLOUD",
        "title": "CSIR Secure Web Appliance OS (CSIR-SWA OS)",
        "subtitle": "Next-Generation Hardened, Immutable, and Containerized Web Hosting Appliance",
        "bullets": [
            "Engineered for classified research laboratories, government web portals, and critical public infrastructure.",
            "Prompt Indigo AI SaaS Architecture with Tailwind CSS, daisyUI, and Glassmorphic aesthetics.",
            "Integrated Multi-Tenant Web Hosting, Virtual Host Manager, KVM VM Manager, HAProxy Proxy, and ACME SSL Key Vault."
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 2: Figure 1 - Overview Dashboard (web_console_01_overview.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 1: Central Operations & Security Health Overview Dashboard",
        "image_file": img_c_ov,
        "caption": "Figure 1: Glassmorphic Operations & Health Dashboard with 4 Trend KPIs, Live Workloads, Threat Shields & ChatOps.",
        "specs": [
            {"label": "Executive Health KPI", "detail": "98.4% operational health score across 24 microservices"},
            {"label": "Proxy Ingress Telemetry", "detail": "1,842 req/s throughput with sub-10ms p95 latency"},
            {"label": "Coraza Threat Shield", "detail": "1,429 blocked attacks with 100% drop & zero bypasses"},
            {"label": "Prompt Indigo ChatOps", "detail": "Real-time security timeline with sovereign AI assistant"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 3: Figure 2 - Virtual Hosts (web_console_02_vhosts.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 2: Native Web Hosting & Multi-Tenant Virtual Host Fleet",
        "image_file": img_c_vh,
        "caption": "Figure 2: Native Virtual Host Manager with Multi-Tenant Runtimes (PHP 8.2, Node 20, Python ASGI), Quotas & SSL Status.",
        "specs": [
            {"label": "Multi-Tenant Isolation", "detail": "Enforced document roots under /srv/www/vhosts with strict POSIX perms"},
            {"label": "Polyglot Runtimes", "detail": "Native support for PHP 8.2-FPM, Node.js 20 SSR, Python ASGI & Static"},
            {"label": "Storage Quota Bars", "detail": "Visual disk consumption tracking with automated threshold enforcement"},
            {"label": "Active SSL Binding", "detail": "Instant binding to automated Let's Encrypt and wildcard certificates"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 4: Figure 3 - Virtual Host Configuration Modal (web_console_02b_vhost_modal.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 3: Virtual Host Configuration & Background Stack Setup Modal",
        "image_file": img_c_vmodal,
        "caption": "Figure 3: Add Virtual Host Modal with Background Application Stack Selection (PHP, Node, Python, Static) and SSL/TLS Binding.",
        "specs": [
            {"label": "Application Runtime Selection", "detail": "Interactive stack choice for PHP 8.2-FPM, Node.js 20 SSR, Python 3.11 ASGI, or Static"},
            {"label": "Tunable Worker Daemons", "detail": "Selectable 2, 4, 8, or 16 isolated worker processes running in unprivileged cgroups"},
            {"label": "Sovereign SSL/TLS Binding", "detail": "Automated ACME Let's Encrypt, TPM Hardware Internal CA, or Enterprise CRT upload"},
            {"label": "Security Enforcements", "detail": "Mandatory HTTP 301 HTTPS redirection and HSTS (31536000s) security headers"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 5: Figure 4 - Reverse Proxy (web_console_03_proxy.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 4: HAProxy Dynamic Reverse Proxy & Upstream Server Pools",
        "image_file": img_c_px,
        "caption": "Figure 4: HAProxy Sovereign Router with Target Pools, Load Balancing Algorithms, Active Health Probes & Routes.",
        "specs": [
            {"label": "Upstream Target Pools", "detail": "Dedicated server pools for Structural Health, Wind Tunnel, and Local AI"},
            {"label": "Balancing Algorithms", "detail": "Round-Robin, Least-Connections, and IP-Hash session pinning"},
            {"label": "Active Health Checks", "detail": "Deterministic HTTP probes every 3-10s with automatic failover"},
            {"label": "Edge Hardening", "detail": "Strict HTTP-to-HTTPS redirect, WebSocket passthrough, and DDoS rate limits"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 6: Figure 5 - SSL Vault (web_console_04_ssl.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 5: Sovereign SSL / TLS Certificate Vault & ACME Key Management",
        "image_file": img_c_ssl,
        "caption": "Figure 5: Cryptographic SSL/TLS Vault with ACME Auto-Renewal, ECDSA 384-bit & RSA 4096-bit Keys, and CSR Generator.",
        "specs": [
            {"label": "Automated ACME Lifecycle", "detail": "Zero-touch renewal for *.serc.res.in 30 days prior to certificate expiry"},
            {"label": "Military-Grade Keys", "detail": "ECDSA secp384r1 and RSA 4096-bit institutional private keys"},
            {"label": "Strict TLS 1.3 Suite", "detail": "Hardened cipher suites with zero legacy fallback vulnerabilities"},
            {"label": "Sovereign CSR Tool", "detail": "Integrated generation of certified government certificate signing requests"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 7: Figure 6 - Container Quadlets (web_console_05_applications.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 6: Rootless Podman Quadlet Container Workloads",
        "image_file": img_c_app,
        "caption": "Figure 6: Rootless Podman Quadlet Container Workloads with Cryptographic Cosign Digests & UserNS Sandboxing.",
        "specs": [
            {"label": "Cosign Verification", "detail": "Mandatory cryptographic signature verification before workload ignition"},
            {"label": "Rootless UserNS Sandbox", "detail": "Zero root privileges inside containers, mitigating container breakout risks"},
            {"label": "Strict Hard Quotas", "detail": "Enforced memory allocations (256MB-1024MB) and 50% CPU ceilings"},
            {"label": "Systemd Supervision", "detail": "Automated health watchdog monitoring with instant restart on crash"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 8: Figure 7 - KVM Hypervisor Active (web_console_06_virtualization_kvm.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 7: KVM Hardware Virtualization & Virtual Machine Manager",
        "image_file": img_c_kvm,
        "caption": "Figure 7: KVM Virtual Machine Manager with QEMU 8.2, Hardware VT-x/AMD-V Acceleration, and 4 Provisioned Guest VMs.",
        "specs": [
            {"label": "Hypervisor Backend", "detail": "QEMU/KVM 8.2 with hardware VT-x/AMD-V acceleration and libvirtd daemon"},
            {"label": "Multi-OS Guest Workloads", "detail": "AlmaLinux 9 Enterprise, Ubuntu 24.04 AI Node, Windows Server 2022 & CentOS 7"},
            {"label": "Resource Commit Pool", "detail": "16 vCPUs and 32 GB RAM allocated across guests on virbr0 virtual bridge"},
            {"label": "Web Console Suite", "detail": "Direct browser-based SPICE and VNC display consoles on ports 5901-5904"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 9: Figure 8 - KVM Setup Wizard (web_console_06b_kvm_setup_wizard.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 8: KVM Subsystem Setup & One-Click Hypervisor Deployment Wizard",
        "image_file": img_c_kvm_wiz,
        "caption": "Figure 8: Interactive KVM Setup Wizard Displayed When Virtualization Is Not Yet Installed, Featuring 1-Click Activation.",
        "specs": [
            {"label": "Hardware VT Detection", "detail": "Automatic kernel inspection verifying Intel VT-x / AMD-V CPU readiness"},
            {"label": "Transactional Packaging", "detail": "Atomic deployment of qemu-kvm, libvirt-daemon-system, and virt-install"},
            {"label": "Web Management Console", "detail": "Cockpit Machines web interface integrated seamlessly with zero reboot"},
            {"label": "One-Click Initialization", "detail": "Single-click activation creating an atomic Btrfs transactional snapshot"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 10: Figure 9 - Coraza WAF (web_console_07_security_waf.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 9: Coraza Sovereign WAF & nftables Network Defense",
        "image_file": img_c_waf,
        "caption": "Figure 9: Real-Time Coraza OWASP CRS Rule Toggles, Paranoia Level Enforcement & Default-Deny nftables Firewall.",
        "specs": [
            {"label": "OWASP CRS v4 Defense", "detail": "Active mitigation of SQLi (942100), XSS (941100), RCE (932100) & LFI (930100)"},
            {"label": "Paranoia Strictness L2", "detail": "Enhanced scrutiny on administrative endpoints without disrupting users"},
            {"label": "nftables Kernel Filter", "detail": "Default-deny ingress policy with strict whitelisting for bastion SSH"},
            {"label": "Zero Cloud Telemetry", "detail": "100% on-premises packet inspection preserving national confidentiality"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 11: Figure 10 - Local AI Security (web_console_08_ai_security_center.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 10: Local AI Security Center & Incident Root Cause Analysis",
        "image_file": img_c_ai,
        "caption": "Figure 10: Local AI Security Center with Plain-English Incident Narratives, Human Approval Gates & ChatOps Telemetry.",
        "specs": [
            {"label": "Incident Synthesis", "detail": "Autonomous plain-English briefings of scanner probes (Narrative NAR-882)"},
            {"label": "Human Approval Gates", "detail": "Strict mandatory human approval required before AI mitigations are committed"},
            {"label": "Database Diagnostics", "detail": "Automated RCA identifying unindexed queries and optimal connection pooling"},
            {"label": "Sovereign ChatOps", "detail": "Natural language query interface for instant cluster operational control"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 12: Figure 11 - Data Protection & DR (web_console_09_data_protection_backups.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 11: Immutable Data Protection & Btrfs Automated DR Drills",
        "image_file": img_c_dr,
        "caption": "Figure 11: Snapper Btrfs Subvolume Trees, Restic Deduplicated Backups & Automated Sandbox DR Verification Drills.",
        "specs": [
            {"label": "Btrfs Subvolume Tree", "detail": "Granular snapshot management across root (@), data (@/srv), and logs (@/var)"},
            {"label": "Verified DR Drills", "detail": "Measured RTO (12s-23s) and measured RPO (15s-45s) for production portals"},
            {"label": "SHA-256 Hash Auditing", "detail": "Full cryptographic verification confirming zero data degradation post-restore"},
            {"label": "Ransomware Immunity", "detail": "Read-only snapshot hierarchies guarantee instant rollback against crypto-malware"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 13: Figure 12 - CERT-In Audit Ledger (web_console_10_compliance_audit_ledger.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 12: CERT-In Section 70B Cryptographic SHA-256 Audit Ledger",
        "image_file": img_c_comp,
        "caption": "Figure 12: CERT-In Section 70B Tamper-Evident SHA-256 Hash-Chained Audit Ledger with 180-Day Retention Lock.",
        "specs": [
            {"label": "SHA-256 Hash Chaining", "detail": "SHA256(prev_hash | entry_hash) guarantees mathematical tamper-evidence"},
            {"label": "Section 70B Compliance", "detail": "Comprehensive auditing of every privileged state change and WAF toggle"},
            {"label": "NPL Stratum 1 Discipline", "detail": "Chronyd synchronized strictly against Indian National Physical Laboratory"},
            {"label": "1-Click Certified Dossier", "detail": "Rapid statutory export fulfilling CERT-In 6-hour incident window"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 14: Figure 13 - Transactional Updates (web_console_11_transactional_updates.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Web Console Subsystem",
        "title": "Figure 13: openSUSE MicroOS Transactional-Updates & Rollback",
        "image_file": img_c_upd,
        "caption": "Figure 13: MicroOS Transactional Update Engine with Read-Only Root Snapshot #14, Staging Trees & Health Gate.",
        "specs": [
            {"label": "Read-Only System Root", "detail": "Appliance operating system executes from immutable snapshot #14"},
            {"label": "Atomic Update Staging", "detail": "OS updates install into isolated snapshots with zero runtime interruption"},
            {"label": "Health-Gated Reversion", "detail": "Automated rollback reboot if post-boot health probes detect failure"},
            {"label": "1-Click Instant Rollback", "detail": "Administrative console allows immediate reversion to known-good baseline"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 15: Figure 14 - Boot Screen Console (web_console_12_boot_screen_console.png)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Hardware Console Subsystem",
        "title": "Figure 14: Bare-Metal Hardware & Diagnostic Terminal Console",
        "image_file": img_c_term,
        "caption": "Figure 14: Bare-Metal Diagnostic Console Banner with Hardware Integrity Checks, Emergency Keys & Statutory Notice.",
        "specs": [
            {"label": "Diagnostic Boot Banner", "detail": "Official ASCII institutional console banner displayed on bare-metal boot"},
            {"label": "Hardware Validation", "detail": "Automated validation of TPM 2.0, Secure Boot, LUKS disks & NPL clock sync"},
            {"label": "Emergency Recovery Keys", "detail": "F2 hotkey for console access, F8 hotkey for emergency immutable rollback"},
            {"label": "Statutory Access Lock", "detail": "Legal access warning restricting appliance entry to authorized personnel"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 16: Figure 15 - GRUB2 Bootloader (vm_boot_menu_v2.jpg)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Bare-Metal Provisioning",
        "title": "Figure 15: Purpose-Driven GRUB2 Bootloader & Profile Selection",
        "image_file": img_boot,
        "caption": "Figure 15: Official CSIR-SERC GRUB2 Graphical Bootloader with Profile Options for Full-Stack, Web Hosting, KVM & Airgap.",
        "specs": [
            {"label": "Purpose Profile Selection", "detail": "Dedicated boot options for Full-Stack, Web Hosting Gateway, KVM, Edge WAF, or Airgap"},
            {"label": "1024x768 Graphical Canvas", "detail": "TrueColor graphical frame-buffer with official CSIR-SERC institutional seal"},
            {"label": "Automated Boot Ingestion", "detail": "Direct kernel ingestion of combustion script and AutoYaST deployment rules"},
            {"label": "Multi-Platform Support", "detail": "Unified UEFI x86_64 and legacy BIOS firmware compatibility"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 17: Figure 16 - AutoYaST Core (vm_step4_yast.jpg)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Bare-Metal Provisioning",
        "title": "Figure 16: AutoYaST Automated OS Installation Engine",
        "image_file": img_yast,
        "caption": "Figure 16: Automated YaST Control Flow - Unattended Installation Ingestion & Base Operating System Deployment.",
        "specs": [
            {"label": "Zero-Touch Provisioning", "detail": "Fully autonomous unattended installation eliminating manual technician errors"},
            {"label": "Package Pattern Resolution", "detail": "Automated dependency calculation for MicroOS core and container engine"},
            {"label": "Secure Boot Verification", "detail": "Mandatory validation of kernel signatures and cryptographic platform keys"},
            {"label": "Non-Interactive Mode", "detail": "Direct hands-free installation for automated data center rollouts"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 18: Figure 17 - Network Ingestion (vm_step5_yast_net.jpg)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Bare-Metal Provisioning",
        "title": "Figure 17: Network & Ingress Interface Configuration",
        "image_file": img_net,
        "caption": "Figure 17: Network Interface Bonding, Static IPv4/IPv6 Addressing & Gateway Ingress Configuration.",
        "specs": [
            {"label": "Predictable Naming", "detail": "Deterministic interface mapping for management and public ingress"},
            {"label": "Hardware Offloading", "detail": "TCP segmentation offload and checksum calculation enabled on NICs"},
            {"label": "DNS Resolver Hardening", "detail": "High-availability DNS resolver configuration with local cache fallbacks"},
            {"label": "Isolated Mgmt Segment", "detail": "Out-of-band management subnet routing for administration traffic"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 19: Figure 18 - Btrfs Subvolumes (vm_step8_partitioning.jpg)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Bare-Metal Provisioning",
        "title": "Figure 18: Btrfs Subvolume Topology & Partitioning",
        "image_file": img_part,
        "caption": "Figure 18: Automated Partitioning Table - Btrfs Root, Granular Subvolumes (@, @/srv, @/var) & ESP Mount.",
        "specs": [
            {"label": "Immutable Root Isolation", "detail": "Subvolume separation ensuring OS root remains isolated from application data"},
            {"label": "Dedicated Data Subvolume", "detail": "/srv subvolume optimized with nocow flag for high-IOPS database operations"},
            {"label": "Dynamic Quota Enforcement", "detail": "Subvolume-level storage limits preventing disk exhaustion attacks"},
            {"label": "Snapper Integration", "detail": "Deep kernel integration for transparent copy-on-write snapshot creation"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 20: Figure 19 - Hardware Topology (vm_final_gui_proof_ready2.jpg)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Bare-Metal Provisioning",
        "title": "Figure 19: Hypervisor Resource Allocation & Hardware Proof",
        "image_file": img_conf,
        "caption": "Figure 19: Comprehensive System Configuration Summary - 4 vCPUs, 8GB ECC RAM, 30GB Disk & Network Topology.",
        "specs": [
            {"label": "Hardware Topology", "detail": "Multi-core vCPU allocation with dedicated memory mapping and VT-x flags"},
            {"label": "Storage Controller", "detail": "High-performance VirtIO SCSI / SATA storage controller configuration"},
            {"label": "Virtual Network Bridge", "detail": "Dedicated host-only and NAT network adapters for testbed isolation"},
            {"label": "Display Subsystem", "detail": "High-resolution VBoxVGA/QXL frame-buffer for administrative boot verification"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 21: Figure 20 - TTY3 Diagnostic Console (vm_tty3_log.jpg)
    # --------------------------------------------------------------------------
    slides.append({
        "type": "hero_screenshot",
        "bg": "F5F3FF",
        "category": "Visual Qualification: Bare-Metal Provisioning",
        "title": "Figure 20: Diagnostic Linuxrc Installation Console & TTY3 Shell",
        "image_file": img_tty3,
        "caption": "Figure 20: TTY3 Real-Time Linuxrc Installation Diagnostics, Kernel Probing & Hardware Telemetry.",
        "specs": [
            {"label": "Kernel Telemetry", "detail": "Live tracking of device driver probing, hardware interrupts & storage mounting"},
            {"label": "Storage Attachment", "detail": "SATA/NVMe controller discovery and LUKS encrypted container initialization"},
            {"label": "Diagnostic Audit Shell", "detail": "Unprivileged audit terminal accessible via Ctrl+Alt+F3 during installation"},
            {"label": "Fail-Safe Logging", "detail": "Direct logging of all low-level hardware interactions for post-install audit"}
        ]
    })

    # --------------------------------------------------------------------------
    # SLIDE 19: Strategic Architecture Wrap-up
    # --------------------------------------------------------------------------
    slides.append({
        "type": "content_2col",
        "bg": "F5F3FF",
        "category": "Architectural Synthesis",
        "title": "Comprehensive Defense-in-Depth & Deployment Summary",
        "card1": {
            "title": "Four Pillars of Sovereign Security",
            "bullets": [
                "Layer 1 - Host Immutability: Read-only Btrfs root snapshot prevents malware foothold persistence.",
                "Layer 2 - Workload Sandboxing: Rootless Podman Quadlets with UserNS isolation eliminate privilege escalation.",
                "Layer 3 - Real-Time WAF Defense: Coraza OWASP CRS v4 inspects 100% on-premises with zero cloud leaks.",
                "Layer 4 - Cryptographic Audit: SHA-256 hash-chained ledger guarantees CERT-In statutory adherence."
            ]
        },
        "card2": {
            "title": "Turn-Key Deployment Modalities",
            "bullets": [
                "Monolithic Full-Stack ISO: csir-swa-os-1.0.0-fullstack-x86_64.iso (2.73 GB) for 100% air-gapped bare-metal.",
                "Universal Online Bootstrap: Remote curl-based bootstrap for rapid provisioning on commodity VPS nodes.",
                "MicroOS Conversion Engine: Dedicated script (convert-microos.sh) transforms vanilla openSUSE nodes.",
                "VirtualBox & Hyper-V Testbeds: Turn-key automated provisioning with 30GB disk and port forwardings."
            ]
        }
    })

    # --------------------------------------------------------------------------
    # SLIDE 20: Executive Conclusion
    # --------------------------------------------------------------------------
    slides.append({
        "type": "title",
        "bg": "312E81",
        "category": "EXECUTIVE CONCLUSION",
        "title": "Institutional Impact & Sovereign Technology Sovereignty",
        "subtitle": "Complete Liberation from Proprietary Software Licenses with Certified National Security Compliance",
        "bullets": [
            "Financial Sovereignty: Eliminates recurring commercial license fees for operating systems, commercial WAFs, and load balancers.",
            "Statutory Assurance: Built-in 1-click incident dossier generation directly fulfills national CERT-In 6-hour disclosure mandates.",
            "Universal Delivery: Complete deliverables suite including Monolithic DVD ISO, Web Management Console, and Full Documentation."
        ]
    })

    return slides

# ==============================================================================
# 3. INTERACTIVE HTML5 PRESENTATION GENERATOR (Prompt Indigo AI SaaS UI Theme)
# ==============================================================================

def generate_interactive_html(slides: list) -> str:
    total_slides = len(slides)
    slides_html = []

    for i, s in enumerate(slides):
        slide_num = i + 1
        s_type = s.get("type", "hero_screenshot")
        bg = s.get("bg", "F5F3FF")
        category = s.get("category", "")
        title = s.get("title", "")
        is_dark = (bg in ["312E81", "1E1B4B", "071321", "0B132B", "0F172A"])

        dark_class = "slide-dark" if is_dark else ""
        content_html = ""

        if s_type == "title":
            subtitle = s.get("subtitle", "")
            bullets = s.get("bullets", [])
            bullets_li = "".join([f"<li class='flex items-start gap-3 text-violet-100 text-base'><span class='w-2.5 h-2.5 rounded-full bg-violet-400 mt-2 shrink-0'></span><span>{b}</span></li>" for b in bullets])

            content_html = f"""
            <div class="h-full flex flex-col justify-between p-12">
                <div>
                    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-950/80 border border-violet-400/40 text-violet-300 font-heading font-extrabold text-xs uppercase tracking-widest mb-6 shadow-sm">
                        <i class="fa-solid fa-shield-halved"></i> {category}
                    </div>
                    <h1 class="font-heading font-extrabold text-4xl sm:text-5xl text-white tracking-tight leading-tight max-w-4xl">
                        {title}
                    </h1>
                    <p class="font-heading font-medium text-xl text-violet-200/90 mt-4 max-w-3xl leading-relaxed">
                        {subtitle}
                    </p>
                </div>

                <div class="glass-card-dark rounded-2xl p-8 border border-violet-400/30 max-w-4xl my-6">
                    <div class="text-xs font-heading font-bold text-violet-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-layer-group"></i> Core Architectural Mandate
                    </div>
                    <ul class="space-y-3.5">
                        {bullets_li}
                    </ul>
                </div>

                <div class="flex items-center justify-between text-xs font-mono text-violet-300/70 border-t border-indigo-800/80 pt-4">
                    <span>Council of Scientific &amp; Industrial Research (CSIR-SERC)</span>
                    <span>Version 1.0.0 Stable Channel • Prompt Indigo Edition</span>
                </div>
            </div>
            """

        elif s_type == "content_2col":
            c1 = s.get("card1", {})
            c2 = s.get("card2", {})

            b1_li = "".join([f"<li class='text-sm text-slate-700 leading-relaxed'><strong class='text-indigo-950'>{b.split(':')[0]}:</strong>{b.split(':', 1)[1] if ':' in b else ''}</li>" for b in c1.get("bullets", [])])
            b2_li = "".join([f"<li class='text-sm text-slate-700 leading-relaxed'><strong class='text-indigo-950'>{b.split(':')[0]}:</strong>{b.split(':', 1)[1] if ':' in b else ''}</li>" for b in c2.get("bullets", [])])

            content_html = f"""
            <div class="h-full flex flex-col justify-between p-10">
                <div class="slide-header">
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-100 text-indigo-900 border border-violet-200 text-xs font-heading font-extrabold uppercase tracking-wider mb-2">
                        {category}
                    </div>
                    <h2 class="font-heading font-extrabold text-2xl sm:text-3xl text-indigo-950 tracking-tight">
                        {title}
                    </h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 my-auto">
                    <div class="glass-card rounded-2xl p-7 border-l-4 border-l-indigo-600 flex flex-col justify-between shadow-md">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-indigo-950 mb-4">{c1.get('title', '')}</h3>
                            <ul class="space-y-3.5 list-disc list-inside">
                                {b1_li}
                            </ul>
                        </div>
                    </div>
                    <div class="glass-card rounded-2xl p-7 border-l-4 border-l-violet-500 flex flex-col justify-between shadow-md">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-indigo-950 mb-4">{c2.get('title', '')}</h3>
                            <ul class="space-y-3.5 list-disc list-inside">
                                {b2_li}
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-violet-200/70 pt-3">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0</span>
                    <span class="font-mono font-semibold text-indigo-900">Slide {slide_num} of {total_slides}</span>
                </div>
            </div>
            """

        elif s_type == "hero_screenshot":
            img_file = s.get("image_file", "")
            caption = s.get("caption", "")
            specs = s.get("specs", [])

            # Generate spec cards
            spec_cards_html = []
            for sp in specs:
                lbl = sp.get("label", "Specification")
                dtl = sp.get("detail", "")
                spec_cards_html.append(f"""
                <div class="p-2.5 rounded-xl bg-white/90 border border-violet-200/80 shadow-sm flex items-start gap-2">
                    <i class="fa-solid fa-circle-check text-indigo-600 mt-0.5 shrink-0 text-xs"></i>
                    <div class="text-[11px] text-slate-700 leading-tight">
                        <strong class="text-indigo-950 block mb-0.5">{lbl}</strong>
                        {dtl}
                    </div>
                </div>
                """)

            # Ensure relative path points to docs/screenshots
            if "web_console" in str(img_file):
                rel_img_src = f"screenshots/web_console/{Path(img_file).name}"
            else:
                rel_img_src = f"screenshots/installer/{Path(img_file).name}"

            content_html = f"""
            <div class="h-full flex flex-col justify-between p-6">
                <!-- Header -->
                <div class="flex items-center justify-between mb-1.5">
                    <div>
                        <div class="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-violet-100 text-indigo-900 border border-violet-200 text-[11px] font-heading font-extrabold uppercase tracking-wider">
                            <i class="fa-solid fa-camera text-indigo-600"></i> {category}
                        </div>
                        <h2 class="font-heading font-extrabold text-xl sm:text-2xl text-indigo-950 tracking-tight mt-1">
                            {title}
                        </h2>
                    </div>
                    <span class="badge badge-md bg-indigo-600 text-white font-mono px-3 py-1 font-semibold border-none">
                        Dedicated Verification Slide
                    </span>
                </div>

                <!-- Full-Width Hero Screenshot Card -->
                <div class="w-full glass-card p-2 rounded-2xl border border-violet-200 shadow-xl overflow-hidden bg-white/80 my-auto flex items-center justify-center">
                    <img src="{rel_img_src}" alt="{title}" class="w-full max-h-[62vh] object-contain rounded-xl shadow-sm">
                </div>

                <!-- Bottom Specs Strip (Horizontal 4-Column Grid) -->
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mt-1.5">
                    {''.join(spec_cards_html)}
                </div>

                <!-- Footer -->
                <div class="flex items-center justify-between text-xs text-slate-500 border-t border-violet-200/70 pt-2 mt-1.5">
                    <span>CSIR Secure Web Appliance OS (CSIR-SWA OS) v1.0.0 | Proof of Verification</span>
                    <span class="font-mono font-semibold text-indigo-900">Slide {slide_num} of {total_slides}</span>
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
        background: #1e1b4b;
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
        background: #f5f3ff;
        box-shadow: 0 20px 40px rgba(49, 46, 129, 0.25);
    }}

    @media screen {{
        body {{
            padding: 20px 0;
            background: #1e1b4b;
        }}
        .slide {{
            margin-bottom: 30px;
            border-radius: 12px;
        }}
    }}

    .slide-dark {{
        background: #312e81 !important;
        color: #f5f3ff !important;
    }}

    /* Glassmorphism Classes - Prompt Indigo Palette */
    .glass-card {{
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid #ddd6fe;
        box-shadow: 0 4px 20px -2px rgba(49, 46, 129, 0.08);
    }}

    .glass-card-dark {{
        background: rgba(49, 46, 129, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(167, 139, 250, 0.35);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
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
        background: rgba(49, 46, 129, 0.92);
        backdrop-filter: blur(12px);
        padding: 8px 16px;
        border-radius: 9999px;
        border: 1px solid rgba(167, 139, 250, 0.35);
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
    <span id="slideCounter" class="text-xs font-mono font-bold text-violet-300">1 / {total_slides}</span>
    <button onclick="nextSlide()" class="btn btn-circle btn-xs btn-ghost text-white"><i class="fa-solid fa-chevron-right"></i></button>
    <button onclick="window.print()" class="btn btn-xs btn-primary bg-indigo-600 hover:bg-indigo-700 border-none rounded-full text-white ml-2"><i class="fa-solid fa-print"></i> PDF Export</button>
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
    print(" Single Dedicated Hero Screenshot per Page Layout (Prompt Indigo Theme)")
    print(" 1-to-1 Match with All 11 Latest Subsystem Screenshots")
    print("=" * 70)

    # 1. Build PPTX
    print("\n[*] Initializing PPTX Builder...")
    pptx_builder = PPTXBuilder(OUTPUT_PPTX)
    slides_data = build_all_slides_data(pptx_builder)

    for i, s in enumerate(slides_data):
        s_type = s.get("type", "hero_screenshot")
        bg = s.get("bg", "F5F3FF")
        cat = s.get("category", "")
        title = s.get("title", "")

        elements = []
        if s_type == "title":
            elements.append({
                "type": "card",
                "x": 731520, "y": 1400000, "cx": 10725120, "cy": 4500000,
                "bg": "312E81", "border": "6366F1",
                "title": s.get("title", ""),
                "title_color": "A78BFA",
                "bullets": [s.get("subtitle", "")] + s.get("bullets", [])
            })
        elif s_type == "content_2col":
            c1 = s.get("card1", {})
            c2 = s.get("card2", {})
            elements.append({
                "type": "card",
                "x": 731520, "y": 1828800, "cx": 5166360, "cy": 4389120,
                "bg": "FFFFFF", "border": "6366F1",
                "title": c1.get("title", ""),
                "title_color": "312E81",
                "bullets": c1.get("bullets", [])
            })
            elements.append({
                "type": "card",
                "x": 6294120, "y": 1828800, "cx": 5166360, "cy": 4389120,
                "bg": "FFFFFF", "border": "A78BFA",
                "title": c2.get("title", ""),
                "title_color": "6366F1",
                "bullets": c2.get("bullets", [])
            })
        elif s_type == "hero_screenshot":
            m_name = Path(s.get("image_file", "")).name
            specs = s.get("specs", [])
            spec_bullets = [f"{sp.get('label', '')}: {sp.get('detail', '')}" for sp in specs]

            # Hero Screenshot (Prominent Widescreen)
            elements.append({
                "type": "image",
                "x": 731520, "y": 1500000, "cx": 10725120, "cy": 4300000,
                "media_name": m_name
            })
            # Bottom Specifications Strip
            elements.append({
                "type": "card",
                "x": 731520, "y": 5900000, "cx": 10725120, "cy": 650000,
                "bg": "FFFFFF", "border": "DDD6FE",
                "title": "",
                "bullets": spec_bullets
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
        "--allow-file-access-from-files",
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
