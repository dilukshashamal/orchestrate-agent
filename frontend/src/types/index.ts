export type StockoutRiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ExceptionSeverity = 'CRITICAL' | 'WARNING' | 'INFO';
export type POStatus = 'PENDING' | 'APPROVED' | 'EXPEDITED' | 'DELAYED' | 'IN_TRANSIT' | 'DELIVERED' | 'CANCELLED' | 'AUTO_EXECUTED';

export interface DecisionFactor {
  factor_name: string;
  observed_value: string;
  rule_threshold: string;
  status: 'PASSED' | 'CRITICAL' | 'APPROVAL_REQUIRED' | 'AUTO_APPROVED' | 'HEALTHY' | 'NORMAL' | 'VERIFIED' | 'UNVERIFIED';
  impact: string;
}

export interface ExceptionCase {
  id: string;
  po_number: string;
  item_sku: string;
  item_name: string;
  supplier_id: string;
  supplier_name: string;
  delay_days: number;
  on_hand_qty: number;
  daily_usage_rate: number;
  stockout_countdown_days: number;
  stockout_risk: StockoutRiskLevel;
  purchase_value: number;
  po_status: POStatus;
  requires_human_approval: boolean;
  disruption_flagged: boolean;
  severity: ExceptionSeverity;
  decision_reasons: string[];
  rule_actions: {
    disruption_rule: string;
    purchase_approval_rule: string;
  };
  last_updated: string;
}

export interface AlternativeSupplier {
  id: string;
  name: string;
  rating: number;
  lead_time_days: number;
  unit_price: number;
  capacity_units_per_week: number;
  is_preapproved: boolean;
  location: string;
  contact_email: string;
  is_viable?: boolean;
  lead_time_delta_days?: number;
  price_delta?: number;
}

export interface WorkflowStateSnapshot {
  current_step?: string;
  approval_status?: string;
  requires_human_approval?: boolean;
  history?: string[];
  monitoring_result?: any;
  impact_analysis?: any;
  supplier_intelligence?: any;
  logistics_recommendations?: any;
  procurement_plan?: any;
}

export interface ExceptionDetail {
  id: string;
  po_data: any;
  inventory_data: any;
  primary_supplier: any;
  stockout_countdown_days: number;
  stockout_risk: StockoutRiskLevel;
  disruption_evaluation: any;
  purchase_approval_evaluation: any;
  decision_factors: DecisionFactor[];
  langgraph_workflow: WorkflowStateSnapshot;
  alternative_suppliers: AlternativeSupplier[];
}

export interface DashboardSummary {
  active_exceptions: number;
  pending_approvals: number;
  auto_executed: number;
  at_risk_capital: number;
  critical_stockouts: number;
  telemetry_status: string;
  telemetry_stream: Array<{
    id: string;
    timestamp: string;
    agent: string;
    message: string;
    severity: 'CRITICAL' | 'WARNING' | 'INFO' | 'SUCCESS';
  }>;
  last_telemetry_scan: string;
}
