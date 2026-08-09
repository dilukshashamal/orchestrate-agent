import { ExceptionCase, ExceptionDetail, DashboardSummary } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Rich fallback data for immediate visual demo rendering
const FALLBACK_SUMMARY: DashboardSummary = {
  active_exceptions: 1,
  pending_approvals: 1,
  auto_executed: 2,
  at_risk_capital: 60000.0,
  critical_stockouts: 1,
  telemetry_status: 'ONLINE',
  telemetry_stream: [
    {
      id: 'EVT-101',
      timestamp: 'Just now',
      agent: 'MonitoringAgent',
      message: 'Flagged 5-day delay on PO-9001 from Titan Semiconductor Corp (MAT-101).',
      severity: 'CRITICAL'
    },
    {
      id: 'EVT-102',
      timestamp: '2 mins ago',
      agent: 'ImpactAnalysisAgent',
      message: 'Stockout countdown calculated at 4.8 days (< 7d threshold). Stockout risk escalated to HIGH.',
      severity: 'CRITICAL'
    },
    {
      id: 'EVT-103',
      timestamp: '5 mins ago',
      agent: 'SupplierIntelAgent',
      message: 'Evaluated alternative supplier Apex Global Microelectronics (Lead time: 5 days, Rating: 4.6).',
      severity: 'INFO'
    },
    {
      id: 'EVT-104',
      timestamp: '8 mins ago',
      agent: 'ProcurementAgent',
      message: 'PO value $60,000 exceeds $50,000 rule engine threshold. Created human approval request.',
      severity: 'WARNING'
    },
    {
      id: 'EVT-105',
      timestamp: '15 mins ago',
      agent: 'RulesEngine',
      message: 'Auto-executed PO-9002 ($6,750 < $10k preapproved limit).',
      severity: 'SUCCESS'
    }
  ],
  last_telemetry_scan: new Date().toISOString()
};

const FALLBACK_EXCEPTIONS: ExceptionCase[] = [
  {
    id: 'EXC-PO-9001',
    po_number: 'PO-9001',
    item_sku: 'MAT-101',
    item_name: 'Microprocessor X100',
    supplier_id: 'SUP-001',
    supplier_name: 'Titan Semiconductor Corp',
    delay_days: 5,
    on_hand_qty: 120,
    daily_usage_rate: 25,
    stockout_countdown_days: 4,
    stockout_risk: 'HIGH',
    purchase_value: 60000.0,
    po_status: 'DELAYED',
    requires_human_approval: true,
    disruption_flagged: true,
    severity: 'CRITICAL',
    decision_reasons: [
      'Supplier delay of 5 days exceeds 3-day threshold with HIGH stockout risk.',
      'Purchase value of $60,000.00 exceeds human approval threshold of $50,000.'
    ],
    rule_actions: {
      disruption_rule: 'CREATE_EXCEPTION_CASE',
      purchase_approval_rule: 'HUMAN_APPROVAL_REQUIRED'
    },
    last_updated: new Date().toISOString()
  },
  {
    id: 'EXC-PO-9002',
    po_number: 'PO-9002',
    item_sku: 'MAT-101',
    item_name: 'Microprocessor X100',
    supplier_id: 'SUP-002',
    supplier_name: 'Apex Global Microelectronics',
    delay_days: 0,
    on_hand_qty: 120,
    daily_usage_rate: 25,
    stockout_countdown_days: 4,
    stockout_risk: 'HIGH',
    purchase_value: 6750.0,
    po_status: 'PENDING',
    requires_human_approval: false,
    disruption_flagged: false,
    severity: 'INFO',
    decision_reasons: [
      'Disruption criteria (delay > 3 days AND HIGH stockout risk) not met.',
      'Purchase value of $6,750.00 is under $10,000 threshold with a preapproved supplier.'
    ],
    rule_actions: {
      disruption_rule: 'NO_ACTION',
      purchase_approval_rule: 'AUTO_CREATE_PO'
    },
    last_updated: new Date().toISOString()
  },
  {
    id: 'EXC-PO-9003',
    po_number: 'PO-9003',
    item_sku: 'MAT-102',
    item_name: 'Polymer Casing Mold B',
    supplier_id: 'SUP-003',
    supplier_name: 'Pacific Polymer Industries',
    delay_days: 1,
    on_hand_qty: 1500,
    daily_usage_rate: 50,
    stockout_countdown_days: 30,
    stockout_risk: 'LOW',
    purchase_value: 18000.0,
    po_status: 'IN_TRANSIT',
    requires_human_approval: true,
    disruption_flagged: false,
    severity: 'WARNING',
    decision_reasons: [
      'Disruption criteria not met.',
      'Purchase value of $18,000.00 requires human review (not preapproved or above $10,000).'
    ],
    rule_actions: {
      disruption_rule: 'NO_ACTION',
      purchase_approval_rule: 'HUMAN_APPROVAL_REQUIRED'
    },
    last_updated: new Date().toISOString()
  }
];

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  try {
    const res = await fetch(`${API_BASE}/dashboard/summary`, { cache: 'no-store' });
    if (!res.ok) throw new Error('API Error');
    return await res.json();
  } catch {
    return FALLBACK_SUMMARY;
  }
}

