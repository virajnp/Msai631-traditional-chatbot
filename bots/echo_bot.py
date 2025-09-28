# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount


class EchoBot(ActivityHandler):
    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        """
        Runs when a new user joins the conversation.
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Runs for normal chat messages sent by the user.
        """
        user_text_raw = turn_context.activity.text

        # Guard: non-text payloads (some channels can send non-string text)
        if not isinstance(user_text_raw, str):
            await turn_context.send_activity(
                "I received something I couldn't understand as text. "
                "Please type a message like 'help' or 'capabilities'."
            )
            return

        # Normalize whitespace
        user_text = user_text_raw.strip()

        # Empty/whitespace-only input
        if not user_text:
            await turn_context.send_activity(
                "I didn't catch any text. Try 'capabilities' to see what I can do."
            )
            return

        lowered = user_text.lower()

        # Capabilities/help command
        if lowered in {"capabilities", "help", "what can you do"}:
            await turn_context.send_activity(
                "Here’s what I can do right now:\n"
                "• Echo back any message you send.\n"
                "• Reverse text with the command: reverse: <your text>\n"
                "• Handle malformed or empty input politely.\n"
                "Try: reverse: hello world"
            )
            return

        # reverse:<text> command
        if lowered.startswith("reverse:"):
            content = user_text[len("reverse:") :].strip()
            if not content:
                await turn_context.send_activity(
                    "Please provide text after 'reverse:'. For example: reverse: chatbot"
                )
                return
            await turn_context.send_activity(f"Reversed: {content[::-1]}")
            return

        # Default: echo back the message
        await turn_context.send_activity(f"You said: {user_text}")

    async def on_event_activity(self, turn_context: TurnContext):
        """
        Runs for non-message 'event' activities (e.g., Emulator ➜ Custom activity).
        """
        await turn_context.send_activity(
            "I received something I couldn't understand as text. "
            "Please type a message like 'help' or 'capabilities'."
        )
        return

    async def on_unrecognized_activity_type(self, turn_context: TurnContext):
        """
        Fallback for activity types not explicitly handled.
        Useful to see what's coming in from the Emulator.
        """
        await turn_context.send_activity(
            f"Received a non-message activity of type: {turn_context.activity.type}"
        )
        return

    async def on_turn(self, turn_context: TurnContext):
        """
        Debug hook: prints every activity type to the terminal, then lets the
        base class route to the right handler.
        """
        print("Activity type:", getattr(turn_context.activity, "type", None))
        await super().on_turn(turn_context)
