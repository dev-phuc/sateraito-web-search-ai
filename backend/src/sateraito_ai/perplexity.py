import json
from typing import Generator, List, Optional, Tuple, Union

import requests
from sateraito_func import format_date

from sateraito_inc import PERPLEXITY_API_KEY
from sateraito_ai.prompt.system_prompt import SYSTEM_PROMPT_DEFAULT
from sateraito_logger import logging

PERPLEXITY_API_COMPLETION_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_HEADERS = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}"}
PERPLEXITY_API_MODEL_DEFAULT = "sonar"

PERPLEXITY_API_DATE_FORMAT = "%m/%d/%Y"

class PerplexityAI:
    """Clean wrapper for Perplexity AI chat completions.

    - Adds type hints and logging.
    - Improves network error handling (timeout, raise_for_status).
    - Stream: returns a generator that yields text fragments (delta content).

    Usage:
        text, citations = ai.chat_completion("Hello")          # non-stream
        gen, _ = ai.chat_completion("Hello", stream=True)      # stream
    """

    url: str = PERPLEXITY_API_COMPLETION_URL
    headers = PERPLEXITY_API_HEADERS
    model: str = PERPLEXITY_API_MODEL_DEFAULT
    system_message: str = SYSTEM_PROMPT_DEFAULT

    def __init__(self) -> None:
        pass
    
    def build_requests_post(self, **kwargs) -> requests.Response:
        """Builds a requests.post call with the given parameters."""
        return requests.post(self.url, headers=self.headers, **kwargs)
    
    def build_payload(self, **kwargs) -> dict:
        """Builds the payload for the chat completion request."""

        self.model = kwargs.get("model_name", self.model)

        messages = []

        system_message = kwargs.get("system_message", None)
        if system_message:
            messages.append({"role": "system", "content": system_message})

        history = kwargs.get("history", [])
        if history:
            for item in history:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    messages.append(item)
                else:
                    logging.warning("Invalid history message format: %s", item)

        max_tokens = kwargs.get("max_tokens", None)
        if max_tokens is not None:
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                raise ValueError("max_tokens must be a positive integer.")
            
        user_location = kwargs.get("user_location", None)
        if user_location and not isinstance(user_location, dict):
            raise ValueError("user_location must be a dictionary with location details.")
            
        query = kwargs.get("query", None)
        if not query:
            raise ValueError("Query must be provided for chat completion.")
        
        images = kwargs.get("images", [])
        if images:
            # Image Guide
            # https://docs.perplexity.ai/guides/image-guide
            if not isinstance(images, list):
                raise ValueError("images must be a list of image URLs.")
            if not all(isinstance(image, str) for image in images):
                raise ValueError("All items in images must be strings representing URLs.")
            
            user_content = []
            user_content.append({"role": "user", "content": query})
            for image in images:
                user_content.append({"type": "image_url", "image_url": {"url": image}})
        else:
            messages.append({"role": "user", "content": query})

        # Image Filters Guide
        # https://docs.perplexity.ai/guides/image-filter-guide
        return_images = kwargs.get("return_images", False)
        if return_images and not isinstance(return_images, bool):
            raise ValueError("return_images must be a boolean value.")
        image_domain_filter = kwargs.get("image_domain_filter", None)
        if image_domain_filter is not None and not isinstance(image_domain_filter, list):
            raise ValueError("image_domain_filter must be a list of strings.")       

        # Search Domain Filter Guide
        # https://docs.perplexity.ai/guides/search-domain-filters
        search_domain_filter = kwargs.get("search_domain_filter", None)
        if search_domain_filter is not None and not isinstance(search_domain_filter, list):
            raise ValueError("search_domain_filter must be a list of strings.")
        
        # Structured Outputs Guide
        # https://docs.perplexity.ai/guides/structured-outputs
        response_format = kwargs.get("response_format", None)
        if response_format is not None and not isinstance(response_format, dict):
            raise ValueError("json_schema must be a dictionary representing the JSON schema.")
        
        # Academic Filter Guide
        # https://docs.perplexity.ai/guides/academic-filter-guide
        search_mode = kwargs.get("search_mode", None)
        if search_mode and search_mode not in ["academic", "sec"]:
            raise ValueError("search_mode must be either 'academic'.")

        # Search Context Size
        # https://docs.perplexity.ai/guides/search-context-size-guide
        search_context_size = kwargs.get("search_context_size", None)
        if search_context_size and search_context_size not in ["low", "medium", "high"]:
            raise ValueError("search_context_size must be one of 'low', 'medium', 'high'.")
        
        # Disabling Search Completely
        # https://docs.perplexity.ai/guides/search-control-guide
        disable_search = kwargs.get("disable_search", False)
        if disable_search and not isinstance(disable_search, bool):
            raise ValueError("disable_search must be a boolean value.")
        
        # Date and Time Filter Guide
        # https://docs.perplexity.ai/guides/date-range-filter-guide
        search_after_date_filter = kwargs.get("search_after_date_filter", None)
        if search_after_date_filter and not isinstance(search_after_date_filter, str):
            raise ValueError("search_after_date_filter must be a string in ISO format m/d/Y.")
        last_updated_after_filter = kwargs.get("last_updated_after_filter", None)
        if last_updated_after_filter and not isinstance(last_updated_after_filter, str):
            raise ValueError("last_updated_after_filter must be a string in ISO format m/d/Y.")
        search_recency_filter = kwargs.get("search_recency_filter", None)
        if search_recency_filter and web_search_options not in ["day", "week", "month", "year"]:
            raise ValueError("web_search_options must be one of 'day', 'week', 'month', 'year'.")
        
        web_search_options = kwargs.get("web_search_options", None)
        if web_search_options and not isinstance(web_search_options, dict):
            raise ValueError("web_search_options must be a dictionary with search options.")
        
        if search_context_size:
            if web_search_options:
                web_search_options = web_search_options['search_context_size'] = search_context_size
            else:
                web_search_options = {"search_context_size": search_context_size}

        # Build the payload for the API request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": kwargs.get("stream", False),
        }

        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if user_location is not None:
            payload["user_location"] = user_location
        if search_domain_filter:
            payload["search_domain_filter"] = search_domain_filter
        if response_format:
            payload["response_format"] = response_format
        if search_mode:
            payload["search_mode"] = search_mode
        if disable_search:
            payload["disable_search"] = disable_search
        if search_after_date_filter:
            payload["search_after_date_filter"] = format_date(search_after_date_filter, format=PERPLEXITY_API_DATE_FORMAT)
        if last_updated_after_filter:
            payload["last_updated_after_filter"] = format_date(last_updated_after_filter, format=PERPLEXITY_API_DATE_FORMAT)
        if search_recency_filter:
            payload["search_recency_filter"] = format_date(search_recency_filter, format=PERPLEXITY_API_DATE_FORMAT)
        if web_search_options:
            payload["web_search_options"] = web_search_options
        
        logging.info("Building payload for Perplexity AI: %s", payload)

        return payload

    def handle_stream_response(self, res: requests.Response) -> Generator[str, None, None]:
        """Handles the streaming response from Perplexity AI."""

        metadata = {}

        def generate() -> Generator[str, None, None]:
            try:
                event_id = 0
                for raw in res.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    line = raw.strip()
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            obj = json.loads(data)
                        except json.JSONDecodeError:
                            logging.warning("Failed to parse JSON from stream line: %s", data)
                            continue

                        # Get the content from the first choice
                        choices = obj.get("choices") or []
                        if choices:
                            delta = choices[0].get("delta", {})
                            content_piece = delta.get("content")
                            if content_piece:
                                yield {
                                    "id": event_id,
                                    "event": "message",
                                    "data": content_piece
                                }
                                event_id += 1

                        for key in ['search_results', 'usage']:
                            if key in obj:
                                metadata[key] = obj[key]

                # End of generator
            finally:
                # Close the response if needed
                try:
                    res.close()
                except Exception:
                    pass
            
            yield {
                "id": event_id,
                "event": "metadata",
                "data": metadata
            }

        return generate
    
    def handle_non_stream_response(self, res: requests.Response) -> Tuple[Optional[str], List[dict]]:
        """Handles the non-streaming response from Perplexity AI."""
        data = res.json()
        choices = data.get("choices") or []
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message") or {}
            content = message.get("content")
        else:
            content = None

        citations = data.get("citations", []) if isinstance(data, dict) else []
        return content, citations

    def chat_completion(
        self, query: str,
        stream: bool = False, timeout: int = 30,
        **kwargs,
    ) -> Union[Tuple[Optional[str], Optional[List[dict]]], Tuple[Generator[str, None, None], List[dict]]]:
        """ Sends a chat completion request to Perplexity AI.

        Args:
            query: User input text.
            stream: If True, returns a generator that yields delta content.
            timeout: HTTP request timeout in seconds.

        Returns:
            If stream=False: (content, citations) or (None, None) on error.
            If stream=True: (generator, []) - generator yields content fragments (strings).
        """

        try:
            # Call the API with a timeout; if stream=True keep the connection open
            payload = self.build_payload(query=query, stream=stream, **kwargs)
            api_response = self.build_requests_post(json=payload, stream=stream, timeout=timeout)
            api_response.raise_for_status()

            if stream:
                # stream: return a generator that yields text fragments
                return self.handle_stream_response(api_response), []

            else:
                # non-stream: return final content and citations
                return self.handle_non_stream_response(api_response)

        except requests.RequestException as e:
            logging.exception("HTTP error when calling Perplexity API: %s", e)
            return None, None
        except Exception as e:
            logging.exception("Unexpected error in chat_completion: %s", e)
            return None, None
