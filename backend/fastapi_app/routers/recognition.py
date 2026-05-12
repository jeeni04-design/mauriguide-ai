from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from models.schemas import (
    ImageRecognitionRequest,
    ImageRecognitionResponse
)
from services.image_recognition import ImageRecognitionService
import base64

# Create the router instance - THIS WAS MISSING!
router = APIRouter()

def get_recognition_service():
    """Dependency injection for recognition service"""
    return ImageRecognitionService()

@router.post("/identify", response_model=ImageRecognitionResponse)
async def identify_landmark(
    image: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    context: Optional[str] = Form(None)
):
    """
    Identify landmarks and places in an image
    
    Upload an image file or provide an image URL
    
    - **image**: Image file (JPEG, PNG)
    - **image_url**: Alternative: URL to image
    - **context**: Optional context about the image
    """
    try:
        service = get_recognition_service()
        
        image_data = None
        
        if image:
            # Read uploaded file
            contents = await image.read()
            
            # Validate file size (max 5MB)
            if len(contents) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Image file too large (max 5MB)"
                )
            
            # Convert to base64
            image_data = base64.b64encode(contents).decode()
        
        elif not image_url:
            raise HTTPException(
                status_code=400,
                detail="Either image file or image_url must be provided"
            )
        
        # Create request
        request = ImageRecognitionRequest(
            image_data=image_data,
            image_url=image_url,
            context=context
        )
        
        # Process recognition
        result = await service.recognize_image(request)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/landmarks")
async def list_landmarks(
    search: Optional[str] = None
):
    """
    List all known landmarks in Mauritius
    
    - **search**: Optional search query to filter landmarks
    """
    try:
        service = get_recognition_service()
        
        if search:
            landmarks = service.search_landmarks(search)
        else:
            # Return all landmarks
            landmarks = [
                {"id": lid, **info}
                for lid, info in service.landmarks_db.items()
            ]
        
        return {
            "landmarks": landmarks,
            "total": len(landmarks),
            "search_query": search
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing landmarks: {str(e)}"
        )

@router.get("/landmarks/{landmark_id}")
async def get_landmark_details(landmark_id: str):
    """
    Get detailed information about a specific landmark
    """
    try:
        service = get_recognition_service()
        
        landmark = service.get_landmark_info(landmark_id)
        
        if not landmark:
            raise HTTPException(
                status_code=404,
                detail=f"Landmark '{landmark_id}' not found"
            )
        
        return {
            "id": landmark_id,
            **landmark
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving landmark: {str(e)}"
        )