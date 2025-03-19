# Global feature definitions (avoiding repetition)
FEATURES = {
    "AI_NODE": "🤖 AI Node",
    "META_ADS": "📈 Meta Ads",
    "HUBSPOT_SIDE_PANEL": "💾 HubSpot Panel",
    "HUBSPOT_CUSTOM_EVENTS": "🔔 HubSpot Events",
    "DYNAMIC_WHATSAPP_FLOWS": "🔄 WhatsApp Flows",
}

COUNTRY_FEATURES = {
    "CO": {"AI_NODE", "HUBSPOT_SIDE_PANEL", "HUBSPOT_CUSTOM_EVENTS", "DYNAMIC_WHATSAPP_FLOWS"},
    "CL": {"AI_NODE", "META_ADS", "DYNAMIC_WHATSAPP_FLOWS"},
    "MX": {"AI_NODE", "META_ADS", "DYNAMIC_WHATSAPP_FLOWS", "HUBSPOT_SIDE_PANEL"},
    "DEFAULT": {"HUBSPOT_SIDE_PANEL", "HUBSPOT_CUSTOM_EVENTS", "DYNAMIC_WHATSAPP_FLOWS"},
}
