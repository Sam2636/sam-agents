# core/openai_utils.py
import time
import openai
import logging

logger = logging.getLogger("OpenAIUtils")
logger.setLevel(logging.INFO)

try:
    from openai.error import RateLimitError, OpenAIError
except ImportError:
    RateLimitError = Exception
    OpenAIError = Exception

def call_openai_with_retry(payload, retries=5):
    """
    Calls OpenAI ChatCompletion with retries on rate limit and transient errors.
    Provides detailed logging for debugging and observability.
    """
    for attempt in range(1, retries + 1):
        try:
            response = openai.ChatCompletion.create(**payload)
            logger.info(f"OpenAI call successful on attempt {attempt}")
            # optionally log token usage if available
            if hasattr(response, "usage"):
                logger.info(f"Token usage: {response.usage}")
            return response

        except RateLimitError as e:
            wait_time = 2 ** (attempt - 1)
            logger.warning(f"[Attempt {attempt}] Rate limit hit, retrying in {wait_time}s... Error: {e}")
            time.sleep(wait_time)

        except OpenAIError as e:
            logger.error(f"[Attempt {attempt}] OpenAI API error: {e}")
            raise

        except Exception as e:
            logger.error(f"[Attempt {attempt}] Unexpected error: {e}")
            raise

    raise Exception(f"Max retries exceeded ({retries}) for OpenAI request")