export async function fetchExceptions(severity?: string): Promise<ExceptionCase[]> {
  try {
    const url = severity ? `${API_BASE}/workflows/exceptions?severity=${severity}` : `${API_BASE}/workflows/exceptions`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('API Error');
    return await res.json();
  } catch {
    if (severity) {
      return FALLBACK_EXCEPTIONS.filter(e => e.severity.toUpperCase() === severity.toUpperCase());
    }
    return FALLBACK_EXCEPTIONS;
  }
}

export async function fetchExceptionDetail(exceptionId: string): Promise<ExceptionDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/workflows/exceptions/${exceptionId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('API Error');
    return await res.json();
  } catch {
    // Generate fallback detailed object
    const exc = FALLBACK_EXCEPTIONS.find(e => e.id === exceptionId) || FALLBACK_EXCEPTIONS[0];
    return {
      id: exc.id,
      po_data: {
        po_number: exc.po_number,
        supplier_id: exc.supplier_id,
        item_sku: exc.item_sku,
        quantity: 500,
        unit_price: 120.0,
        total_value: exc.purchase_value,
        status: exc.po_status,
        actual_delay_days: exc.delay_days
      },
      inventory_data: {
        sku: exc.item_sku,
        name: exc.item_name,
        on_hand_qty: exc.on_hand_qty,
        daily_usage_rate: exc.daily_usage_rate
      },
      primary_supplier: {
        id: exc.supplier_id,
        name: exc.supplier_name,
        rating: 4.8,
        is_preapproved: true,
        location: 'Hsinchu, Taiwan'
      },
      stockout_countdown_days: exc.stockout_countdown_days,
      stockout_risk: exc.stockout_risk,
      disruption_evaluation: {
        action: exc.rule_actions.disruption_rule,
        reason: exc.decision_reasons[0],
        requires_human_approval: false
      },
      purchase_approval_evaluation: {
        action: exc.rule_actions.purchase_approval_rule,
        reason: exc.decision_reasons[1],
        requires_human_approval: exc.requires_human_approval
      },
      decision_factors: [
        {
          factor_name: 'Supplier Transit Delay',
          observed_value: `${exc.delay_days} days`,
          rule_threshold: '> 3 days',
          status: exc.delay_days > 3 ? 'PASSED' : 'NORMAL',
          impact: exc.delay_days > 3 ? 'Triggered exception case creation' : 'Within tolerance'
        },
        {
          factor_name: 'Stockout Countdown',
          observed_value: `${exc.stockout_countdown_days} days (${exc.on_hand_qty} units on-hand / ${exc.daily_usage_rate} daily usage)`,
          rule_threshold: '< 7 days (HIGH severity)',
          status: exc.stockout_countdown_days < 7 ? 'CRITICAL' : 'HEALTHY',
          impact: `Stockout severity assessed as ${exc.stockout_risk}`
        },
        {
          factor_name: 'PO Financial Value',
          observed_value: `$${exc.purchase_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
          rule_threshold: '> $50,000 (Human Approval Limit)',
          status: exc.requires_human_approval ? 'APPROVAL_REQUIRED' : 'AUTO_APPROVED',
          impact: exc.decision_reasons[1]
        },
        {
          factor_name: 'Supplier Preapproval',
          observed_value: 'PREAPPROVED',
          rule_threshold: 'Required for auto PO creation under $10,000',
          status: 'VERIFIED',
          impact: `Supplier ${exc.supplier_name} preapproval verification status`
        }
      ],
      langgraph_workflow: {
        current_step: 'procurement_node',
        approval_status: exc.requires_human_approval ? 'PENDING' : 'AUTO_EXECUTED',
        requires_human_approval: exc.requires_human_approval,
        history: [
          'monitoring_node: completed disruption detection',
          'impact_analysis_node: completed stockout impact calculation',
          'supplier_intelligence_node: evaluated alternative suppliers',
          'logistics_node: evaluated freight options',
          'procurement_node: evaluated policy compliance & approval requirements'
        ],
        monitoring_result: {
          disruption_flagged: true,
          supplier_delay_days: exc.delay_days,
          rule_action: 'CREATE_EXCEPTION_CASE'
        },
        impact_analysis: {
          stockout_countdown_days: exc.stockout_countdown_days,
          evaluated_stockout_risk: exc.stockout_risk,
          production_impact: 'HIGH'
        },
        supplier_intelligence: {
          alternative_supplier_available: true,
          best_alternative: {
            id: 'SUP-002',
            name: 'Apex Global Microelectronics',
            rating: 4.6,
            lead_time_days: 5,
            unit_price: 135.0,
            is_preapproved: true,
            location: 'Austin, TX, USA'
          }
        },
        logistics_recommendations: {
          recommended_mode: 'AIR',
          carrier_name: 'Vanguard Express Air',
          estimated_transit_days: 2,
          estimated_cost: 3200.0
        },
        procurement_plan: {
          recommended_action: exc.requires_human_approval ? 'HUMAN_APPROVAL_REQUIRED' : 'AUTO_CREATE_PO',
          requires_human_approval: exc.requires_human_approval,
          reason: exc.decision_reasons[1]
        }
      },
      alternative_suppliers: [
        {
          id: 'SUP-002',
          name: 'Apex Global Microelectronics',
          rating: 4.6,
          lead_time_days: 5,
          unit_price: 135.0,
          capacity_units_per_week: 2000,
          is_preapproved: true,
          location: 'Austin, TX, USA',
          contact_email: 'supply@apexmicro.com',
          is_viable: true,
          lead_time_delta_days: -9,
          price_delta: 15.0
        },
        {
          id: 'SUP-004',
          name: 'Vanguard Logistics & Components',
          rating: 4.9,
          lead_time_days: 3,
          unit_price: 150.0,
          capacity_units_per_week: 1500,
          is_preapproved: true,
          location: 'Frankfurt, Germany',
          contact_email: 'expedite@vanguardcomp.de',
          is_viable: true,
          lead_time_delta_days: -11,
          price_delta: 30.0
        }
      ]
    };
  }
}

export async function submitApprovalDecision(exceptionId: string, decision: 'APPROVED' | 'REJECTED', notes?: string) {
  try {
    const res = await fetch(`${API_BASE}/workflows/approvals/${exceptionId}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, reviewer_notes: notes })
    });
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch {
    return {
      exception_id: exceptionId,
      decision,
      status: decision === 'APPROVED' ? 'EXPEDITED' : 'CANCELLED',
      message: 'Decision logged (offline mode).'
    };
  }
}

export async function submitBulkPreapprove() {
  try {
    const res = await fetch(`${API_BASE}/workflows/approvals/bulk-preapprove`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch {
    return {
      auto_executed_count: 1,
      message: 'Auto-executed low-risk preapproved orders (offline mode).'
    };
  }
}

export async function triggerWorkflowRun(poNumber: string = 'PO-9001') {
  try {
    const res = await fetch(`${API_BASE}/workflows/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ po_number: poNumber })
    });
    if (!res.ok) throw new Error('API error');
    return await res.json();
  } catch {
    return {
      status: 'COMPLETED',
      message: `Simulated LangGraph workflow run for ${poNumber}`
    };
  }
}
