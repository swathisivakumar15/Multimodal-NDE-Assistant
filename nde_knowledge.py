import logging
from openai_service import chat_with_nde_assistant

# NDE Standards and Documentation Database
NDE_STANDARDS = {
    "ASME": {
        "BPVC": "ASME Boiler and Pressure Vessel Code",
        "Section V": "Nondestructive Examination",
        "Section VIII": "Rules for Construction of Pressure Vessels",
        "Section XI": "Rules for Inservice Inspection of Nuclear Power Plant Components"
    },
    "ASTM": {
        "E94": "Standard Guide for Radiographic Examination",
        "E114": "Standard Practice for Ultrasonic Pulse-Echo Straight-Beam Contact Testing",
        "E165": "Standard Practice for Liquid Penetrant Examination",
        "E709": "Standard Guide for Magnetic Particle Testing",
        "E1444": "Standard Practice for Magnetic Particle Testing",
        "E1316": "Standard Terminology for Nondestructive Examinations"
    },
    "AWS": {
        "D1.1": "Structural Welding Code - Steel",
        "D1.5": "Bridge Welding Code",
        "B1.10": "Guide for the Nondestructive Examination of Welds",
        "B1.11": "Guide for the Visual Examination of Welds"
    },
    "API": {
        "API 510": "Pressure Vessel Inspection Code",
        "API 570": "Piping Inspection Code",
        "API 653": "Tank Inspection, Repair, Alteration, and Reconstruction",
        "API 1104": "Welding of Pipelines and Related Facilities"
    },
    "ISO": {
        "ISO 9712": "Non-destructive testing - Qualification and certification of NDT personnel",
        "ISO 17640": "Non-destructive testing of welds - Ultrasonic testing",
        "ISO 17636": "Non-destructive testing of welds - Radiographic testing"
    }
}

NDE_METHODS = {
    "Ultrasonic Testing (UT)": {
        "description": "Uses high-frequency sound waves to detect internal defects",
        "applications": ["Thickness measurement", "Flaw detection", "Material characterization"],
        "advantages": ["Deep penetration", "High sensitivity", "Real-time results"],
        "limitations": ["Requires coupling medium", "Complex geometries challenging", "Skilled operator needed"]
    },
    "Radiographic Testing (RT)": {
        "description": "Uses X-rays or gamma rays to create images of internal structure",
        "applications": ["Weld inspection", "Casting examination", "Pipeline inspection"],
        "advantages": ["Permanent record", "Good for complex geometries", "Detects internal defects"],
        "limitations": ["Radiation safety concerns", "Access to both sides needed", "Expensive equipment"]
    },
    "Magnetic Particle Testing (MT)": {
        "description": "Uses magnetic fields to detect surface and near-surface discontinuities",
        "applications": ["Crack detection", "Weld inspection", "Component inspection"],
        "advantages": ["Fast inspection", "Low cost", "Easy to interpret"],
        "limitations": ["Ferromagnetic materials only", "Surface preparation required", "Limited depth"]
    },
    "Liquid Penetrant Testing (PT)": {
        "description": "Uses liquid penetrants to detect surface-breaking defects",
        "applications": ["Crack detection", "Porosity detection", "Leak detection"],
        "advantages": ["Simple process", "Low cost", "Works on any material"],
        "limitations": ["Surface defects only", "Clean surface required", "Multiple steps"]
    },
    "Eddy Current Testing (ET)": {
        "description": "Uses electromagnetic induction to detect defects and measure properties",
        "applications": ["Tube inspection", "Crack detection", "Conductivity measurement"],
        "advantages": ["No coupling required", "Fast inspection", "Automated systems"],
        "limitations": ["Conductive materials only", "Limited depth", "Complex interpretation"]
    },
    "Visual Testing (VT)": {
        "description": "Direct visual examination of surfaces and components",
        "applications": ["General inspection", "Weld quality", "Surface condition"],
        "advantages": ["Simple and fast", "Low cost", "No special equipment"],
        "limitations": ["Surface defects only", "Subjective interpretation", "Lighting dependent"]
    }
}

