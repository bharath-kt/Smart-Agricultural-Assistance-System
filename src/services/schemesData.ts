import type { GovernmentScheme } from '../types';

export const governmentSchemes: GovernmentScheme[] = [
  {
    id: 'pm-kisan',
    title: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
    description: 'Income support of Rs. 6000 per year in three equal installments to all land holding farmer families.',
    category: 'subsidy',
    eligibility: [
      'Small and marginal farmers with cultivable land',
      'Landholding should be up to 2 hectares',
      'Family consists of husband, wife, and minor children'
    ],
    benefits: 'Rs. 6,000 per year directly transferred to bank account in three installments of Rs. 2,000 each',
    applicationProcess: 'Register through CSC centers, visit nearest agriculture office, or apply online at pmkisan.gov.in',
    documents: ['Aadhaar Card', 'Land Records', 'Bank Account Details', 'Passport Size Photo'],
    website: 'https://pmkisan.gov.in'
  },
  {
    id: 'soil-health-card',
    title: 'Soil Health Card Scheme',
    description: 'Provides information on nutrient status of soil and recommendations for appropriate dosage of nutrients.',
    category: 'equipment',
    eligibility: [
      'All farmers owning agricultural land',
      'Farmers cultivating on leased land',
      'Priority to small and marginal farmers'
    ],
    benefits: 'Free soil testing and customized fertilizer recommendations to improve soil health and crop yield',
    applicationProcess: 'Contact local agriculture department or Krishi Vigyan Kendra for soil sample collection',
    documents: ['Land Ownership Proof', 'Identity Proof', 'Application Form'],
    website: 'https://soilhealth.dac.gov.in'
  },
  {
    id: 'kcc',
    title: 'Kisan Credit Card (KCC)',
    description: 'Provides farmers with timely access to credit for agricultural needs at concessional interest rates.',
    category: 'loan',
    eligibility: [
      'Individual farmers (owner/cultivator)',
      'Tenant farmers and share croppers',
      'Self-help groups of farmers',
      'Joint liability groups'
    ],
    benefits: 'Short-term credit up to Rs. 3 lakh at 7% interest (4% with prompt repayment), coverage under PMFBY',
    applicationProcess: 'Apply at any nationalized bank, cooperative bank, or regional rural bank with required documents',
    documents: ['Identity Proof', 'Address Proof', 'Land Documents', 'Passport Photo', 'Bank Account Statement'],
    website: 'https://www.nabard.org'
  },
  {
    id: 'pmfby',
    title: 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
    description: 'Comprehensive crop insurance scheme to protect farmers against crop loss due to natural calamities.',
    category: 'insurance',
    eligibility: [
      'All farmers growing notified crops in notified areas',
      'Loanee farmers (compulsory)',
      'Non-loanee farmers (voluntary)'
    ],
    benefits: 'Insurance coverage and financial support to farmers in case of crop failure due to natural calamities, pests & diseases',
    applicationProcess: 'Enroll through bank while taking loan or directly through CSC/insurance company/agent',
    documents: ['Aadhaar Card', 'Land Records', 'Bank Account Details', 'Sowing Certificate'],
    website: 'https://pmfby.gov.in'
  },
  {
    id: 'midh',
    title: 'Mission for Integrated Development of Horticulture (MIDH)',
    description: 'Promotes holistic growth of horticulture sector including bamboo and coconut through area-based regionally differentiated strategies.',
    category: 'subsidy',
    eligibility: [
      'Individual farmers',
      'Self-help groups',
      'Cooperatives',
      'Farmer Producer Organizations'
    ],
    benefits: 'Financial assistance for establishment of orchards, nurseries, post-harvest management, and protected cultivation',
    applicationProcess: 'Apply through State Horticulture Mission or District Agriculture Office',
    documents: ['Identity Proof', 'Land Documents', 'Bank Account Details', 'Project Proposal'],
    website: 'https://midh.gov.in'
  },
  {
    id: 'aif',
    title: 'Agriculture Infrastructure Fund (AIF)',
    description: 'Financing facility for investment in viable projects for post-harvest management infrastructure and community farming assets.',
    category: 'loan',
    eligibility: [
      'Farmers',
      'FPOs',
      'Panchayats',
      'Startups',
      'State agencies involved in agriculture'
    ],
    benefits: 'Interest subvention of 3% per annum up to Rs. 2 crore, credit guarantee coverage under CGTMSE for loans up to Rs. 2 crore',
    applicationProcess: 'Apply online through Agriculture Infrastructure Fund portal with detailed project report',
    documents: ['Identity Proof', 'Land Documents', 'Bank Account Details', 'Detailed Project Report', 'Business Plan'],
    website: 'https://agriinfra.dac.gov.in'
  },
  {
    id: 'nmoop',
    title: 'National Mission on Oilseeds and Oil Palm (NMOOP)',
    description: 'Increases production and productivity of oilseeds and oil palm to reduce import dependency.',
    category: 'subsidy',
    eligibility: [
      'Farmers cultivating oilseed crops',
      'Farmers interested in oil palm cultivation',
      'State agricultural departments'
    ],
    benefits: 'Financial assistance for seeds, farm machinery, irrigation, and processing units for oilseeds',
    applicationProcess: 'Contact District Agriculture Office or State Department of Agriculture',
    documents: ['Identity Proof', 'Land Documents', 'Bank Account Details', 'Crop Details'],
    website: 'https://nmsa.dac.gov.in'
  },
  {
    id: 'nmaet',
    title: 'National Mission on Agricultural Extension and Technology (NMAET)',
    description: 'Strengthens agricultural extension services and promotes use of technology in farming.',
    category: 'training',
    eligibility: [
      'Farmers',
      'Extension workers',
      'Agricultural students',
      'Self-help groups'
    ],
    benefits: 'Training programs, demonstrations, exposure visits, and support for adopting new technologies',
    applicationProcess: 'Contact nearest Krishi Vigyan Kendra or State Agricultural University',
    documents: ['Identity Proof', 'Land Documents', 'Educational Certificates (if applicable)'],
    website: 'https://www.manage.gov.in'
  },
  {
    id: 'rkvy',
    title: 'Rashtriya Krishi Vikas Yojana (RKVY)',
    description: 'Provides states flexibility to develop and implement agricultural schemes as per their priorities.',
    category: 'subsidy',
    eligibility: [
      'Individual farmers',
      'Farmer groups',
      'Cooperatives',
      'Agricultural entrepreneurs'
    ],
    benefits: 'Financial assistance for various agricultural activities including farm mechanization, organic farming, and value addition',
    applicationProcess: 'Apply through State Agriculture Department with project proposal',
    documents: ['Identity Proof', 'Land Documents', 'Bank Account Details', 'Project Proposal'],
    website: 'https://rkvy.nic.in'
  },
  {
    id: 'paramparagat',
    title: 'Paramparagat Krishi Vikas Yojana (PKVY)',
    description: 'Promotes organic farming through adoption of eco-friendly technologies and traditional practices.',
    category: 'subsidy',
    eligibility: [
      'Farmers willing to adopt organic farming',
      'Groups of farmers (minimum 50 farmers)',
      'Farmers with contiguous land'
    ],
    benefits: 'Financial assistance of Rs. 50,000 per hectare for 3 years for organic inputs and certification',
    applicationProcess: 'Form a group of 50 farmers and apply through District Agriculture Office',
    documents: ['Identity Proof', 'Land Documents', 'Group Formation Documents', 'Bank Account Details'],
    website: 'https://pgsindia-ncof.gov.in'
  }
];

export function getSchemesByCategory(category: string): GovernmentScheme[] {
  if (category === 'all') return governmentSchemes;
  return governmentSchemes.filter(scheme => scheme.category === category);
}

export function searchSchemes(query: string): GovernmentScheme[] {
  const lowerQuery = query.toLowerCase();
  return governmentSchemes.filter(scheme => 
    scheme.title.toLowerCase().includes(lowerQuery) ||
    scheme.description.toLowerCase().includes(lowerQuery) ||
    scheme.category.toLowerCase().includes(lowerQuery)
  );
}
