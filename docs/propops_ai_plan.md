# PropOps AI (Kenya Edition) Strategic Overview

## 1. Localized Value Proposition
- *"Kenya’s first AI-powered property operations platform that unites rent collection, Airbnb oversight, tenant management, and compliance in one dashboard — built by Kenyans, for Kenya."*
- Differentiators vs. PMS.co.ke, EazzyRent, etc.:
  - AI-driven automation covering reminders, anomaly detection, predictive maintenance, and smart rent forecasting.
  - Integrated M-Pesa payments and Airbnb performance analytics.
  - Local compliance intelligence for rent tribunal rules, KRA obligations, eCitizen property searches, and localized lease templates.

## 2. MVP Feature Priorities (Lean Build)
| Priority | Module | Description |
| --- | --- | --- |
| 🟢 Must-Have | Property Dashboard | Add/manage properties & tenants (long-term & Airbnb) |
| 🟢 Must-Have | Rent Collection & Accounting | Auto invoices, receipts, M-Pesa integration, arrears tracker |
| 🟢 Must-Have | Tenant & Guest CRM | Store tenant data, lease dates, maintenance requests |
| 🟡 Should-Have | Automated Messaging | SMS/WhatsApp rent reminders, check-in/out messages |
| 🟡 Should-Have | Compliance Center | Legal templates, reminders for KRA filings, NEMA updates |
| ⚪ Nice-to-Have | AI Assistant | Summaries, delinquency forecasting, tenant replies |
| ⚪ Nice-to-Have | Vendor Portal | Maintenance teams receive and close work orders |

## 3. Stack Recommendation (Low Cost, Build-It-Yourself Friendly)
| Function | Recommended Tool | Notes |
| --- | --- | --- |
| Backend & Database | Supabase or Firebase | Free-tier, scalable backend options |
| Frontend / UI | Bubble, Glide, or Next.js + Tailwind | Bubble enables the fastest no-code MVP |
| Payments | M-Pesa Daraja API | Direct integration for Kenyan market |
| AI Layer | OpenAI GPT-4 API | Powers automations, summaries, forecasts |
| Messaging | Twilio or WhatsApp Cloud API | Automated reminders & notifications |
| Hosting / Domain | Vercel or Render | Low/no-cost deployment |
| Auth / Login | Clerk.dev or Firebase Auth | Secure tenant/landlord sign-ins |

*Estimated initial monthly cost: < KES 5,000 (≈ $40).* 

## 4. Kenya Pricing Model (Local Purchasing Power)
| Plan | Target | Price (KES/month) | Description |
| --- | --- | --- | --- |
| Starter | 1–10 Units or 2 Airbnb Listings | 1,500 | Core dashboard, invoices, receipts |
| Professional | 11–50 Units | 3,500 | Starter + compliance & messaging automation |
| Enterprise | 51–200 Units | 7,500 | Professional + AI assistant, analytics |
| Custom / Corporate | 200+ | Negotiated | SLA support, multi-agent access |

Free Tier: Manage 1 property + 1 tenant for free to support top-of-funnel marketing.

## 5. Launch Roadmap
**Phase 1 — Prototype & Pilot (0–3 months)**
- Build MVP on Bubble/Glide.
- Onboard 5–10 friendly Airbnb hosts as pilot users.
- Validate rent reminder, receipt, and dashboard workflows.
- Gather testimonials.

**Phase 2 — Public Beta (3–6 months)**
- Launch landing page (e.g., propops.ai by Perlin Ventures).
- Add WhatsApp-based customer support bot.
- Introduce three subscription tiers.
- Run targeted Facebook/Instagram ads for Kenyan landlords, property managers, and Airbnb hosts.

**Phase 3 — Growth (6–12 months)**
- Integrate KRA auto-reminders and eCitizen search API access.
- Partner with legal/accounting firms for compliance content.
- Add AI features (performance summaries, predictive arrears, messaging support).
- Expand to property agents in Nairobi and Mombasa.

## 6. Revenue & Scaling Projection (Lean Model)
| Metric | Month 6 | Month 12 |
| --- | --- | --- |
| Paying users | 50 | 200 |
| Average revenue / user (KES) | 3,000 | 3,500 |
| MRR (KES) | 150,000 | 700,000 |
| CAC (avg) | 2,000 | 1,000 |
| Churn | 6% | 4% |

Break-even expected by months 10–12 with organic growth and limited marketing spend.

## 7. Branding under Perlin Ventures
- Parent company: Perlin Ventures; SaaS product: PropOps AI.
- Brand tone: Modern, professional, Pan-African, minimalist.
- Visual direction:
  - Colours: Deep green, gold, slate grey.
  - Fonts: Inter or Poppins.
  - Logo concept: Stylised building combined with circuitry to represent tech-enabled property operations.
