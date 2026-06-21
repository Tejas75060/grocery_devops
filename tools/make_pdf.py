#!/usr/bin/env python3
"""Render the project documentation to a PDF (simple black theme).

Cover page + problem statement + solution + tech stack + all stack screenshots.
Uses headless Chromium (Playwright) to render HTML -> PDF.
"""
import os
from playwright.sync_api import sync_playwright

ROOT = "/Users/tejasmhatre/Desktop/grocery"
SHOTS = os.path.join(ROOT, "docs", "screenshots")
OUT = os.path.join(ROOT, "docs", "Grocery_DevOps_Documentation.pdf")


def img(path):
    return "file://" + os.path.join(SHOTS, path)


SECTIONS = [
    ("1. Application — FastAPI",
     "Backend with endpoints for placing orders, tracking status, inventory "
     "check and delivery assignment. SQLAlchemy models, an order state machine, "
     "and a built-in dashboard. Validated with an automated test suite.",
     [("01-app/01-pytest.png", "Automated tests — 6 passing")]),

    ("2. Docker — Containerization",
     "Multi-stage Dockerfile (non-root, healthcheck) and docker-compose running "
     "the backend together with PostgreSQL. The backend also serves the dashboard.",
     [("02-docker/01-dashboard.png", "Dashboard served from the container (live orders)"),
      ("02-docker/02-swagger.png", "Swagger / OpenAPI documentation"),
      ("02-docker/03-compose-ps.png", "docker compose ps — app + database healthy"),
      ("02-docker/04-docker-images.png", "Built images")]),

    ("3. Jenkins — CI/CD Pipeline",
     "Declarative pipeline: Checkout, Build & Test, Docker Build, Push to "
     "registry, Deploy. Tests run in an isolated python:3.11 container; the "
     "image is pushed to a local registry.",
     [("03-jenkins/01-pipeline-stages.png", "Pipeline builds green; 6 tests passing"),
      ("03-jenkins/02-console-success.png", "Console — all stages SUCCESS"),
      ("03-jenkins/03-build-graph.png", "Build detail — git revision + tests"),
      ("03-jenkins/04-dashboard.png", "Jenkins dashboard")]),

    ("4. Terraform — Infrastructure as Code",
     "Provisions the local environment (network, PostgreSQL, app, registry) with "
     "the local Docker provider — no cloud-managed services. Local state backend.",
     [("04-terraform/01-tf-apply.png", "terraform apply — 8 resources created"),
      ("04-terraform/02-tf-output.png", "terraform output"),
      ("04-terraform/03-docker-ps.png", "Provisioned containers")]),

    ("5. Kubernetes — Orchestration & Autoscaling",
     "Deployment, Service, Ingress, ConfigMap, Secret, a Postgres StatefulSet, "
     "and an HPA on a local kind cluster. The HPA scales the app under load.",
     [("05-kubernetes/01-get-all.png", "pods, services, ingress, HPA"),
      ("05-kubernetes/02-dashboard-ingress.png", "App via Ingress (grocery.localhost)"),
      ("05-kubernetes/03-hpa-scaling.png", "HPA autoscaling 2 to 8 pods under load"),
      ("05-kubernetes/04-hpa-pods.png", "Scaled replicas + HPA status")]),

    ("6. Monitoring & Logging — Prometheus, Grafana, ELK",
     "Prometheus scrapes app metrics via Kubernetes service discovery; Grafana "
     "visualises them. The ELK stack centralises structured application logs.",
     [("06-monitoring/01-prometheus-targets.png", "Prometheus targets UP"),
      ("06-monitoring/02-prometheus-graph.png", "Prometheus — request-rate query"),
      ("06-monitoring/03-grafana-dashboard.png", "Grafana dashboard (live data)"),
      ("06-monitoring/04-kibana-logs.png", "Kibana Discover — grocery logs"),
      ("06-monitoring/05-es-index.png", "Elasticsearch log index")]),

    ("7. Vault — Secrets Management",
     "HashiCorp Vault stores DB credentials / API keys. The app loads its "
     "database URL from Vault at startup instead of from plain config.",
     [("07-vault/01-vault-kv-get.png", "Secret stored in Vault (KV v2)"),
      ("07-vault/02-app-vault-override.png", "App loads DB credentials from Vault"),
      ("07-vault/03-vault-ui.png", "Vault UI")]),
]

TECH = [
    ("Source / VCS", "GitHub + Git"),
    ("Application", "FastAPI (Python), SQLAlchemy"),
    ("Database", "PostgreSQL (SQLite for dev)"),
    ("Containerization", "Docker, docker-compose"),
    ("CI / CD", "Jenkins (declarative pipeline)"),
    ("Infrastructure as Code", "Terraform (local Docker provider)"),
    ("Orchestration", "Kubernetes on kind + HPA"),
    ("Monitoring", "Prometheus + Grafana"),
    ("Logging", "ELK (Elasticsearch, Logstash, Kibana)"),
    ("Secrets", "HashiCorp Vault"),
]