NDE_CERTIFICATIONS = {
    "ASNT": {
        "SNT-TC-1A": "Personnel Qualification and Certification in Nondestructive Testing",
        "CP-189": "ASNT Standard for Qualification and Certification of Nondestructive Testing Personnel"
    },
    "ACCP": {
        "Description": "ASNT Central Certification Program",
        "Levels": ["Level I", "Level II", "Level III"]
    },
    "EN ISO 9712": {
        "Description": "European standard for NDT personnel certification",
        "Requirements": "Harmonized with international standards"
    }
}

def get_nde_suggestions():
    """Get expert suggestions for NDE methods and best practices"""
    try:
        suggestions = [
            {
                "category": "Method Selection",
                "title": "Ultrasonic Testing for Thick Sections",
                "description": "Use UT for components > 2 inches thick where RT becomes impractical",
                "standards": ["ASME Section V", "ASTM E114"]
            },
            {
                "category": "Quality Assurance",
                "title": "Calibration Block Requirements", 
                "description": "Use appropriate calibration standards for each testing method",
                "standards": ["ASTM E164", "ASME Section V"]
            },
            {
                "category": "Safety",
                "title": "Radiation Safety Protocol",
                "description": "Implement ALARA principles for radiographic testing operations",
                "standards": ["10 CFR 20", "ASME Section V"]
            },
            {
                "category": "Documentation",
                "title": "Inspection Report Requirements",
                "description": "Include all required elements per applicable codes and standards",
                "standards": ["API 510", "ASME Section XI"]
            },
            {
                "category": "Training",
                "title": "Personnel Certification",
                "description": "Ensure inspectors meet SNT-TC-1A or CP-189 requirements",
                "standards": ["SNT-TC-1A", "ASNT CP-189"]
            },
            {
                "category": "Equipment",
                "title": "Calibration and Verification",
                "description": "Regular calibration of NDE equipment per manufacturer specifications",
                "standards": ["ASTM E543", "ASME Section V"]
            }
        ]
        
        return suggestions
        
    except Exception as e:
        logging.error(f"Error getting NDE suggestions: {str(e)}")
        return []

def search_nde_standards(query):
    """Search NDE standards and documentation based on query"""
    try:
        query_lower = query.lower()
        results = []
        
        # Search through standards
        for organization, standards in NDE_STANDARDS.items():
            for code, description in standards.items():
                if (query_lower in code.lower() or 
                    query_lower in description.lower() or
                    any(term in description.lower() for term in query_lower.split())):
                    results.append({
                        "type": "standard",
                        "organization": organization,
                        "code": code,
                        "description": description,
                        "relevance": "high" if query_lower in code.lower() else "medium"
                    })
        
        # Search through methods
        for method, details in NDE_METHODS.items():
            if (query_lower in method.lower() or 
                query_lower in details["description"].lower() or
                any(query_lower in app.lower() for app in details["applications"])):
                results.append({
                    "type": "method",
                    "name": method,
                    "description": details["description"],
                    "applications": details["applications"],
                    "relevance": "high" if query_lower in method.lower() else "medium"
                })
        
        # Sort by relevance
        results.sort(key=lambda x: 0 if x["relevance"] == "high" else 1)
        
        return results[:10]  # Return top 10 results
        
    except Exception as e:
        logging.error(f"Error searching NDE standards: {str(e)}")
        return []

def get_method_details(method_name):
    """Get detailed information about a specific NDE method"""
    try:
        for method, details in NDE_METHODS.items():
            if method_name.lower() in method.lower():
                return {
                    "method": method,
                    "details": details,
                    "related_standards": get_related_standards(method),
                    "typical_procedures": get_typical_procedures(method)
                }
        
        return None
        
    except Exception as e:
        logging.error(f"Error getting method details: {str(e)}")
        return None

