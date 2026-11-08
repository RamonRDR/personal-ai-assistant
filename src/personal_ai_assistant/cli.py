"""Deliberately bound to localhost, not 0.0.0.0."""

import uvicorn


def main():
    uvicorn.run("personal_ai_assistant.api:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
