import json
import openai


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def handle(event, context):
    try:
        body = json.loads(event.body)
        user_id, chatgpt_bot_id, messages, channel = (
            body.get("user_id"),
            body.get("chatgpt_bot_id"),
            body.get("messages"),
            body.get("channel"),
        )
        authorization = event.headers.get("Authorization")

        openai.api_key = (
            remove_prefix(authorization, "Bearer ") if authorization else ""
        )

        conversationLog = []
        count = 0
        for msg in messages[::-1]:
            # Only get the last 20 messages
            if count == 20:
                break

            author_id = msg.get("author_id")
            content = msg.get("content")

            if str(author_id) == str(chatgpt_bot_id):
                conversationLog.append({"role": "assistant", "content": content})
                count += 1

            elif not channel == "chatgpt" and not content.startswith("!chat"):
                pass

            elif str(author_id) == str(user_id):
                conversationLog.append(
                    {"role": "user", "content": remove_prefix(content, "!chat").strip()}
                )
                count += 1
        conversationLog.reverse()

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversationLog,
        )

        return {
            "statusCode": 200,
            "body": {
                "response": completion.choices[0].message.content,
            },
            "headers": {"Content-Type": "application/json"},
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
            },
            "headers": {"Content-Type": "application/json"},
        }
