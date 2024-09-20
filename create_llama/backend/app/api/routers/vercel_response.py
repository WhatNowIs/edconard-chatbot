import json
from typing import Any
from fastapi.responses import StreamingResponse


class VercelStreamResponse(StreamingResponse):
    """
    Class to convert the response from the chat engine to the streaming format expected by Vercel
    """

    TEXT_PREFIX = "0:"
    DATA_PREFIX = "8:"

    @classmethod
    def convert_text(cls, token: str):
        # Escape newlines and double quotes to avoid breaking the stream    
        try:
            token = json.dumps(token)
            return f"{cls.TEXT_PREFIX}{token}\n"
        except TypeError as e:
            print(f"Error serializing token: {e}")
            # Handle the error or filter out problematic parts of `data`
            # For example, you could remove non-serializable items
            # or log them for further inspection.
            return str(token)

    @classmethod
    def convert_data(cls, data: dict):
        try:
            data_str = json.dumps(data)
            return f"{cls.DATA_PREFIX}[{data_str}]\n"
        except TypeError as e:
            print(f"Error serializing data: {e}")
            # Handle the error or filter out problematic parts of `data`
            # For example, you could remove non-serializable items
            # or log them for further inspection.
            return str(data)

    def __init__(self, content: Any, **kwargs):
        super().__init__(
            content=content,
            **kwargs,
        )
