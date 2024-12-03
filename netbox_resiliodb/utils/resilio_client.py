import hashlib
import json
import logging
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

from ..models import PluginSettings, LCACache

logger = logging.getLogger(__name__)

class ResilioDBClient:
    """
    Client for interacting with ResilioDB API
    """
    def __init__(self):
        self.settings = PluginSettings.objects.first()
        if not self.settings:
            raise ValueError("ResilioDB plugin settings not configured")

        self.base_url = self.settings.api_url.rstrip('/')
        self.api_key = self.settings.api_key
        self.api_version = self.settings.api_version

    def _get_headers(self):
        """Get headers with valid access token"""
        access_token = self._ensure_valid_token()
        return {
            'Content-Type': 'application/json',
            'Authorization': access_token
        }

    def _ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if needed"""
        now = timezone.now()

        # Check if token is still valid
        if (self.settings.access_token and self.settings.access_token_expiry
            and self.settings.access_token_expiry > now):
            return self.settings.access_token

        # Need to get new token
        try:
            # Configure session without system proxy
            session = requests.Session()
            session.trust_env = False  # Don't use system proxy settings

            response = session.post(
                f"{self.base_url}/api/login",
                json={"secretAccessToken": self.api_key},
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()

            # Save new token
            self.settings.access_token = response.json()['accessToken']
            self.settings.access_token_expiry = now + timedelta(hours=23)  # 23 hours to be safe
            self.settings.save()

            return self.settings.access_token

        except Exception as e:
            logger.error(f"Failed to refresh ResilioDB access token: {str(e)}")
            raise

    def _compute_hash(self, endpoint: str, payload: dict) -> str:
        """Compute hash for request caching"""
        # Include API version and endpoint in hash
        hash_input = {
            'api_version': self.api_version,
            'endpoint': endpoint,
            'payload': payload
        }
        hash_string = json.dumps(hash_input, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def _get_cached_response(self, hash_value: str) -> dict:
        """Get cached response if available"""
        try:
            cache_entry = LCACache.objects.get(hash=hash_value)
            return cache_entry
        except LCACache.DoesNotExist:
            return None

    def _cache_response(self, hash_value: str, response_data: dict) -> LCACache:
        """
        Cache API response and return the cache entry
        """
        return LCACache.objects.create(
            hash=hash_value,
            request_payload=response_data
        )

    def get_footprint(self, lca_type: str, payload: dict) -> dict:
        """
        Get footprint data for a device configuration

        Args:
            lca_type: LCA type endpoint (e.g. 'blade_server', 'rack_server')
            payload: Request payload matching the endpoint's schema

        Returns:
            dict: Response data containing footprint results
        """
        # Compute request hash
        hash_value = self._compute_hash(lca_type, payload)

        # Check cache first
        cached_response = self._get_cached_response(hash_value)
        if cached_response:
            logger.debug(f"Cache hit for hash {hash_value}")
            return {"_cache_entry": cached_response}

        # Make API request
        try:
            endpoint = f"{self.base_url}/api/{lca_type}"
            # Use session without system proxy
            session = requests.Session()
            session.trust_env = False
            # Log equivalent curl command for debugging
            headers = self._get_headers()
            curl_cmd = f"curl -X POST '{endpoint}' \\\n"
            for header, value in headers.items():
                curl_cmd += f"  -H '{header}: {value}' \\\n"
            curl_cmd += f"  -d '{json.dumps(payload)}'"
            logger.debug(f"Equivalent curl command:\n{curl_cmd}")

            response = session.post(
                endpoint,
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            response_data = {
                "_raw_data": response.json()
            }

            # Cache the response and return both response and cache entry
            cache_entry = self._cache_response(hash_value, response_data["_raw_data"])
            response_data['_cache_entry'] = cache_entry

            return response_data

        except Exception as e:
            logger.error(f"ResilioDB API request failed: {str(e)}")
            raise

    def get_countries(self) -> list:
        """Get list of supported countries"""
        try:
            # Use session without system proxy
            session = requests.Session()
            session.trust_env = False

            response = session.get(
                f"{self.base_url}/api/countries",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()['countries']
        except Exception as e:
            logger.error(f"Failed to get countries list: {str(e)}")
            raise

    def healthcheck(self) -> bool:
        """Check if ResilioDB API is available"""
        try:
            session = requests.Session()
            session.trust_env = False
            response = session.get(f"{self.base_url}/api/healthcheck")
            return response.status_code == 200
        except:
            return False
