class ComparisonEngine:
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.cdp_features = {
            "segment": {
                "audience_creation": "User segmentation in Segment is primarily done through Personas. It allows you to create audiences based on user traits and events.",
                "data_collection": "Segment collects data through Sources like websites, mobile apps, servers, and cloud apps using various SDKs and APIs.",
                "integrations": "Segment offers 300+ pre-built integrations called Destinations to send your data to various marketing, analytics, and data warehouse tools.",
                "user_profiles": "Segment Personas creates unified user profiles by merging user identities across devices and channels.",
                "privacy_compliance": "Segment provides tools for GDPR, CCPA, and other privacy regulations compliance through its Privacy Portal."
            },
            "mparticle": {
                "audience_creation": "mParticle's Audience Manager allows you to create segments based on user behaviors, attributes, and calculated values.",
                "data_collection": "mParticle collects data through SDKs for web, mobile, and server-side implementations, as well as through feeds and partner feeds.",
                "integrations": "mParticle offers 250+ integrations with various platforms for data forwarding.",
                "user_profiles": "mParticle creates persistent, cross-channel user profiles with its IDSync feature.",
                "privacy_compliance": "mParticle provides data subject request automation, consent management, and data governance tools."
            },
            "lytics": {
                "audience_creation": "Lytics uses machine learning for audience creation and allows for real-time segmentation based on behavioral data.",
                "data_collection": "Lytics collects data through JavaScript tags, mobile SDKs, server-side APIs, and direct integrations.",
                "integrations": "Lytics offers integrations with major marketing platforms, data warehouses, and analytics tools.",
                "user_profiles": "Lytics builds Identity-resolved profiles that unify user data across touchpoints.",
                "privacy_compliance": "Lytics provides privacy management tools including data subject requests and consent management."
            },
            "zeotap": {
                "audience_creation": "Zeotap's Customer Intelligence Platform allows for audience creation based on first-party data and enriched with additional signals.",
                "data_collection": "Zeotap collects data through SDKs, APIs, and direct integrations with various platforms.",
                "integrations": "Zeotap integrates with major advertising platforms, marketing tools, and analytics systems.",
                "user_profiles": "Zeotap unifies customer identities across channels using its Identity Resolution feature.",
                "privacy_compliance": "Zeotap offers privacy-compliant data collection and management with consent frameworks."
            }
        }
        
    def extract_feature_from_question(self, question):
        """Extract the feature being compared from the question."""
        question_lower = question.lower()
        
        feature_keywords = {
            "audience_creation": ["audience", "segment", "segmentation"],
            "data_collection": ["collect", "gathering", "tracking", "capture"],
            "integrations": ["integrat", "connect", "destination", "connect"],
            "user_profiles": ["profile", "identity", "identities", "user data"],
            "privacy_compliance": ["privacy", "gdpr", "ccpa", "compliance", "consent"],
        }
        
        # Find which feature is most relevant to the question
        best_match = None
        match_count = 0
        
        for feature, keywords in feature_keywords.items():
            current_count = sum(1 for keyword in keywords if keyword in question_lower)
            if current_count > match_count:
                match_count = current_count
                best_match = feature
        
        return best_match
    
    def get_comparison_data(self, question, cdps):
        """Get comparison data for the specified CDPs based on the question."""
        feature = self.extract_feature_from_question(question)
        
        if not feature:
            # If we couldn't extract a specific feature, get general information
            docs = {}
            for cdp in cdps:
                cdp_docs = self.vector_db.similarity_search(
                    question,
                    k=3,
                    filter={"cdp": cdp}
                )
                docs[cdp] = cdp_docs
            return docs
        
        # If we have a specific feature, use our pre-defined comparison data
        # and supplement with retrieved docs
        comparison_data = {}
        
        for cdp in cdps:
            feature_info = self.cdp_features.get(cdp, {}).get(feature, "")
            
            # Get additional information from vector DB
            feature_query = f"{feature} in {cdp}"
            docs = self.vector_db.similarity_search(
                feature_query,
                k=2,
                filter={"cdp": cdp}
            )
            
            doc_texts = [doc.page_content for doc in docs]
            
            comparison_data[cdp] = {
                "feature": feature,
                "summary": feature_info,
                "docs": doc_texts
            }
        
        return comparison_data
