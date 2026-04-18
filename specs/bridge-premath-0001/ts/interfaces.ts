export type CoherenceLevel = "Set" | "Gpd" | "Cat" | "S_infinity";
export type Mode = "normal" | "degraded" | "safe" | "burn" | "restoring";
export type ChartId = "bridge" | "secret-core" | "materialization" | "provider-plane" | "audit";

export interface PremathContext {
  version: "bridge-premath-0001-0.1";
  context_id: string;
  coherence_level: CoherenceLevel;
  request: {
    request_id: string;
    trace: string;
    witness_jti: string;
    witness_type: string;
    requested_tool: string;
    requested_resource: string;
    source_domain: string;
    destination_domain: string;
    subject_id: string;
    act_for?: string;
    consumer_kind: string;
    consumer_id: string;
  };
  interpretation: {
    foreign_observation_id: string;
    source_context_id: string;
    interpretation_binding_id?: string;
    typed_observation_id?: string;
    interpretation_status: "admitted" | "unknown" | "ambiguous" | "stale";
  };
  secret: {
    secret_id: string;
    secret_class: string;
    version_selector?: string;
    version_id?: string;
    secret_epoch?: number | string;
    bridge_binding_required?: boolean;
  };
  resource_secret_binding: {
    binding_id: string;
    resource_basis: string;
    requested_resource: string;
    secret_id: string;
    backend_profile_id: string;
    materializer_profile_id: string;
    issuance_mode: string;
  };
  policy: {
    requested_method: string;
    requested_ttl_s: number;
    mode: Mode;
    conf_level: string;
    compartments?: string[];
    integ_level: string;
    non_exportable: boolean;
    direct_model_access_prohibited: boolean;
  };
  provider_facts: {
    deployment_profile_id: string;
    provider_catalog_id: string;
    time_source_id: string;
    authoritative_now: string;
    attestation_id: string;
    posture_digest: string;
    revocation_snapshot_id: string;
    issuer_epoch: number | string;
    mode_controller_id: string;
    mode_epoch: number | string;
    audit_sink_id: string;
    facts_fresh_until?: string;
  };
  binding: {
    binding_id: string;
    backend_profile_id: string;
    materializer_profile_id: string;
    allowed_actions?: string[];
    allowed_modes?: string[];
    non_exportable?: boolean;
  };
  audit: {
    stream_id: string;
    last_sequence: number;
    last_event_hash: string;
    checkpoint_source_id?: string;
    payload_hash?: string;
  };
  charts: ChartId[];
  notes?: string;
}

export interface ContextMorphism {
  version: "bridge-premath-0001-0.1";
  morphism_id: string;
  domain_context_id: string;   // narrower context Γ'
  codomain_context_id: string; // broader context Γ
  operations: Array<{
    op:
      | "tighten_request_scope"
      | "reduce_ttl"
      | "tighten_conf_label"
      | "tighten_integ_label"
      | "select_secret_version"
      | "restrict_binding"
      | "narrow_allowed_modes"
      | "refresh_facts"
      | "advance_mode_to_safe"
      | "advance_mode_to_burn"
      | "prefix_audit_stream"
      | "project_chart";
    chart_id?: ChartId;
    before?: unknown;
    after?: unknown;
    note?: string;
  }>;
  invariants: {
    authority_not_widened: true;
    ttl_nonincreasing: true;
    freshness_nonstale: true;
    burn_monotone: true;
    plaintext_not_globalized: true;
  };
  notes?: string;
}

export interface RequestOverlap {
  trace: string;
  request_id: string;
  witness_jti: string;
  requested_tool: string;
  requested_resource: string;
  source_domain: string;
  destination_domain: string;
  subject_id: string;
  act_for: string;
  consumer_kind: string;
  consumer_id: string;
}

export interface SecretOverlap {
  secret_id: string;
  secret_class: string;
  version_selector?: string;
  version_id?: string;
  secret_epoch?: number | string;
  binding_id: string;
  requested_resource: string;
  backend_profile_id: string;
  materializer_profile_id: string;
}

export interface PolicyOverlap {
  requested_method: string;
  requested_ttl_s: number;
  mode: Mode;
  conf_level: string;
  integ_level: string;
  non_exportable: boolean;
  direct_model_access_prohibited: boolean;
}

