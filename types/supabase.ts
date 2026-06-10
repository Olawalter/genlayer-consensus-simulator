export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

type Relationship = {
  foreignKeyName: string;
  columns: string[];
  isOneToOne?: boolean;
  referencedRelation: string;
  referencedColumns: string[];
};

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          username: string;
          role: string;
          xp: number;
          created_at: string;
        };
        Insert: {
          id: string;
          username: string;
          role?: string;
          xp?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          username?: string;
          role?: string;
          xp?: number;
        };
        Relationships: Relationship[];
      };
      claims: {
        Row: {
          id: string;
          user_id: string | null;
          content: string;
          category: string;
          metadata: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          content: string;
          category: string;
          metadata?: Json | null;
          created_at?: string;
        };
        Update: {
          content?: string;
          category?: string;
          metadata?: Json | null;
        };
        Relationships: Relationship[];
      };
      simulations: {
        Row: {
          id: string;
          claim_id: string;
          user_id: string | null;
          status: string;
          validator_count: number;
          consensus_reached: boolean | null;
          final_verdict: string | null;
          contract_address: string | null;
          tx_hash: string | null;
          chain_data: Json | null;
          created_at: string;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          claim_id: string;
          user_id?: string | null;
          status?: string;
          validator_count?: number;
          consensus_reached?: boolean | null;
          final_verdict?: string | null;
          contract_address?: string | null;
          tx_hash?: string | null;
          chain_data?: Json | null;
          created_at?: string;
          completed_at?: string | null;
        };
        Update: {
          status?: string;
          consensus_reached?: boolean | null;
          final_verdict?: string | null;
          tx_hash?: string | null;
          chain_data?: Json | null;
          completed_at?: string | null;
        };
        Relationships: Relationship[];
      };
      validators: {
        Row: {
          id: string;
          name: string;
          model: string;
          persona: string;
          bias_profile: Json | null;
          is_active: boolean;
          created_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          model: string;
          persona: string;
          bias_profile?: Json | null;
          is_active?: boolean;
          created_at?: string;
        };
        Update: {
          name?: string;
          model?: string;
          persona?: string;
          bias_profile?: Json | null;
          is_active?: boolean;
        };
        Relationships: Relationship[];
      };
      validator_votes: {
        Row: {
          id: string;
          simulation_id: string;
          validator_id: string;
          role: string;
          vote: string;
          confidence: number | null;
          reasoning: string | null;
          raw_llm_output: string | null;
          equivalence_score: number | null;
          voted_at: string;
        };
        Insert: {
          id?: string;
          simulation_id: string;
          validator_id: string;
          role?: string;
          vote: string;
          confidence?: number | null;
          reasoning?: string | null;
          raw_llm_output?: string | null;
          equivalence_score?: number | null;
          voted_at?: string;
        };
        Update: {
          vote?: string;
          confidence?: number | null;
          reasoning?: string | null;
          equivalence_score?: number | null;
        };
        Relationships: Relationship[];
      };
      consensus_results: {
        Row: {
          id: string;
          simulation_id: string;
          round: number;
          accept_count: number;
          reject_count: number;
          uncertain_count: number;
          consensus_type: string | null;
          equivalence_pass: boolean | null;
          outcome: string | null;
          computed_at: string;
        };
        Insert: {
          id?: string;
          simulation_id: string;
          round?: number;
          accept_count?: number;
          reject_count?: number;
          uncertain_count?: number;
          consensus_type?: string | null;
          equivalence_pass?: boolean | null;
          outcome?: string | null;
          computed_at?: string;
        };
        Update: {
          outcome?: string | null;
          equivalence_pass?: boolean | null;
        };
        Relationships: Relationship[];
      };
      appeals: {
        Row: {
          id: string;
          simulation_id: string;
          initiated_by: string | null;
          reason: string;
          status: string;
          additional_validators: number;
          original_outcome: string;
          final_outcome: string | null;
          created_at: string;
          resolved_at: string | null;
        };
        Insert: {
          id?: string;
          simulation_id: string;
          initiated_by?: string | null;
          reason: string;
          status?: string;
          additional_validators?: number;
          original_outcome: string;
          final_outcome?: string | null;
          created_at?: string;
          resolved_at?: string | null;
        };
        Update: {
          status?: string;
          final_outcome?: string | null;
          resolved_at?: string | null;
        };
        Relationships: Relationship[];
      };
      appeal_rounds: {
        Row: {
          id: string;
          appeal_id: string;
          round: number;
          outcome: string | null;
          votes_data: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          appeal_id: string;
          round: number;
          outcome?: string | null;
          votes_data?: Json | null;
          created_at?: string;
        };
        Update: {
          outcome?: string | null;
          votes_data?: Json | null;
        };
        Relationships: Relationship[];
      };
      analytics_events: {
        Row: {
          id: string;
          user_id: string | null;
          event_type: string;
          payload: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          event_type: string;
          payload?: Json | null;
          created_at?: string;
        };
        Update: never;
      };
      audit_logs: {
        Row: {
          id: string;
          user_id: string | null;
          action: string;
          table_name: string | null;
          record_id: string | null;
          diff: Json | null;
          ip_address: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          action: string;
          table_name?: string | null;
          record_id?: string | null;
          diff?: Json | null;
          ip_address?: string | null;
          created_at?: string;
        };
        Update: never;
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
}
