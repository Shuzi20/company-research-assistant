export interface Competitor {
  name: string;
  website: string | null;
  reason?: string | null;
}

export interface CompanyData {
  company_name: string;

  website: string | null;
  phone: string | null;
  address: string | null;

  industry?: string | null;
  summary?: string | null;
  business_model?: string | null;

  target_customers: string[];

  products_services: string[];

  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];

  pain_points: string[];

  competitors: Competitor[];
}

export interface ResearchResponse {
  data: CompanyData;
  warnings: string[];
  pdf_url: string | null;
}

export interface ApiKeys {
  openrouterKey: string;
  serperKey: string;
  model: string;
}

export interface DiscordConfig {
  botToken: string;
  channelId: string;
  applicantName: string;
  applicantEmail: string;
}