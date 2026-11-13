import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_cloud_architecture():
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')

    plt.title("FinFlow Global Systems: Distributed & Multi-Region Cloud Database Topology\n"
              "MIVA Open University | MIT 8103 Advanced Database Systems (Portfolio 5)",
              fontsize=13, fontweight='bold', pad=20, color='#0F172A')

    # Draw Region Containers
    regions = [
        {"name": "PRIMARY REGION: EMEA (eu-west-1, Ireland)", "x": 0.5, "y": 0.8, "w": 4.2, "h": 7.5, "color": "#EFF6FF", "border": "#3B82F6"},
        {"name": "SECONDARY REGION: AMER (us-east-1, N. Virginia)", "x": 5.2, "y": 0.8, "w": 4.2, "h": 7.5, "color": "#F0FDF4", "border": "#22C55E"},
        {"name": "TERTIARY REGION: APAC/AFR (af-south-1, Cape Town)", "x": 9.9, "y": 0.8, "w": 4.2, "h": 7.5, "color": "#FEFCE8", "border": "#EAB308"}
    ]

    for reg in regions:
        rect = patches.FancyBboxPatch(
            (reg["x"], reg["y"]), reg["w"], reg["h"],
            boxstyle="round,pad=0.1,rounding_size=0.2",
            linewidth=1.5, edgecolor=reg["border"], facecolor=reg["color"], linestyle="--"
        )
        ax.add_patch(rect)
        ax.text(reg["x"] + reg["w"]/2, reg["y"] + reg["h"] - 0.4, reg["name"],
                fontsize=8.5, fontweight='bold', ha='center', color='#1E293B')

    # Global Entry Tier
    global_gateway = patches.FancyBboxPatch(
        (3.5, 8.8), 7.6, 0.9, boxstyle="round,pad=0.08,rounding_size=0.15",
        facecolor="#1E293B", edgecolor="#0F172A"
    )
    ax.add_patch(global_gateway)
    ax.text(7.3, 9.25, "GLOBAL ROUTE 53 ANYCAST DNS & CLOUD LOAD BALANCER / API GATEWAY",
            color="white", fontsize=8.5, fontweight='bold', ha='center')

    # Regional Component Generator
    def add_node(x, y, w, h, title, subtext, color, text_color="white"):
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.1",
            facecolor=color, edgecolor="#64748B", linewidth=1.0
        )
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.62, title, color=text_color, fontsize=8, fontweight='bold', ha='center')
        ax.text(x + w/2, y + h*0.28, subtext, color=text_color, fontsize=6.8, ha='center')

    # EMEA Nodes
    add_node(0.9, 6.3, 3.4, 1.1, "Edge Ingress & Shard Router", "Hash Key: MD5(account_id) % N", "#3B82F6")
    add_node(0.9, 4.6, 3.4, 1.2, "PRIMARY AURORA MASTER (RW)", "Active Shard 0 (EMEA Accounts) - LSN Leader", "#1E3A8A")
    add_node(0.9, 3.0, 3.4, 1.1, "Local Read Replica (RO)", "Sub-10ms read query offload", "#60A5FA")
    add_node(0.9, 1.4, 3.4, 1.1, "Redis ElastiCache Cluster", "Idempotency Tokens & Rate Limits (TTL)", "#DC2626")

    # AMER Nodes
    add_node(5.6, 6.3, 3.4, 1.1, "AMER Regional Ingress", "Edge SSL Termination & Router", "#10B981")
    add_node(5.6, 4.6, 3.4, 1.2, "Cross-Region Replica (RO / Failover)", "Active Shard 1 (AMER Accounts)", "#065F46")
    add_node(5.6, 3.0, 3.4, 1.1, "Local Read Replica (RO)", "Bi-directional async log streaming", "#34D399")
    add_node(5.6, 1.4, 3.4, 1.1, "Redis ElastiCache Cluster", "Active-Active Global Datastore", "#DC2626")

    # APAC/AFR Nodes
    add_node(10.3, 6.3, 3.4, 1.1, "APAC/AFR Regional Ingress", "Local Gateway & 2PC Participant", "#F59E0B")
    add_node(10.3, 4.6, 3.4, 1.2, "Cross-Region Replica (RO / Failover)", "Active Shard 2 (AFR/APAC Accounts)", "#B45309")
    add_node(10.3, 3.0, 3.4, 1.1, "Local Read Replica (RO)", "Automated Failover Target (LSN Quorum)", "#FBBF24", text_color="#1E293B")
    add_node(10.3, 1.4, 3.4, 1.1, "Redis ElastiCache Cluster", "Local Read Cache & Token Mirror", "#DC2626")

    # Arrows
    def draw_arrow(x1, y1, x2, y2, color="#2563EB", style="->", label=""):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle=style, color=color, lw=1.5, shrinkA=3, shrinkB=3)
        )
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2, label, fontsize=6.8, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='#CBD5E1', alpha=0.9))

    # Down from global gateway
    draw_arrow(7.3, 8.8, 2.6, 7.5, color="#0F172A", label="EMEA Traffic")
    draw_arrow(7.3, 8.8, 7.3, 7.5, color="#0F172A", label="AMER Traffic")
    draw_arrow(7.3, 8.8, 12.0, 7.5, color="#0F172A", label="APAC/AFR Traffic")

    # Ingress to Primary
    draw_arrow(2.6, 6.3, 2.6, 5.9, color="#1E40AF")
    draw_arrow(2.6, 4.6, 2.6, 4.2, color="#2563EB", label="WAL Stream")
    draw_arrow(2.6, 4.6, 7.3, 5.2, color="#8B5CF6", label="Inter-Region Cross-Shard 2PC & Replication")
    draw_arrow(2.6, 4.6, 12.0, 5.2, color="#8B5CF6")

    # Consensus & Health Monitor Banner
    ax.text(7.3, 0.4, "PACELC Tradeoff: PC/EC for Core Double-Entry Ledger | PA/EL for Transaction Event Feeds & Telemetry\n"
                      "RPO (Recovery Point Objective) = 0 | RTO (Recovery Time Objective) < 3.0 Seconds (Automated Quorum Failover)",
            fontsize=8.5, ha='center', va='center', color='#0F172A', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F1F5F9', edgecolor='#94A3B8'))

    ax.set_xlim(0, 14.6)
    ax.set_ylim(0, 10)
    ax.axis('off')

    plt.tight_layout()
    chart_path = 'advanced-database-portfolio/portfolio-5-distributed-cloud/architecture_diagram.png'
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    print(f"Cloud Architecture Diagram generated: {chart_path}")

if __name__ == "__main__":
    draw_cloud_architecture()
