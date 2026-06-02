from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, ConversationHandler

from bot.webhook_client import trigger_workflow
from utils.formatter import split_message
from utils.logger import logger

# Conversation states
COLLECT_START = 0
COLLECT_DEST = 1
COLLECT_DATES = 2
COLLECT_BUDGET = 3
COLLECT_TRANSPORT = 4
COLLECT_STYLE = 5


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — greet user and ask for origin."""
    context.user_data.clear()
    await update.message.reply_text(
        "✈️ Welcome to SkyStride AI!\n\n"
        "Let's build your personalised trip blueprint step by step.\n\n"
        "📍 Where are you departing from? (e.g. Hyderabad, India)"
    )
    return COLLECT_START


async def collect_dest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store origin, ask for destination."""
    context.user_data["origin"] = update.message.text.strip()
    logger.info("User %s set origin: %s", update.effective_user.id, context.user_data["origin"])
    await update.message.reply_text(
        "🏁 Got it! What's your final destination? (e.g. Goa, India)"
    )
    return COLLECT_DEST


async def collect_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store destination, ask for trip duration/dates."""
    context.user_data["destination"] = update.message.text.strip()
    logger.info("User %s set destination: %s", update.effective_user.id, context.user_data["destination"])
    await update.message.reply_text(
        "📅 How many days is your trip? (e.g. 3 days, or Jun 15–18)"
    )
    return COLLECT_DATES


async def collect_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store dates, ask for budget."""
    context.user_data["dates"] = update.message.text.strip()
    logger.info("User %s set dates: %s", update.effective_user.id, context.user_data["dates"])
    await update.message.reply_text(
        "💰 What's your total budget? Include currency symbol (e.g. ₹8000 or $150)"
    )
    return COLLECT_BUDGET


async def collect_transport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store budget, ask for transport mode."""
    context.user_data["budget"] = update.message.text.strip()
    logger.info("User %s set budget: %s", update.effective_user.id, context.user_data["budget"])
    await update.message.reply_text(
        "🚗 Mode of transport? (e.g. driving, train, bus, flight)"
    )
    return COLLECT_TRANSPORT


async def collect_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store transport (if in COLLECT_TRANSPORT state) or style (if in COLLECT_STYLE state),
    then either ask for style or trigger the workflow."""

    # Determine which field we're collecting based on what's already stored
    if "transport" not in context.user_data:
        # We were called from COLLECT_TRANSPORT state
        context.user_data["transport"] = update.message.text.strip()
        logger.info("User %s set transport: %s", update.effective_user.id, context.user_data["transport"])
        await update.message.reply_text(
            "🎯 Last one! Any travel preferences?\n"
            "(e.g. scenic route, foodie, historical, adventure, fast travel)"
        )
        return COLLECT_STYLE
    else:
        # We were called from COLLECT_STYLE state
        context.user_data["style"] = update.message.text.strip()
        logger.info("User %s set style: %s", update.effective_user.id, context.user_data["style"])
        return await _generate_blueprint(update, context)


async def _generate_blueprint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Trigger n8n workflow and return the blueprint to the user."""
    await update.message.reply_text(
        "⚙️ Perfect! Sending your trip data to SkyStride AI...\n\n"
        "🔄 Generating blueprint (10–20 seconds)..."
    )

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    trip_params = {
        "origin": context.user_data.get("origin", ""),
        "destination": context.user_data.get("destination", ""),
        "dates": context.user_data.get("dates", ""),
        "budget": context.user_data.get("budget", ""),
        "transport": context.user_data.get("transport", ""),
        "style": context.user_data.get("style", ""),
    }

    logger.info(
        "Triggering n8n workflow for user %s with params: %s",
        update.effective_user.id,
        trip_params,
    )

    blueprint = await trigger_workflow(trip_params)

    if blueprint and isinstance(blueprint, str):
        chunks = split_message(blueprint)
        for chunk in chunks:
            await update.message.reply_text(chunk)
        logger.info(
            "Blueprint delivered to user %s in %d chunk(s)",
            update.effective_user.id,
            len(chunks),
        )
    else:
        await update.message.reply_text(
            "⚠️ Blueprint generation failed. Please try /start again."
        )
        logger.error("Blueprint generation failed for user %s", update.effective_user.id)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current conversation."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Trip planning cancelled. Send /start to begin a new trip."
    )
    logger.info("User %s cancelled the conversation.", update.effective_user.id)
    return ConversationHandler.END
