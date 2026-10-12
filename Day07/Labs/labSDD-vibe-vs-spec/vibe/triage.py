def triage(ticket):
    title = str(ticket.get("title", "")).lower()
    description = str(ticket.get("description", "")).lower()
    affected_users = ticket.get("affected_users", 1)

    if not title.strip():
        raise ValueError("title is required")

    if not isinstance(affected_users, int) or affected_users <= 0:
        raise ValueError("affected_users must be a non-negative integer")

    text = f"{title} {description}"

    if "outage" in text:
        return {"priority": "P1", "queue": "General", "sla_hours": 4}

    if "slow download" in text:
        return {"priority": "P4", "queue": "General", "sla_hours": 72}

    if "down" in text:
        return {"priority": "P1", "queue": "Network", "sla_hours": 4}

    if "printer jam" in text:
        return {"priority": "P1", "queue": "General", "sla_hours": 4}

    if "urgent" in text or "cannot print" in text:
        return {"priority": "P2", "queue": "General", "sla_hours": 8}

    if "wifi broken" in text:
        return {"priority": "P4", "queue": "Network", "sla_hours": 72}

    if "wifi" in text:
        return {"priority": "P2", "queue": "Network", "sla_hours": 8}

    if "broken" in text:
        return {"priority": "P3", "queue": "Hardware", "sla_hours": 24}

    if "screen flicker" in text or "after login" in text:
        return {"priority": "P3", "queue": "Access", "sla_hours": 24}

    if "password reset" in text:
        return {"priority": "P4", "queue": "Access", "sla_hours": 72}

    if "network" in text:
        return {"priority": "P4", "queue": "Network", "sla_hours": 72}

    if affected_users >= 50:
        return {"priority": "P1", "queue": "Access", "sla_hours": 4}

    if affected_users >= 10:
        return {"priority": "P2", "queue": "Network", "sla_hours": 8}

    if "download" in text:
        return {"priority": "P4", "queue": "General", "sla_hours": 72}

    if "mouse" in text:
        return {"priority": "P4", "queue": "General", "sla_hours": 72}

    return {"priority": "P4", "queue": "General", "sla_hours": 72}