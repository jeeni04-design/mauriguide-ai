import httpx
from typing import Optional, Dict
from config import settings
from fastapi import HTTPException

async def verify_django_token(token: str) -> Optional[Dict]:
    """
    Verify Django authentication token
    Returns user data if valid, None otherwise
    """
    if not token:
        return None
    
    try:
        # Remove 'Bearer ' prefix if present
        clean_token = token.replace("Bearer ", "").replace("Token ", "")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.DJANGO_API_URL}/api/auth/verify/",
                headers={"Authorization": f"Token {clean_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return None
            else:
                print(f"Unexpected status code from Django: {response.status_code}")
                return None
                
    except httpx.TimeoutException:
        print("Django authentication service timeout")
        return None
    except httpx.RequestError as e:
        print(f"Error connecting to Django: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in token verification: {e}")
        return None

async def get_user_from_token(authorization: Optional[str]) -> Optional[Dict]:
    """
    Extract and verify user from authorization header
    """
    if not authorization:
        return None
    
    return await verify_django_token(authorization)

class AuthMiddleware:
    """
    Optional authentication middleware
    """
    
    @staticmethod
    async def verify_user(authorization: Optional[str], required: bool = False) -> Optional[Dict]:
        """
        Verify user authentication
        
        Args:
            authorization: Authorization header value
            required: If True, raises HTTPException when auth fails
            
        Returns:
            User data dict or None
        """
        user_data = await get_user_from_token(authorization)
        
        if required and not user_data:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        return user_data