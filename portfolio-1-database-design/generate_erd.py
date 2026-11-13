import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_erd():
    fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("#F8FAFC")
    
    # Title and Case Study Header
    plt.title("FinFlow Global Payment Systems - Relational Database Entity-Relationship Diagram (ERD)\n"
              "MIVA Open University | MIT 8103 Advanced Database Systems (Portfolio 1)",
              fontsize=14, fontweight="bold", pad=20, color="#0F172A")
    
    entities = [
        {
            "name": "CUSTOMERS",
            "x": 0.5, "y": 7.0, "w": 3.0, "h": 2.8,
            "header_color": "#1E40AF",
            "attrs": [
                "PK customer_id (UUID)",
                "   first_name VARCHAR(50)",
                "   last_name VARCHAR(50)",
                "UQ email VARCHAR(100)",
                "UQ phone_number VARCHAR(25)",
                "   kyc_tier INT (1-3)",
                "   country_code CHAR(3)",
                "   status VARCHAR(20)",
                "   created_at TIMESTAMP"
            ]
        },
        {
            "name": "CURRENCY_REGISTRY",
            "x": 4.5, "y": 7.5, "w": 3.0, "h": 2.2,
            "header_color": "#065F46",
            "attrs": [
                "PK currency_code CHAR(3)",
                "   currency_name VARCHAR(50)",
                "   symbol VARCHAR(5)",
                "   decimal_precision INT",
                "   is_active INT"
            ]
        },
        {
            "name": "EXCHANGE_RATES",
            "x": 8.5, "y": 7.5, "w": 3.0, "h": 2.2,
            "header_color": "#047857",
            "attrs": [
                "PK rate_id INTEGER",
                "FK base_currency CHAR(3)",
                "FK target_currency CHAR(3)",
                "   rate DECIMAL(18,6)",
                "   effective_timestamp TIME"
            ]
        },
        {
            "name": "ACCOUNTS (WALLETS)",
            "x": 0.5, "y": 3.2, "w": 3.2, "h": 3.2,
            "header_color": "#2563EB",
            "attrs": [
                "PK account_id (UUID)",
                "FK customer_id (UUID)",
                "UQ account_number VARCHAR(20)",
                "   account_type VARCHAR(25)",
                "FK currency_code CHAR(3)",
                "   balance DECIMAL(18,4)",
                "   locked_balance DECIMAL",
                "   daily_transfer_limit",
                "   status VARCHAR(20)",
                "   version INT (for OCC)"
            ]
        },
        {
            "name": "MERCHANTS",
            "x": 4.5, "y": 4.2, "w": 3.0, "h": 2.5,
            "header_color": "#7C3AED",
            "attrs": [
                "PK merchant_id (UUID)",
                "FK customer_id (UUID)",
                "   business_name VARCHAR(100)",
                "   merchant_cat_code CHAR(4)",
                "FK settlement_account_id",
                "   commission_rate DECIMAL",
                "   status VARCHAR(20)"
            ]
        },
        {
            "name": "TRANSACTIONS",
            "x": 8.5, "y": 2.8, "w": 3.4, "h": 3.8,
            "header_color": "#B91C1C",
            "attrs": [
                "PK transaction_id (UUID)",
                "UQ idempotency_key VARCHAR(64)",
                "FK source_account_id (UUID)",
                "FK destination_account_id",
                "FK merchant_id (UUID, NULL)",
                "   transaction_type VARCHAR",
                "FK source_currency CHAR(3)",
                "   source_amount DECIMAL",
                "FK destination_currency",
                "   destination_amount",
                "   exchange_rate_applied",
                "   status (PENDING/COMPLETED)",
                "   risk_score DECIMAL"
            ]
        },
        {
            "name": "LEDGER_ENTRIES",
            "x": 4.5, "y": 0.5, "w": 3.0, "h": 2.8,
            "header_color": "#C2410C",
            "attrs": [
                "PK entry_id INTEGER (AUTO)",
                "FK transaction_id (UUID)",
                "FK account_id (UUID)",
                "   entry_type (DEBIT/CREDIT)",
                "   amount DECIMAL(18,4)",
                "FK currency_code CHAR(3)",
                "   balance_after DECIMAL",
                "   entry_timestamp TIME"
            ]
        },
        {
            "name": "AML_RISK_ALERTS",
            "x": 8.5, "y": 0.2, "w": 3.4, "h": 2.1,
            "header_color": "#991B1B",
            "attrs": [
                "PK alert_id INTEGER (AUTO)",
                "FK transaction_id (UUID)",
                "   rule_code VARCHAR(50)",
                "   severity (LOW-CRITICAL)",
                "   flagged_amount DECIMAL",
                "   status (OPEN/CLEARED)"
            ]
        }
    ]
    
    for e in entities:
        rect = patches.FancyBboxPatch(
            (e["x"], e["y"]), e["w"], e["h"],
            boxstyle="round,pad=0.06,rounding_size=0.15",
            linewidth=1.2, edgecolor="#CBD5E1", facecolor="#FFFFFF"
        )
        ax.add_patch(rect)
        
        header_h = 0.5
        header_rect = patches.FancyBboxPatch(
            (e["x"], e["y"] + e["h"] - header_h), e["w"], header_h,
            boxstyle="round,pad=0.06,rounding_size=0.1",
            linewidth=0, facecolor=e["header_color"]
        )
        ax.add_patch(header_rect)
        
        ax.text(e["x"] + e["w"]/2, e["y"] + e["h"] - header_h/2, e["name"],
                color="white", fontsize=9, fontweight="bold", ha="center", va="center")
        
        attr_text = "\n".join(e["attrs"])
        ax.text(e["x"] + 0.15, e["y"] + e["h"] - header_h - 0.2, attr_text,
                color="#1E293B", fontsize=7.5, va="top", fontfamily="monospace", linespacing=1.3)

    def draw_relation(x1, y1, x2, y2, label="", color="#64748B"):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.3, shrinkA=5, shrinkB=5)
        )
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my, label, fontsize=7, color="#475569",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#F1F5F9", edgecolor="none", alpha=0.9))

    draw_relation(2.0, 7.0, 2.0, 6.4, "1 : N (owns accounts)")
    draw_relation(3.5, 8.0, 4.5, 5.5, "1 : N (registers merchant)")
    draw_relation(4.5, 8.2, 3.7, 5.8, "1 : N (currency)")
    draw_relation(7.5, 8.5, 8.5, 8.5, "FX pairs")
    draw_relation(3.7, 4.8, 8.5, 4.8, "1 : N (source/dest)")
    draw_relation(6.0, 4.2, 8.5, 3.5, "1 : N (merchant checkout)")
    draw_relation(10.2, 2.8, 6.5, 2.0, "1 : 2+ (ledger entries)")
    draw_relation(10.2, 2.8, 10.2, 2.3, "1 : N (AML alerts)")

    ax.set_xlim(-0.2, 12.5)
    ax.set_ylim(-0.2, 10.5)
    ax.axis("off")
    
    plt.tight_layout()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(base_dir, "schema_diagram.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"ER Diagram generated successfully: {out_file}")

if __name__ == "__main__":
    generate_erd()
