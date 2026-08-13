"""Government schemes service with scalable database and rule eligibility engine."""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.logging import get_logger
from app.models.scheme import GovernmentScheme, SchemeApplication
from app.models.user import FarmerProfile
from app.schemas.scheme import (
    SchemeResponse,
    SchemeDetailResponse,
    SchemeRecommendationResponse,
    SchemeRecommendationItem
)

logger = get_logger(__name__)


class SchemeService:
    """Service for government schemes management & recommendation engine."""

    DEFAULT_SCHEMES = [
        {
            "scheme_code": "PM-KISAN",
            "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "source": "PM-KISAN Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Department of Agriculture & Farmers Welfare",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "financial",
            "short_description": "Income support of Rs. 6,000 per year to eligible farmer families in 3 installments.",
            "full_description": "PM-KISAN is a Central Sector Scheme providing direct income support of Rs. 6,000 per year to all landholding farmer families across the country. The amount is transferred directly into bank accounts in 3 equal installments of Rs. 2,000 every 4 months.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "All Farmers"],
            "eligible_crops": ["All Crops"],
            "min_age": 18,
            "max_age": 80,
            "gender_req": "All",
            "min_land_holding": 0.01,
            "max_land_holding": 2.0,
            "income_criteria": "Small & Marginal Farmers with cultivable land record",
            "eligibility_summary": "Open to landholding farmer families with up to 2.0 hectares of land. Excludes high income taxpayers.",
            "benefit_type": "financial",
            "benefit_amount": "Rs. 6,000 per year",
            "benefit_description": "Direct bank transfer of Rs. 6,000 annually in three 4-monthly installments of Rs. 2,000.",
            "required_documents": ["Aadhaar Card", "Land Ownership Record (Pahani/RTC)", "Active Savings Bank Account", "Mobile Number"],
            "application_process": "Register online at https://pmkisan.gov.in via Farmers Corner or visit nearest Common Service Centre (CSC) / Village Agriculture Officer.",
            "application_url": "https://pmkisan.gov.in/",
            "official_website": "https://pmkisan.gov.in/",
            "helpline_number": "155261 / 011-24300606",
            "helpline_email": "pmkisan-ict@gov.in",
            "last_updated_date": "2026-08-01",
            "tags": ["income support", "cash transfer", "small farmer", "pm-kisan"]
        },
        {
            "scheme_code": "PMFBY",
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "source": "PMFBY Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Department of Agriculture & Farmers Welfare",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "insurance",
            "short_description": "Comprehensive crop loss insurance against natural disasters, pests, and drought.",
            "full_description": "PMFBY provides financial support to farmers suffering crop loss/damage arising out of unavoidable natural calamities, pests, and diseases. Farmers pay a low premium (1.5% - 2% for food crops, 5% for commercial/horticultural crops) and receive sum insured.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "Large", "Tenant Farmers", "All Farmers"],
            "eligible_crops": ["Food Crops", "Oilseeds", "Cotton", "Sugarcane", "Tomato", "Paddy", "Corn", "Wheat", "Commercial Crops"],
            "min_age": 18,
            "max_age": 75,
            "gender_req": "All",
            "min_land_holding": 0.05,
            "max_land_holding": 25.0,
            "eligibility_summary": "All farmers growing notified crops in notified areas including sharecroppers and tenant farmers.",
            "benefit_type": "insurance",
            "benefit_amount": "Up to 100% Sum Insured for yield loss",
            "benefit_description": "Comprehensive risk coverage from pre-sowing to post-harvest losses due to non-preventable natural risks.",
            "required_documents": ["Aadhaar Card", "Land Record / Tenancy Agreement", "Bank Passbook", "Sowing Certificate / Crop Declaration"],
            "application_process": "Enroll online at pmfby.gov.in, via national crop insurance portal app, or through authorized banks/CSCs before notified cutoff date.",
            "application_url": "https://pmfby.gov.in/",
            "official_website": "https://pmfby.gov.in/",
            "helpline_number": "1800-180-1551",
            "helpline_email": "pmfby@gov.in",
            "last_updated_date": "2026-07-15",
            "tags": ["crop insurance", "disaster relief", "drought insurance", "pmfby"]
        },
        {
            "scheme_code": "KCC",
            "name": "Kisan Credit Card (KCC) Scheme",
            "source": "Reserve Bank of India & NABARD",
            "government_level": "Central",
            "state": "All States",
            "department": "Department of Financial Services",
            "ministry": "Ministry of Finance",
            "category": "loan",
            "short_description": "Concessional agricultural credit loan up to Rs. 3 Lakhs at 4% effective interest rate.",
            "full_description": "KCC provides short-term formal credit to farmers for cultivation of crops, post-harvest expenses, maintenance of farm assets, and allied activities. Interest rate is 7% with 3% prompt repayment incentive, reducing effective interest rate to 4%.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "Large", "Tenant Farmers", "Share Croppers", "All Farmers"],
            "eligible_crops": ["All Crops"],
            "min_age": 18,
            "max_age": 75,
            "gender_req": "All",
            "min_land_holding": 0.01,
            "max_land_holding": 50.0,
            "income_criteria": "All owner cultivators, tenant farmers, and oral lessees",
            "eligibility_summary": "Individual farmers, joint borrowers, tenant farmers, self-help groups (SHGs) engaged in agriculture.",
            "benefit_type": "loan",
            "benefit_amount": "Collateral-free loan up to Rs. 1.6 Lakh (max limit Rs. 3 Lakh at subsidized interest)",
            "benefit_description": "Subsidized interest credit for farm inputs (seeds, fertilizers, pesticides) and harvesting operations.",
            "required_documents": ["Identity Proof (Aadhaar/Voter ID)", "Address Proof", "Land Ownership Documents / Cultivation Proof", "Passport Size Photographs"],
            "application_process": "Fill KCC application at any commercial bank, RRB, cooperative bank, or download form from bank portal.",
            "application_url": "https://www.pmkisan.gov.in/KccForm.aspx",
            "official_website": "https://www.nabard.org/",
            "helpline_number": "1800-11-22-11",
            "helpline_email": "kcc-help@gov.in",
            "last_updated_date": "2026-07-20",
            "tags": ["credit", "loan", "low interest", "kcc", "subsidy"]
        },
        {
            "scheme_code": "eNAM",
            "name": "National Agriculture Market (eNAM)",
            "source": "eNAM Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Small Farmers Agribusiness Consortium (SFAC)",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "equipment",
            "short_description": "Pan-India electronic trading portal uniting APMC mandis for transparent crop selling.",
            "full_description": "eNAM integrates physical APMC market yards into a single online trading platform to create a unified national agricultural market. Farmers can view real-time prices across mandis and sell produce to buyers anywhere in India.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["All Farmers", "Traders", "FPOs"],
            "eligible_crops": ["All Crops", "Tomato", "Paddy", "Corn", "Wheat", "Vegetables", "Pulses"],
            "min_age": 18,
            "max_age": 85,
            "gender_req": "All",
            "eligibility_summary": "All farmers looking to sell agricultural commodities directly via APMC mandis with digital payments.",
            "benefit_type": "market access",
            "benefit_amount": "Direct online buyer bidding & zero market middleman fee",
            "benefit_description": "Transparent price discovery, quality testing facility, direct bank settlement, and expanded buyer reach.",
            "required_documents": ["Aadhaar Card", "Bank Account Details", "Mobile Number", "Farmer APMC Passbook"],
            "application_process": "Register online at enam.gov.in or at the eNAM help desk located in any registered APMC mandi.",
            "application_url": "https://enam.gov.in/web/",
            "official_website": "https://enam.gov.in/web/",
            "helpline_number": "1800-270-0224",
            "helpline_email": "support-enam@gov.in",
            "last_updated_date": "2026-06-30",
            "tags": ["mandi prices", "online sale", "direct trade", "enam"]
        },
        {
            "scheme_code": "SMAM",
            "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
            "source": "FARMECH Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Mechanization and Technology Division",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "subsidy",
            "short_description": "40% to 80% financial subsidy for purchasing tractors, tillers, sprayers, and harvesters.",
            "full_description": "SMAM aims to promote farm mechanization by providing financial assistance/subsidy for purchasing tractors, power tillers, reapers, sprayers, rotavators, and setting up Custom Hiring Centres (CHCs).",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "Large", "Women Farmers", "All Farmers"],
            "eligible_crops": ["All Crops"],
            "min_age": 18,
            "max_age": 75,
            "gender_req": "All",
            "min_land_holding": 0.1,
            "max_land_holding": 15.0,
            "eligibility_summary": "Individual farmers, SHGs, and cooperatives. Special higher subsidy percentage (50-80%) for small, marginal, and women farmers.",
            "benefit_type": "subsidy",
            "benefit_amount": "40% to 80% subsidy on equipment cost",
            "benefit_description": "Subsidized farm machinery purchase or custom hiring access to reduce manual labor costs.",
            "required_documents": ["Aadhaar Card", "Ration Card", "Land Record (Pahani)", "Bank Passbook", "Proforma Invoice from Dealer"],
            "application_process": "Apply online at agrimachinery.nic.in portal during state application windows.",
            "application_url": "https://agrimachinery.nic.in/",
            "official_website": "https://agrimachinery.nic.in/",
            "helpline_number": "1800-180-1551",
            "helpline_email": "smam-help@gov.in",
            "last_updated_date": "2026-07-10",
            "tags": ["machinery", "tractor subsidy", "equipment", "smam"]
        },
        {
            "scheme_code": "PMKSY-PDMC",
            "name": "Pradhan Mantri Krishi Sinchayee Yojana - Per Drop More Crop",
            "source": "PMKSY Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Department of Agriculture & Farmers Welfare",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "subsidy",
            "short_description": "55% subsidy for Small & Marginal farmers on Drip & Sprinkler Irrigation systems.",
            "full_description": "PMKSY (Per Drop More Crop) focuses on enhancing water use efficiency at farm level through Micro Irrigation technologies like Drip and Sprinkler systems. Government provides up to 55% subsidy for Small/Marginal farmers and 45% for Other farmers.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "Large", "All Farmers"],
            "eligible_crops": ["All Crops", "Tomato", "Paddy", "Corn", "Sugarcane", "Horticulture"],
            "min_age": 18,
            "max_age": 80,
            "gender_req": "All",
            "min_land_holding": 0.1,
            "max_land_holding": 5.0,
            "irrigation_req": "Drip/Sprinkler",
            "eligibility_summary": "Farmers with valid land record and assured water source installing micro-irrigation systems.",
            "benefit_type": "subsidy",
            "benefit_amount": "45% to 55% subsidy on Drip/Sprinkler installation",
            "benefit_description": "Financial subsidy for micro-irrigation pipeline, drip lines, filters, and sprinkler equipment.",
            "required_documents": ["Aadhaar Card", "Land Pahani / RTC", "Water Source Certificate / Electricity Bill", "Bank Passbook"],
            "application_process": "Submit application to District Horticulture / Agriculture Officer or register on state micro-irrigation portal.",
            "application_url": "https://pmksy.gov.in/",
            "official_website": "https://pmksy.gov.in/",
            "helpline_number": "011-23381005",
            "helpline_email": "pmksy-agri@gov.in",
            "last_updated_date": "2026-05-18",
            "tags": ["irrigation", "drip subsidy", "sprinkler", "water saving", "pmksy"]
        },
        {
            "scheme_code": "SHC",
            "name": "Soil Health Card Scheme",
            "source": "Soil Health Card Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Department of Agriculture & Farmers Welfare",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "training",
            "short_description": "Free soil testing report and customized nutrient management guidelines for farm land.",
            "full_description": "Soil Health Card scheme provides every farmer with a detailed soil diagnostic report covering 12 parameters (N, P, K, S, Zinc, Fe, Cu, Mn, Bo, pH, EC, OC). Includes customized fertilizer recommendations to boost crop yield.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "Large", "All Farmers"],
            "eligible_crops": ["All Crops"],
            "min_age": 18,
            "max_age": 85,
            "gender_req": "All",
            "eligibility_summary": "All farmers with agricultural land across all states.",
            "benefit_type": "service",
            "benefit_amount": "Free soil testing & advisory report every 2 years",
            "benefit_description": "Scientifically recommended dose of primary, secondary, and micro-nutrients to reduce input cost by 20%.",
            "required_documents": ["Aadhaar Card", "Land Survey Number / RTC Details", "Mobile Number"],
            "application_process": "Request soil sample collection through Village Agriculture Assistant or submit sample directly at Soil Testing Lab.",
            "application_url": "https://soilhealth.dac.gov.in/",
            "official_website": "https://soilhealth.dac.gov.in/",
            "helpline_number": "011-23382012",
            "helpline_email": "helpdesk-shc@gov.in",
            "last_updated_date": "2026-06-12",
            "tags": ["soil test", "fertilizer guide", "yield improvement", "free card"]
        },
        {
            "scheme_code": "KAR-KB",
            "name": "Krishi Bhagya Scheme (Karnataka State)",
            "source": "Karnataka Agriculture Department",
            "government_level": "State",
            "state": "Karnataka",
            "department": "Department of Agriculture, Govt of Karnataka",
            "ministry": "Ministry of Agriculture, Karnataka",
            "category": "subsidy",
            "short_description": "80% to 90% subsidy for construction of Farm Ponds (Krishi Houda) and polyhouse lining in Karnataka.",
            "full_description": "Krishi Bhagya is Karnataka state flagship scheme designed for rainfed agriculture regions. Provides 80-90% subsidy for farm ponds, polythene lining, diesel/solar pump sets, and shade nets to secure rain water for dryland crops.",
            "eligible_states": ["Karnataka"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "All Farmers"],
            "eligible_crops": ["All Crops", "Tomato", "Paddy", "Corn", "Millets", "Pulses"],
            "min_age": 18,
            "max_age": 75,
            "gender_req": "All",
            "min_land_holding": 0.2,
            "max_land_holding": 10.0,
            "irrigation_req": "Rainfed",
            "eligibility_summary": "Farmers residing in Karnataka engaged in rainfed agriculture.",
            "benefit_type": "subsidy",
            "benefit_amount": "Up to 90% subsidy on Farm Pond construction",
            "benefit_description": "Financial assistance for rain water harvesting ponds, solar pump sets, and micro-irrigation attachments.",
            "required_documents": ["Aadhaar Card", "Karnataka Pahani / RTC Record", "Bank Passbook", "Caste / Category Certificate"],
            "application_process": "Apply at Raitha Samparka Kendra (RSK) or online via Karnataka KUTUMBA / Fruit portal.",
            "application_url": "https://fruits.karnataka.gov.in/",
            "official_website": "https://raitamitra.karnataka.gov.in/",
            "helpline_number": "1800-425-3553 (Kisan Call Centre KA)",
            "helpline_email": "dir-agri-ka@nic.in",
            "last_updated_date": "2026-07-28",
            "tags": ["karnataka", "krishi bhagya", "farm pond", "rainfed subsidy"]
        },
        {
            "scheme_code": "RKVY-RAFTAAR",
            "name": "Rashtriya Krishi Vikas Yojana (RKVY-RAFTAAR)",
            "source": "RKVY Portal",
            "government_level": "Central",
            "state": "All States",
            "department": "Department of Agriculture & Farmers Welfare",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "category": "training",
            "short_description": "Financial grant up to Rs. 5 Lakhs for Agri-Startups, innovation, and farmer processing units.",
            "full_description": "RKVY-RAFTAAR aims at making farming a lucrative economic activity by strengthening infrastructure, post-harvest management, and promoting agri-entrepreneurship and innovation among young farmers.",
            "eligible_states": ["All States"],
            "eligible_farmer_types": ["Small", "Marginal", "Medium", "Large", "Agri-Entrepreneurs", "FPOs"],
            "eligible_crops": ["All Crops"],
            "min_age": 18,
            "max_age": 60,
            "gender_req": "All",
            "eligibility_summary": "Farmers, FPOs, and youth introducing innovation, processing, or organic farming infrastructure.",
            "benefit_type": "financial",
            "benefit_amount": "Seed funding up to Rs. 5 Lakhs to Rs. 25 Lakhs grant",
            "benefit_description": "Incubation support, business mentoring, and financial grants for setting up agri-business/processing units.",
            "required_documents": ["Aadhaar Card", "PAN Card", "Agri Business Proposal", "Bank Account Details"],
            "application_process": "Submit project proposal to RKVY Knowledge Partners / State Agriculture University Incubation Centre.",
            "application_url": "https://rkvy.nic.in/",
            "official_website": "https://rkvy.nic.in/",
            "helpline_number": "011-23383916",
            "helpline_email": "rkvy-agri@gov.in",
            "last_updated_date": "2026-05-30",
            "tags": ["agri startup", "innovation grant", "processing unit", "rkvy"]
        }
    ]

    async def initialize_schemes(self, db: AsyncSession) -> None:
        """Initialize and sync government schemes in the database."""
        list_fields = ["eligible_states", "eligible_farmer_types", "eligible_crops", "required_documents", "tags"]
        for scheme_data in self.DEFAULT_SCHEMES:
            result = await db.execute(
                select(GovernmentScheme).where(GovernmentScheme.scheme_code == scheme_data["scheme_code"])
            )
            existing = result.scalar_one_or_none()

            data = scheme_data.copy()
            for field in list_fields:
                if field in data and isinstance(data[field], list):
                    data[field] = json.dumps(data[field])

            if not existing:
                scheme = GovernmentScheme(**data)
                db.add(scheme)
                logger.info(f"Added scheme: {scheme_data['name']}")
            else:
                for key, val in data.items():
                    setattr(existing, key, val)

        await db.commit()

    async def get_schemes(
        self,
        db: AsyncSession,
        state: Optional[str] = None,
        farmer_type: Optional[str] = None,
        crop: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[GovernmentScheme]:
        """Get schemes with filtering."""
        query = select(GovernmentScheme).where(GovernmentScheme.is_active == True)

        if state and state != "All States":
            query = query.where(
                or_(
                    GovernmentScheme.eligible_states.contains(state),
                    GovernmentScheme.eligible_states.contains("All States"),
                    GovernmentScheme.state == "All States",
                    GovernmentScheme.state == state
                )
            )

        if farmer_type:
            query = query.where(
                or_(
                    GovernmentScheme.eligible_farmer_types.contains(farmer_type),
                    GovernmentScheme.eligible_farmer_types.contains("All Farmers")
                )
            )

        if crop:
            query = query.where(
                or_(
                    GovernmentScheme.eligible_crops.contains(crop),
                    GovernmentScheme.eligible_crops.contains("All Crops")
                )
            )

        if source:
            query = query.where(GovernmentScheme.source.ilike(f"%{source}%"))

        if category:
            query = query.where(GovernmentScheme.category == category)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    GovernmentScheme.name.ilike(search_term),
                    GovernmentScheme.short_description.ilike(search_term),
                    GovernmentScheme.full_description.ilike(search_term),
                    GovernmentScheme.tags.contains(search)
                )
            )

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_scheme_by_id(self, db: AsyncSession, scheme_id: int) -> Optional[GovernmentScheme]:
        """Get scheme by ID."""
        result = await db.execute(
            select(GovernmentScheme).where(
                and_(
                    GovernmentScheme.id == scheme_id,
                    GovernmentScheme.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def search_schemes(
        self,
        db: AsyncSession,
        query_text: str,
        state: Optional[str] = None,
        crop: Optional[str] = None
    ) -> List[GovernmentScheme]:
        return await self.get_schemes(db=db, state=state, crop=crop, search=query_text, limit=50)

    def parse_json_list(self, field_val: Optional[str]) -> List[str]:
        """Utility to safely parse JSON strings or return list."""
        if not field_val:
            return []
        if isinstance(field_val, list):
            return field_val
        try:
            val = json.loads(field_val)
            return val if isinstance(val, list) else [str(val)]
        except Exception:
            return [s.strip() for s in field_val.split(",") if s.strip()]

    def format_scheme_detail(self, scheme: GovernmentScheme) -> SchemeDetailResponse:
        """Format GovernmentScheme model to SchemeDetailResponse pydantic schema."""
        return SchemeDetailResponse(
            id=scheme.id,
            scheme_code=scheme.scheme_code,
            name=scheme.name,
            short_description=scheme.short_description,
            full_description=scheme.full_description,
            source=scheme.source,
            government_level=scheme.government_level or "Central",
            state=scheme.state or "All States",
            department=scheme.department,
            ministry=scheme.ministry,
            category=scheme.category or "subsidy",
            eligible_states=self.parse_json_list(scheme.eligible_states),
            eligible_farmer_types=self.parse_json_list(scheme.eligible_farmer_types),
            eligible_crops=self.parse_json_list(scheme.eligible_crops),
            benefit_type=scheme.benefit_type,
            benefit_amount=scheme.benefit_amount,
            benefit_description=scheme.benefit_description,
            min_age=scheme.min_age,
            max_age=scheme.max_age,
            gender_req=scheme.gender_req or "All",
            min_land_holding=scheme.min_land_holding,
            max_land_holding=scheme.max_land_holding,
            max_income=scheme.max_income,
            income_criteria=scheme.income_criteria,
            irrigation_req=scheme.irrigation_req,
            eligibility_summary=scheme.eligibility_summary,
            required_documents=self.parse_json_list(scheme.required_documents),
            application_process=scheme.application_process,
            application_url=scheme.application_url,
            offline_application_office=scheme.offline_application_office,
            official_website=scheme.official_website,
            helpline_number=scheme.helpline_number,
            helpline_email=scheme.helpline_email,
            start_date=scheme.start_date,
            end_date=scheme.end_date,
            is_active=scheme.is_active,
            last_updated_date=scheme.last_updated_date or "2026-08-01",
            tags=self.parse_json_list(scheme.tags)
        )

    async def recommend_schemes_for_farmer(
        self,
        db: AsyncSession,
        profile: FarmerProfile
    ) -> SchemeRecommendationResponse:
        """Core Eligibility Engine: Compares farmer profile against scheme rules."""
        result = await db.execute(select(GovernmentScheme).where(GovernmentScheme.is_active == True))
        all_schemes = result.scalars().all()

        farmer_crops = self.parse_json_list(profile.crops_grown)
        farmer_state = (profile.state or "Karnataka").strip()
        farmer_category = (profile.farmer_category or "Small").strip()
        land_size = profile.land_size if profile.land_size is not None else 1.5
        farmer_age = profile.age or 35
        farmer_gender = (profile.gender or "Male").strip()
        farmer_income = profile.annual_income or 180000.0
        irrigation = (profile.irrigation_type or "Well").strip()

        recommendations: List[SchemeRecommendationItem] = []
        eligible_cnt = 0
        partial_cnt = 0
        not_eligible_cnt = 0

        for scheme in all_schemes:
            match_reasons = []
            missing_criteria = []
            score = 100

            eligible_states = self.parse_json_list(scheme.eligible_states)
            eligible_types = self.parse_json_list(scheme.eligible_farmer_types)
            eligible_crops = self.parse_json_list(scheme.eligible_crops)

            # 1. State check
            if "All States" in eligible_states or scheme.state == "All States" or farmer_state in eligible_states or scheme.state == farmer_state:
                match_reasons.append(f"Available in your state ({farmer_state})")
            else:
                score -= 40
                missing_criteria.append(f"Restricted to {scheme.state or ', '.join(eligible_states)} (Your state: {farmer_state})")

            # 2. Farmer Category check
            if "All Farmers" in eligible_types or farmer_category in eligible_types:
                match_reasons.append(f"Applies to {farmer_category} farmers")
            else:
                score -= 25
                missing_criteria.append(f"Requires farmer category in {', '.join(eligible_types)} (You: {farmer_category})")

            # 3. Land Holding check
            if scheme.max_land_holding is not None and land_size > scheme.max_land_holding:
                score -= 30
                missing_criteria.append(f"Max land holding limit is {scheme.max_land_holding} Ha (Your land: {land_size} Ha)")
            elif scheme.min_land_holding is not None and land_size < scheme.min_land_holding:
                score -= 20
                missing_criteria.append(f"Min land holding requirement is {scheme.min_land_holding} Ha (Your land: {land_size} Ha)")
            else:
                match_reasons.append(f"Land holding ({land_size} Ha) meets criteria")

            # 4. Crop check
            if "All Crops" in eligible_crops:
                match_reasons.append("Covers all crops")
            elif farmer_crops and any(c.lower() in [ec.lower() for ec in eligible_crops] for c in farmer_crops):
                matched_c = [c for c in farmer_crops if any(c.lower() in ec.lower() for ec in eligible_crops)]
                match_reasons.append(f"Covers your grown crops ({', '.join(matched_c)})")
            else:
                score -= 15
                missing_criteria.append(f"Specific to crops: {', '.join(eligible_crops)}")

            # 5. Age check
            if scheme.min_age and farmer_age < scheme.min_age:
                score -= 20
                missing_criteria.append(f"Minimum age requirement is {scheme.min_age} years")
            elif scheme.max_age and farmer_age > scheme.max_age:
                score -= 20
                missing_criteria.append(f"Maximum age limit is {scheme.max_age} years")

            # 6. Gender check
            if scheme.gender_req and scheme.gender_req != "All" and scheme.gender_req.lower() != farmer_gender.lower():
                score -= 20
                missing_criteria.append(f"Targeted for {scheme.gender_req} farmers")

            # Determine match status badge
            if score >= 90 and len(missing_criteria) == 0:
                status_label = "Eligible"
                eligible_cnt += 1
            elif score >= 50 and len(missing_criteria) <= 2:
                status_label = "Partially matching"
                partial_cnt += 1
            else:
                status_label = "Not eligible"
                not_eligible_cnt += 1

            detail_schema = self.format_scheme_detail(scheme)
            docs = self.parse_json_list(scheme.required_documents)

            recommendations.append(SchemeRecommendationItem(
                scheme=detail_schema,
                status=status_label,
                match_score=max(0, score),
                match_reasons=match_reasons,
                missing_criteria=missing_criteria,
                required_documents=docs,
                disclaimer="Final eligibility is subject to verification by the concerned government department."
            ))

        # Sort recommendations: Eligible first, then Partially matching, then Not eligible (and by match score descending)
        status_rank = {"Eligible": 0, "Partially matching": 1, "Not eligible": 2}
        recommendations.sort(key=lambda x: (status_rank[x.status], -x.match_score))

        return SchemeRecommendationResponse(
            farmer_id=profile.user_id,
            farmer_name=profile.full_name or "Farmer",
            total_schemes=len(all_schemes),
            eligible_count=eligible_cnt,
            partial_count=partial_cnt,
            not_eligible_count=not_eligible_cnt,
            recommendations=recommendations,
            disclaimer="Recommendations are generated based on stored farmer profile information. Final approval is subject to verification by the concerned government department."
        )


scheme_service = SchemeService()
