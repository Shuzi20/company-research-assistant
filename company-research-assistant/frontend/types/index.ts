export interface Competitor {
  name: string;
  website: string | null;
}

export interface CompanyData {
  company_name: string;
  website: string | null;
  phone: string | null;
  address: string | null;
  products_services: string[];
  pain_points: string[];
  competitors: Competitor[];
}

export interface ResearchResponse {
  data: CompanyData;
  warnings: string[];
  pdf_url: string | null; // base64 data URI, see pdf_generator.py
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