def get_related_standards(method):
    """Get standards related to a specific NDE method"""
    method_standards = {
        "Ultrasonic": ["ASTM E114", "ASTM E317", "ASME Section V Article 4"],
        "Radiographic": ["ASTM E94", "ASTM E142", "ASME Section V Article 2"],
        "Magnetic Particle": ["ASTM E709", "ASTM E1444", "ASME Section V Article 7"],
        "Liquid Penetrant": ["ASTM E165", "ASTM E1417", "ASME Section V Article 6"],
        "Eddy Current": ["ASTM E309", "ASTM E426", "ASME Section V Article 8"],
        "Visual": ["ASTM E165", "AWS B1.11", "ASME Section V Article 9"]
    }
    
    for key, standards in method_standards.items():
        if key.lower() in method.lower():
            return standards
    
    return []

def get_typical_procedures(method):
    """Get typical procedures for a specific NDE method"""
    procedures = {
        "Ultrasonic": [
            "Equipment calibration and verification",
            "Surface preparation and coupling",
            "Systematic scanning with proper overlap",
            "Signal evaluation and interpretation",
            "Documentation of findings"
        ],
        "Radiographic": [
            "Radiation safety setup and verification", 
            "Film placement and identification",
            "Exposure parameter calculation",
            "Film processing and evaluation",
            "Image quality indicator verification"
        ],
        "Magnetic Particle": [
            "Surface cleaning and preparation",
            "Magnetization technique selection",
            "Particle application (wet or dry)",
            "Indication evaluation under proper lighting",
            "Demagnetization if required"
        ],
        "Liquid Penetrant": [
            "Surface cleaning and preparation",
            "Penetrant application and dwell time",
            "Excess penetrant removal",
            "Developer application",
            "Indication evaluation and interpretation"
        ],
        "Eddy Current": [
            "Equipment setup and calibration",
            "Probe selection and frequency optimization",
            "Systematic scanning pattern",
            "Signal analysis and interpretation",
            "Correlation with other NDE methods"
        ],
        "Visual": [
            "Lighting setup and verification",
            "Systematic visual examination",
            "Use of visual aids (magnification, mirrors)",
            "Documentation with measurements",
            "Photography of significant findings"
        ]
    }
    
    for key, proc_list in procedures.items():
        if key.lower() in method.lower():
            return proc_list
    
    return []

def get_defect_interpretation_guide(defect_type):
    """Get interpretation guidance for specific defect types"""
    defect_guides = {
        "crack": {
            "description": "Linear discontinuity caused by stress concentration",
            "detection_methods": ["PT", "MT", "UT", "ET"],
            "evaluation_criteria": "Length, depth, orientation relative to stress",
            "acceptance_standards": ["ASME Section VIII", "AWS D1.1", "API 579"]
        },
        "porosity": {
            "description": "Gas entrapment creating spherical voids",
            "detection_methods": ["RT", "UT"],
            "evaluation_criteria": "Size, distribution, percentage of weld area",
            "acceptance_standards": ["AWS D1.1", "ASME Section IX"]
        },
        "inclusion": {
            "description": "Foreign material trapped in weld metal",
            "detection_methods": ["RT", "UT"],
            "evaluation_criteria": "Size, type, location within weld",
            "acceptance_standards": ["AWS D1.1", "ASME Section VIII"]
        },
        "lack_of_fusion": {
            "description": "Incomplete fusion between weld passes or base metal",
            "detection_methods": ["UT", "RT"],
            "evaluation_criteria": "Length, location, depth",
            "acceptance_standards": ["AWS D1.1", "ASME Section IX"]
        }
    }
    
    return defect_guides.get(defect_type.lower(), None)

def generate_inspection_plan(component_type, material, thickness, service_conditions):
    """Generate NDE inspection plan based on component parameters"""
    try:
        prompt = f"""Generate a comprehensive NDE inspection plan for the following component:

Component Type: {component_type}
Material: {material}
Thickness: {thickness}
Service Conditions: {service_conditions}

Include:
1. Recommended NDE methods with justification
2. Applicable codes and standards
3. Inspection sequence and timing
4. Acceptance criteria
5. Personnel qualification requirements
6. Documentation requirements

Provide specific, actionable recommendations suitable for engineering implementation."""

        return chat_with_nde_assistant(prompt)
        
    except Exception as e:
        logging.error(f"Error generating inspection plan: {str(e)}")
        return "Unable to generate inspection plan. Please try again."