def build_html():
    tech_rows = "".join(
        f"<tr><td class='k'>{k}</td><td>{v}</td></tr>" for k, v in TECH
    )
    sections_html = ""
    for title, desc, shots in SECTIONS:
        figs = "".join(
            f"<figure><img src='{img(p)}'/><figcaption>{c}</figcaption></figure>"
            for p, c in shots
        )
        sections_html += f"""
        <section class="stack">
          <h2>{title}</h2>
          <p class="desc">{desc}</p>
          {figs}
        </section>"""

    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin:0; padding:0; font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; color:#111; }}
    .cover {{ background:#000; color:#fff; height:1122px; padding:90px 70px;
              display:flex; flex-direction:column; justify-content:space-between;
              page-break-after:always; }}
    .cover .top .kick {{ letter-spacing:6px; font-size:13px; color:#bbb; text-transform:uppercase; }}
    .cover h1 {{ font-size:54px; line-height:1.05; margin:18px 0 10px; font-weight:800; }}
    .cover .sub {{ font-size:17px; color:#ccc; max-width:640px; line-height:1.5; }}
    .rule {{ height:3px; width:90px; background:#fff; margin:26px 0; }}
    .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:24px; max-width:680px; }}
    .chip {{ border:1px solid #555; border-radius:20px; padding:6px 14px; font-size:12px; color:#eee; }}
    .meta {{ border-top:1px solid #333; padding-top:24px; }}
    .meta table {{ font-size:15px; color:#eee; border-collapse:collapse; }}
    .meta td {{ padding:4px 0; }}
    .meta td.lbl {{ color:#888; width:150px; letter-spacing:1px; text-transform:uppercase; font-size:12px; }}
    .page {{ padding:55px 60px; }}
    h2 {{ font-size:24px; border-bottom:3px solid #000; padding-bottom:8px; margin:0 0 14px; }}
    h2.big {{ font-size:30px; }}
    p {{ line-height:1.6; font-size:14px; }}
    .desc {{ color:#333; }}
    .ps {{ background:#f3f3f3; border-left:5px solid #000; padding:16px 20px; font-size:15px; line-height:1.65; }}
    table.tech {{ width:100%; border-collapse:collapse; margin-top:10px; font-size:14px; }}
    table.tech td {{ border:1px solid #ddd; padding:9px 12px; }}
    table.tech td.k {{ background:#000; color:#fff; width:230px; font-weight:600; }}
    section.stack {{ page-break-before:always; padding:50px 60px; }}
    figure {{ margin:16px 0 22px; }}
    figure img {{ width:100%; border:1px solid #ccc; }}
    figcaption {{ font-size:12px; color:#555; margin-top:6px; font-style:italic; }}
    ul {{ font-size:14px; line-height:1.7; }}
    </style></head><body>

    <div class="cover">
      <div class="top">
        <div class="kick">ITM Skills University &nbsp;&middot;&nbsp; Case Study Project</div>
        <h1>Grocery Delivery<br/>Platform</h1>
        <div class="sub">A production-style DevOps platform for grocery delivery
          operations — automated deployments, autoscaling, monitoring and
          resilient, fully self-hosted infrastructure.</div>
        <div class="rule"></div>
        <div class="chips">
          {''.join(f"<span class='chip'>{v.split('(')[0].strip()}</span>" for _,v in TECH)}
        </div>
      </div>
      <div class="meta">
        <table>
          <tr><td class="lbl">Name</td><td>Tejas Mhatre</td></tr>
          <tr><td class="lbl">Roll No</td><td>150096724085</td></tr>
          <tr><td class="lbl">Cohort</td><td>Elon Musk</td></tr>
          <tr><td class="lbl">Subject</td><td>DevOps</td></tr>
        </table>
      </div>
    </div>

    <div class="page">
      <h2 class="big">Problem Statement</h2>
      <p><strong>Industry:</strong> E-Commerce</p>
      <div class="ps">The Grocery Delivery Platform is experiencing
        <strong>order processing delays</strong>, <strong>infrastructure
        scalability issues</strong>, <strong>deployment bottlenecks</strong>, and
        <strong>insufficient monitoring capabilities</strong> during peak demand
        periods.</div>

      <h2 style="margin-top:34px">Our Solution</h2>
      <p>We designed and built a complete, production-style DevOps platform that
      runs entirely on <strong>local / self-hosted infrastructure</strong> (Docker,
      kind, Terraform local provider) — no cloud-managed services. Each concern in
      the problem statement is addressed directly:</p>
      <ul>
        <li><strong>Order processing delays</strong> &rarr; FastAPI backend with an
          indexed PostgreSQL store and an explicit order state machine.</li>
        <li><strong>Scalability issues</strong> &rarr; Kubernetes with a Horizontal
          Pod Autoscaler that scales the app 2&rarr;10 pods automatically under load.</li>
        <li><strong>Deployment bottlenecks</strong> &rarr; a Jenkins CI/CD pipeline
          (build, test, image, push, deploy) and reproducible Terraform infrastructure.</li>
        <li><strong>Poor monitoring</strong> &rarr; Prometheus + Grafana metrics,
          the ELK stack for logs, alert rules, and a Disaster Recovery plan.</li>
        <li><strong>Secrets</strong> &rarr; HashiCorp Vault for database credentials
          and API keys, injected into the app at startup.</li>
      </ul>

      <h2 style="margin-top:34px">Technology Stack</h2>
      <table class="tech">{tech_rows}</table>
    </div>

    {sections_html}

    </body></html>"""


def main():
    html = build_html()
    html_path = os.path.join(ROOT, "docs", "_doc.html")
    open(html_path, "w").write(html)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        page = b.new_page()
        page.goto("file://" + html_path, wait_until="networkidle", timeout=120000)
        page.wait_for_timeout(1500)
        page.pdf(path=OUT, format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    print("PDF written:", OUT)


if __name__ == "__main__":
    main()
