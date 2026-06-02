import os
import httpx
from utils.logger import logger

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/skystride-blueprint")


async def trigger_workflow(trip_params: dict) -> str | None:
    """
    POST trip parameters to the n8n webhook and return the generated blueprint text.

    Args:
        trip_params: dict containing origin, destination, dates, budget, transport, style

    Returns:
        Blueprint text string on success, or None on any failure.
    """
    payload = {
        "origin": trip_params.get("origin", ""),
        "destination": trip_params.get("destination", ""),
        "dates": trip_params.get("dates", ""),
        "budget": trip_params.get("budget", ""),
        "transport": trip_params.get("transport", ""),
        "style": trip_params.get("style", ""),
    }

    logger.info("POSTing to n8n webhook: %s | Payload: %s", N8N_WEBHOOK_URL, payload)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

        response.raise_for_status()

        data = response.json()

        if "blueprint" not in data:
            logger.error("n8n response missing 'blueprint' key. Response: %s", data)
            return None

        blueprint = data["blueprint"]
        if not isinstance(blueprint, str) or not blueprint.strip():
            logger.error("n8n returned empty or non-string blueprint: %s", blueprint)
            return None

        logger.info("Blueprint received from n8n (%d characters).", len(blueprint))
        return blueprint

    except httpx.TimeoutException as exc:
        logger.error("n8n webhook request timed out: %s", exc)
        return None
    except httpx.HTTPStatusError as exc:
        logger.error(
            "n8n returned HTTP error %s: %s",
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.RequestError as exc:
        logger.error("n8n webhook connection error: %s", exc)
        return None
    except (ValueError, KeyError) as exc:
        logger.error("Failed to parse n8n response: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error calling n8n webhook: %s", exc)
        return None
