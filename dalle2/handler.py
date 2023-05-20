import json
import openai


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def handle(event, context):
    try:
        body = json.loads(event.body)
        prompt = body.get("prompt")

        authorization = event.headers.get("Authorization")

        openai.api_key = (
            remove_prefix(authorization, "Bearer ") if authorization else ""
        )

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256",
        )

        return {
            "statusCode": 200,
            "body": {
                "response": response["data"][0]["url"],
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
