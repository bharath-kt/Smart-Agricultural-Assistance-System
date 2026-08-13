import type { GovernmentScheme } from '../types';

export const CATEGORY_TRANSLATIONS: Record<string, { en: string; kn: string }> = {
  subsidy: { en: 'Subsidy', kn: 'ಸಹಾಯಧನ' },
  loan: { en: 'Loan', kn: 'ಸಾಲ ಯೋಜನೆ' },
  insurance: { en: 'Insurance', kn: 'ಬೆಳೆ ವಿಮೆ' },
  training: { en: 'Training', kn: 'ತರಬೇತಿ' },
  equipment: { en: 'Equipment', kn: 'ಉಪಕರಣ' }
};

export function translateSchemeCategory(category: string, lang: string): string {
  if (lang === 'kn' && CATEGORY_TRANSLATIONS[category]) {
    return CATEGORY_TRANSLATIONS[category].kn;
  }
  return CATEGORY_TRANSLATIONS[category]?.en || category;
}

export const SCHEME_KN_DATA: Record<string, {
  title: string;
  description: string;
  benefits: string;
  eligibility: string[];
  applicationProcess: string;
  documents: string[];
}> = {
  'pm-kisan': {
    title: 'ಪಿಎಂ-ಕಿಸಾನ್ (ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ)',
    description: 'ಎಲ್ಲಾ ಜಮೀನು ಹೊಂದಿರುವ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ರೂ. 6000 ಆದಾಯ ಬೆಂಬಲವನ್ನು ಮೂರು ಸಮಾನ ಕಂತುಗಳಲ್ಲಿ ನೀಡಲಾಗುತ್ತದೆ.',
    benefits: 'ವರ್ಷಕ್ಕೆ ರೂ. 6,000 ನೇರವಾಗಿ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಮೂರು ಕಂತುಗಳಲ್ಲಿ (ಪ್ರತಿ ಕಂತಿಗೆ ರೂ. 2,000) ಜಮೆಯಾಗುತ್ತದೆ',
    eligibility: [
      'ಸಾಗುವಳಿ ಭೂಮಿ ಹೊಂದಿರುವ ಸಣ್ಣ ಮತ್ತು ಅಂಚಿನ ರೈತರು',
      'ಭೂಮಿಯ ವಿಸ್ತೀರ್ಣ 2 ಹೆಕ್ಟೇರ್‌ವರೆಗೆ ಇರಬೇಕು',
      'ಕುಟುಂಬವು ಪತಿ, ಪತ್ನಿ ಮತ್ತು ಅಪ್ರಾಪ್ತ ಮಕ್ಕಳನ್ನು ಒಳಗೊಂಡಿರುತ್ತದೆ'
    ],
    applicationProcess: 'CSC ಕೇಂದ್ರಗಳ ಮೂಲಕ ನೋಂದಾಯಿಸಿ, ಹತ್ತಿರದ ಕೃಷಿ ಕಚೇರಿಗೆ ಭೇಟಿ ನೀಡಿ ಅಥವಾ pmkisan.gov.in ನಲ್ಲಿ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ',
    documents: ['ಆಧಾರ್ ಕಾರ್ಡ್', 'ಪಹಣಿ (RTC/ಭೂ ದಾಖಲೆಗಳು)', 'ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು', 'ಪಾಸ್‌ಪೋರ್ಟ್ ಅಳತೆಯ ಫೋಟೋ']
  },
  'soil-health-card': {
    title: 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಯೋಜನೆ (Soil Health Card)',
    description: 'ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳ ಸ್ಥಿತಿಯ ಬಗ್ಗೆ ಮಾಹಿತಿ ಮತ್ತು ಪೋಷಕಾಂಶಗಳ ಸೂಕ್ತ ಪ್ರಮಾಣಕ್ಕಾಗಿ ಶಿಫಾರಸುಗಳನ್ನು ಒದಗಿಸುತ್ತದೆ.',
    benefits: 'ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಮತ್ತು ಬೆಳೆ ಇಳುವರಿಯನ್ನು ಸುಧಾರಿಸಲು ಉಚಿತ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮತ್ತು ರಸಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳು',
    eligibility: [
      'ಕೃಷಿ ಭೂಮಿ ಹೊಂದಿರುವ ಎಲ್ಲಾ ರೈತರು',
      'ಗುತ್ತಿಗೆ ಭೂಮಿಯಲ್ಲಿ ಬೇಸಾಯ ಮಾಡುವ ರೈತರು',
      'ಸಣ್ಣ ಮತ್ತು ಅಂಚಿನ ರೈತರಿಗೆ ಆದ್ಯತೆ'
    ],
    applicationProcess: 'ಮಣ್ಣಿನ ಮಾದರಿ ಸಂಗ್ರಹಣೆಗಾಗಿ ಸ್ಥಳೀಯ ಕೃಷಿ ಇಲಾಖೆ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು ಸಂಪರ್ಕಿಸಿ',
    documents: ['ಭೂ ಮಾಲೀಕತ್ವದ ಪುರಾವೆ (RTC)', 'ಗುರುತಿನ ಚೀಟಿ (Aadhaar)', 'ಅರ್ಜಿ ನಮೂನೆ']
  },
  'kcc': {
    title: 'ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC)',
    description: 'ರೈತರಿಗೆ ಕೃಷಿ ಅಗತ್ಯಗಳಿಗಾಗಿ ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರದಲ್ಲಿ ಸಮಯೋಚಿತ ಸಾಲದ ಸೌಲಭ್ಯವನ್ನು ಒದಗಿಸುತ್ತದೆ.',
    benefits: '7% ಬಡ್ಡಿದರದಲ್ಲಿ ರೂ. 3 ಲಕ್ಷದವರೆಗೆ ಅಲ್ಪಾವಧಿ ಸಾಲ (ಸರಿಯಾದ ಸಮಯಕ್ಕೆ ಮರುಪಾವತಿಸಿದರೆ 4% ಬಡ್ಡಿ), PMFBY ಅಡಿಯಲ್ಲಿ ವಿಮೆ',
    eligibility: [
      'ವೈಯಕ್ತಿಕ ರೈತರು (ಮಾಲೀಕರು/ಸಾಗುವಳಿದಾರರು)',
      'ಗುತ್ತಿಗೆದಾರರು ಮತ್ತು ಗೇಣಿದಾರರು',
      'ರೈತರ ಸ್ವಸಹಾಯ ಗುಂಪುಗಳು (SHG)'
    ],
    applicationProcess: 'ಅಗತ್ಯ ದಾಖಲೆಗಳೊಂದಿಗೆ ಯಾವುದೇ ರಾಷ್ಟ್ರೀಕೃತ ಬ್ಯಾಂಕ್, ಸಹಕಾರಿ ಬ್ಯಾಂಕ್ ಅಥವಾ ಪ್ರಾದೇಶಿಕ ಗ್ರಾಮೀಣ ಬ್ಯಾಂಕ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ವಿಳಾಸದ ಪುರಾವೆ', 'ಪಹಣಿ / ಭೂ ದಾಖಲೆಗಳು', 'ಫೋಟೋ', 'ಬ್ಯಾಂಕ್ ಖಾತೆ ಪುಸ್ತಕ']
  },
  'pmfby': {
    title: 'ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY)',
    description: 'ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳಿಂದ ಬೆಳೆ ನಷ್ಟದ ವಿರುದ್ಧ ರೈತರನ್ನು ರಕ್ಷಿಸಲು ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ ಯೋಜನೆ.',
    benefits: 'ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳು, ಕೀಟಗಳು ಮತ್ತು ರೋಗಗಳಿಂದ ಬೆಳೆ ನಷ್ಟವಾದಲ್ಲಿ ರೈತರಿಗೆ ವಿಮಾ ರಕ್ಷಣೆ ಮತ್ತು ಆರ್ಥಿಕ ನೆರವು',
    eligibility: [
      'ಅಧಿಸೂಚಿತ ಪ್ರದೇಶಗಳಲ್ಲಿ ಅಧಿಸೂಚಿತ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯುವ ಎಲ್ಲಾ ರೈತರು',
      'ಸಾಲ ಪಡೆದ ರೈತರು (ಕಡ್ಡಾಯ)',
      'ಸಾಲ ಪಡೆಯದ ರೈತರು (ಐಚ್ಛಿಕ)'
    ],
    applicationProcess: 'ಸಾಲ ಪಡೆಯುವಾಗ ಬ್ಯಾಂಕ್ ಮೂಲಕ ಅಥವಾ CSC/ವಿಮಾ ಕಂಪನಿ/ಏಜೆಂಟ್ ಮೂಲಕ ನೇರವಾಗಿ ನೋಂದಾಯಿಸಿ',
    documents: ['ಆಧಾರ್ ಕಾರ್ಡ್', 'ಪಹಣಿ (RTC)', 'ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು', 'ಬೆಳೆ ಬಿತ್ತನೆ ದೃಢೀಕರಣ ಪತ್ರ']
  },
  'midh': {
    title: 'ಸಮಗ್ರ ತೋಟಗಾರಿಕೆ ಅಭಿವೃದ್ಧಿ ಮಿಷನ್ (MIDH)',
    description: 'ಬಿದಿರು ಮತ್ತು ತೆಂಗು ಸೇರಿದಂತೆ ತೋಟಗಾರಿಕಾ ಕ್ಷೇತ್ರದ ಸಮಗ್ರ ಬೆಳವಣಿಗೆಯನ್ನು ಉತ್ತೇಜಿಸುತ್ತದೆ.',
    benefits: 'ತೋಟಗಳು, ನರ್ಸರಿಗಳು, ಕೊಯ್ಲೋತ್ತರ ನಿರ್ವಹಣೆ ಮತ್ತು ರಕ್ಷಿತ ಬೇಸಾಯ ಸ್ಥಾಪನೆಗೆ ಆರ್ಥಿಕ ನೆರವು',
    eligibility: [
      'ವೈಯಕ್ತಿಕ ರೈತರು',
      'ಸ್ವಸಹಾಯ ಗುಂಪುಗಳು',
      'ಸಹಕಾರ ಸಂಘಗಳು',
      'ರೈತ ಉತ್ಪಾದಕ ಸಂಸ್ಥೆಗಳು (FPO)'
    ],
    applicationProcess: 'ರಾಜ್ಯ ತೋಟಗಾರಿಕೆ ಮಿಷನ್ ಅಥವಾ ಜಿಲ್ಲಾ ಕೃಷಿ ಕಚೇರಿಯ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ಭೂ ದಾಖಲೆಗಳು', 'ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು', 'ಯೋಜನಾ ಪ್ರಸ್ತಾಪ']
  },
  'aif': {
    title: 'ಕೃಷಿ ಮೂಲಸೌಕರ್ಯ ನಿಧಿ (Agriculture Infrastructure Fund)',
    description: 'ಕೊಯ್ಲೋತ್ತರ ನಿರ್ವಹಣಾ ಮೂಲಸೌಕರ್ಯ ಮತ್ತು ಸಮುದಾಯ ಕೃಷಿ ಆಸ್ತಿಗಳ ಯೋಜನೆಗಳಿಗೆ ಧನಸಹಾಯ.',
    benefits: 'ರೂ. 2 ಕೋಟಿವರೆಗಿನ ಸಾಲಕ್ಕೆ ವರ್ಷಕ್ಕೆ 3% ಬಡ್ಡಿ ಸಹಾಯಧನ',
    eligibility: [
      'ರೈತರು',
      'ಎಫ್‌ಪಿಒ (FPO)',
      'ಪಂಚಾಯತ್‌ಗಳು',
      'ಸ್ಟಾರ್ಟ್‌ಅಪ್‌ಗಳು'
    ],
    applicationProcess: 'ವಿಸ್ತೃತ ಯೋಜನಾ ವರದಿಯೊಂದಿಗೆ ಕೃಷಿ ಮೂಲಸೌಕರ್ಯ ನಿಧಿ ಪೋರ್ಟಲ್ ಮೂಲಕ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ಭೂ ದಾಖಲೆಗಳು', 'ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು', 'ಯೋಜನಾ ವರದಿ (DPR)']
  },
  'nmoop': {
    title: 'ರಾಷ್ಟ್ರೀಯ ಎಣ್ಣೆಕಾಳು ಮತ್ತು ಎಣ್ಣೆ ತಾಳೆ ಮಿಷನ್ (NMOOP)',
    description: 'ಆಮದು ಅವಲಂಬನೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಎಣ್ಣೆಕಾಳುಗಳು ಮತ್ತು ಎಣ್ಣೆ ತಾಳೆ ಉತ್ಪಾದನೆ ಹೆಚ್ಚಳ.',
    benefits: 'ಬಿತ್ತನೆ ಬೀಜಗಳು, ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳು, ನೀರಾವರಿ ಮತ್ತು ಸಂಸ್ಕರಣಾ ಘಟಕಗಳಿಗೆ ಆರ್ಥಿಕ ನೆರವು',
    eligibility: [
      'ಎಣ್ಣೆಕಾಳು ಬೆಳೆಯುವ ರೈತರು',
      'ಎಣ್ಣೆ ತಾಳೆ ಬೇಸಾಯದಲ್ಲಿ ಆಸಕ್ತಿ ಹೊಂದಿರುವ ರೈತರು'
    ],
    applicationProcess: 'ಜಿಲ್ಲಾ ಕೃಷಿ ಕಚೇರಿ ಅಥವಾ ರಾಜ್ಯ ಕೃಷಿ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ಭೂ ದಾಖಲೆಗಳು', 'ಬ್ಯಾಂಕ್ ವಿವರಗಳು']
  },
  'nmaet': {
    title: 'ರಾಷ್ಟ್ರೀಯ ಕೃಷಿ ವಿಸ್ತರಣೆ ಮತ್ತು ತಂತ್ರಜ್ಞಾನ ಮಿಷನ್ (NMAET)',
    description: 'ಕೃಷಿ ವಿಸ್ತರಣಾ ಸೇವೆಗಳನ್ನು ಬಲಪಡಿಸುತ್ತದೆ ಮತ್ತು ಕೃಷಿಯಲ್ಲಿ ತಂತ್ರಜ್ಞಾನದ ಬಳಕೆಯನ್ನು ಉತ್ತೇಜಿಸುತ್ತದೆ.',
    benefits: 'ತರಬೇತಿ ಕಾರ್ಯಕ್ರಮಗಳು, ಪ್ರಾತ್ಯಕ್ಷಿಕೆಗಳು ಮತ್ತು ಹೊಸ ತಂತ್ರಜ್ಞಾನ ಅಳವಡಿಕೆಗೆ ಬೆಂಬಲ',
    eligibility: [
      'ರೈತರು',
      'ವಿಸ್ತರಣಾ ಕರ್ತರು',
      'ಕೃಷಿ ವಿದ್ಯಾರ್ಥಿಗಳು'
    ],
    applicationProcess: 'ಹತ್ತಿರದ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಅಥವಾ ರಾಜ್ಯ ಕೃಷಿ ವಿಶ್ವವಿದ್ಯಾಲಯವನ್ನು ಸಂಪರ್ಕಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ಭೂ ದಾಖಲೆಗಳು']
  },
  'rkvy': {
    title: 'ರಾಷ್ಟ್ರೀಯ ಕೃಷಿ ವಿಕಾಸ ಯೋಜನೆ (RKVY)',
    description: 'ರಾಜ್ಯಗಳಿಗೆ ತಮ್ಮ ಆದ್ಯತೆಗಳಿಗೆ ಅನುಗುಣವಾಗಿ ಕೃಷಿ ಯೋಜನೆಗಳನ್ನು ಅಭಿವೃದ್ಧಿಪಡಿಸಲು ನಮ್ಯತೆಯನ್ನು ನೀಡುತ್ತದೆ.',
    benefits: 'ಯಾಂತ್ರೀಕರಣ, ಸಾವಯವ ಕೃಷಿ ಸೇರಿದಂತೆ ವಿವಿಧ ಕೃಷಿ ಚಟುವಟಿಕೆಗಳಿಗೆ ಆರ್ಥಿಕ ನೆರವು',
    eligibility: [
      'ವೈಯಕ್ತಿಕ ರೈತರು',
      'ರೈತರ ಗುಂಪುಗಳು',
      'ಸಹಕಾರ ಸಂಘಗಳು'
    ],
    applicationProcess: 'ಯೋಜನಾ ಪ್ರಸ್ತಾಪದೊಂದಿಗೆ ರಾಜ್ಯ ಕೃಷಿ ಇಲಾಖೆಯ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ಭೂ ದಾಖಲೆಗಳು', 'ಬ್ಯಾಂಕ್ ವಿವರಗಳು']
  },
  'paramparagat': {
    title: 'ಪರಂಪರಾಗತ್ ಕೃಷಿ ವಿಕಾಸ ಯೋಜನೆ (PKVY)',
    description: 'ಪರಿಸರ ಸ್ನೇಹಿ ತಂತ್ರಜ್ಞಾನಗಳು ಮತ್ತು ಸಾಂಪ್ರದಾಯಿಕ ಪದ್ಧತಿಗಳ ಮೂಲಕ ಸಾವಯವ ಕೃಷಿಯನ್ನು ಉತ್ತೇಜಿಸುತ್ತದೆ.',
    benefits: 'ಸಾವಯವ ಪರಿಕರಗಳು ಮತ್ತು ಪ್ರಮಾಣೀಕರಣಕ್ಕಾಗಿ 3 ವರ್ಷಗಳವರೆಗೆ ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ರೂ. 50,000 ಆರ್ಥಿಕ ನೆರವು',
    eligibility: [
      'ಸಾವಯವ ಕೃಷಿ ಅಳವಡಿಸಿಕೊಳ್ಳಲು ಸಿದ್ಧರಿರುವ ರೈತರು',
      'ರೈತರ ಗುಂಪುಗಳು (ಕನಿಷ್ಠ 50 ರೈತರು)'
    ],
    applicationProcess: '50 ರೈತರ ಗುಂಪನ್ನು ರಚಿಸಿ ಮತ್ತು ಜಿಲ್ಲಾ ಕೃಷಿ ಕಚೇರಿಯ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ',
    documents: ['ಗುರುತಿನ ಚೀಟಿ', 'ಭೂ ದಾಖಲೆಗಳು', 'ಗುಂಪಿನ ದಾಖಲೆಗಳು', 'ಬ್ಯಾಂಕ್ ವಿವರಗಳು']
  }
};

export function getLocalizedScheme(scheme: GovernmentScheme, lang: string): GovernmentScheme {
  if (lang === 'kn' && SCHEME_KN_DATA[scheme.id]) {
    const kn = SCHEME_KN_DATA[scheme.id];
    return {
      ...scheme,
      title: kn.title,
      description: kn.description,
      benefits: kn.benefits,
      eligibility: kn.eligibility,
      applicationProcess: kn.applicationProcess,
      documents: kn.documents,
    };
  }
  return scheme;
}

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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function fetchBackendRecommendations(token: string) {
  const res = await fetch(`${API_BASE_URL}/schemes/recommendations`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch recommendations');
  return res.json();
}

export async function fetchBackendSchemes(token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE_URL}/schemes`, { headers });
  if (!res.ok) throw new Error('Failed to fetch schemes');
  return res.json();
}
