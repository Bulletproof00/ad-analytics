export interface AdListItem {
  id: string;
  score_total: number;
  score_reuse?: number;
  score_variants?: number;
  page_name: string | null;
  start_time: string | null;
  stop_time: string | null;
  hook_preview: string | null;
  funnel_type: string | null;
  offer_type: string | null;
  snapshot_url: string | null;
}

export interface HookItem {
  id: string;
  hook_text: string;
  reuse_count: number;
  example_ad_ids: string[];
}

export interface StatsResponse {
  total_ads: number;
  total_pages: number;
  winners_count: number;
  new_ads_last_7d: number;
  top_hooks: { hook_text: string; reuse_count: number }[];
}

export interface AdDetail {
  id: string;
  ad_archive_id: string;
  page_id: string | null;
  page_name: string | null;
  start_time: string | null;
  stop_time: string | null;
  snapshot_url: string | null;
  copy_bodies: Record<string, string> | null;
  link_titles: Record<string, string> | null;
  link_descriptions: Record<string, string> | null;
  link_captions: Record<string, string> | null;
  publisher_platforms: Record<string, string> | null;
  tags: {
    niche: string;
    funnel_type: string;
    offer_type: string;
    emotion_trigger: string;
    is_winner: boolean;
    notes: string | null;
  };
  score: {
    score_total: number;
    score_runtime: number;
    score_variants: number;
    score_reuse: number;
    score_funnel_fit: number;
    saturation_index?: number;
    explanation: Record<string, any>;
  };
  hook: string | null;
  reuse_count: number;
  variants_count: number;
  features?: Record<string, any>;
}