export interface FactsOverlap {
  deployment_profile_id: string;
  provider_catalog_id: string;
  attestation_id: string;
  posture_digest: string;
  revocation_snapshot_id: string;
  issuer_epoch: number | string;
  mode_epoch: number | string;
  audit_sink_id: string;
}

export interface AuditOverlap {
  trace: string;
  stream_id: string;
  sequence: number;
  payload_hash: string;
  prev_event_hash: string;
  event_hash: string;
}

export interface BridgeSection {
  trace: string;
  witness_jti: string;
  decision_effect: "allow" | "deny" | "burn";
  effective_ttl_s?: number;
  policy_input_hash?: string;
}

export interface SecretCoreSection {
  secret_id: string;
  secret_class: string;
  version_id?: string;
  lifecycle_state: string;
}

export interface MaterializationSection {
  binding_id: string;
  session_id?: string;
  session_state: string;
  issued_ttl_s?: number;
}

export interface ProviderPlaneSection {
  deployment_profile_id: string;
  provider_decision_status: "accept" | "deny" | "burn";
  attestation_id?: string;
  revocation_snapshot_id?: string;
}

export interface AuditSection {
  stream_id: string;
  sequence: number;
  event_hash: string;
}

export interface CompatibilityWitness {
  version: "bridge-premath-0001-0.1";
  witness_id: string;
  request_coherent: boolean;
  secret_seam_coherent: boolean;
  policy_monotone: boolean;
  authority_is_meet: boolean;
  provider_facts_coherent: boolean;
  lifecycle_coherent: boolean;
  burn_dominates: boolean;
  audit_before_allow: boolean;
  no_plaintext_global: boolean;
  notes?: string[];
}

export interface GluedBundle {
  version: "bridge-premath-0001-0.1";
  bundle_id: string;
  context_ref: string;
  overlaps: {
    request: RequestOverlap;
    secret: SecretOverlap;
    policy: PolicyOverlap;
    facts: FactsOverlap;
    audit: AuditOverlap;
  };
  local_sections: {
    bridge: BridgeSection;
    secret_core: SecretCoreSection;
    materialization: MaterializationSection;
    provider_plane: ProviderPlaneSection;
    audit: AuditSection;
  };
  compatibility_witness: CompatibilityWitness;
  laws: {
    pullback_stable: boolean;
    descent_claimed: boolean;
    plaintext_global_section_absent: boolean;
  };
  notes?: string;
}

export interface RestrictionAlgebra {
  restrictContext(context: PremathContext, f: ContextMorphism): PremathContext;
  requestOverlap(context: PremathContext): RequestOverlap;
  secretOverlap(context: PremathContext): SecretOverlap;
  policyOverlap(context: PremathContext): PolicyOverlap;
  factsOverlap(context: PremathContext): FactsOverlap;
  auditOverlap(context: PremathContext): AuditOverlap;

  restrictBridge(section: BridgeSection, f: ContextMorphism): BridgeSection;
  restrictSecretCore(section: SecretCoreSection, f: ContextMorphism): SecretCoreSection;
  restrictMaterialization(section: MaterializationSection, f: ContextMorphism): MaterializationSection;
  restrictProviderPlane(section: ProviderPlaneSection, f: ContextMorphism): ProviderPlaneSection;
  restrictAudit(section: AuditSection, f: ContextMorphism): AuditSection;
}

export interface GlueAlgebra {
  deriveCompatibility(args: {
    context: PremathContext;
    bridge: BridgeSection;
    secret_core: SecretCoreSection;
    materialization: MaterializationSection;
    provider_plane: ProviderPlaneSection;
    audit: AuditSection;
  }): CompatibilityWitness;

  glue(args: {
    context: PremathContext;
    bridge: BridgeSection;
    secret_core: SecretCoreSection;
    materialization: MaterializationSection;
    provider_plane: ProviderPlaneSection;
    audit: AuditSection;
    witness: CompatibilityWitness;
  }): GluedBundle;
}

export interface Cover {
  context_id: string;
  charts: ChartId[];
}

export interface DescentCheck {
  cover: Cover;
  compatible: boolean;
  contractible: boolean;
  notes?: string[];
}
