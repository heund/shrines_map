# Environment Setup

## Local API Key

Create or update the project root `.env` file with your Kakao REST API key and, if needed, your Google Maps API key.

```env
KAKAO_REST_API_KEY=your_kakao_rest_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

## Notes

- Use the Kakao app `REST API key`
- Do not use an access token
- Do not wrap the key in extra quotes unless needed
- `GOOGLE_MAPS_API_KEY` is optional and is used only as fallback after Kakao

## Current Script Behavior

`scripts/clean_shrines.py` loads `.env` from the project root automatically and reads:

- `KAKAO_REST_API_KEY`
- `GOOGLE_MAPS_API_KEY`
