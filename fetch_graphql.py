import json
import aiohttp
import asyncio

async def fetch_graphql(session, url, query, variables, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'query': query,
        'variables': variables,
    }

    print(f"Making GraphQL request to {url}")
    print(f"Headers: {headers}")
    print(f"Variables: {variables}")

    attempt = 0
    while True:  # Infinite retry loop
        try:
            async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
                print(f"Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if 'errors' in data:
                        print(f"GraphQL errors: {data['errors']}")
                        return None
                    return data
                else:
                    response_text = await response.text()
                    print(f"Request failed with status {response.status}")
                    print(f"Response body: {response_text}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Request exception: {e}")
            return None

        # Exponential backoff and retry
        attempt += 1
        if attempt >= 3:  # Max 3 attempts
            print("Max retry attempts reached")
            return None
            
        wait_time = min(5 * 2 ** attempt, 30)  # Exponential backoff with max wait time of 30 seconds
        print(f"Retrying in {wait_time} seconds (attempt {attempt})...")
        await asyncio.sleep(wait_time)