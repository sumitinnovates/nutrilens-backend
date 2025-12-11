from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from db import FoodScan,auth, storage , Recommendation
from services import analyze_image , recommend_food
from helpers import clean_analysis_result_str


router = APIRouter()

@router.post("/analyze")
async def analyze(img: UploadFile = File(...), user=Depends(auth.get_current_user)):
    # 1. Read image
    try:
        image_bytes = await img.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read uploaded image")

    # 2. Analyze image with Gemini
    try:
        result = analyze_image(image_bytes)
    except Exception as e:
        print("Gemini analyze_image error:", str(e))
        raise HTTPException(status_code=500, detail="Image analysis failed")

    # 3. Handle Gemini quota or errors
    if result is None:
        raise HTTPException(
            status_code=429,
            detail="Gemini quota exceeded or returned no result"
        )

    json_result = clean_analysis_result_str(result)

    # 4. Recommendation via Gemini
    try:
        recommend_result = recommend_food(result)
    except Exception as e:
        print("Gemini recommend_food error:", str(e))
        recommend_result = None

    json_recommendation = clean_analysis_result_str(recommend_result)
    print("Recommendation result:", json_recommendation)

    # 5. Upload image to Supabase Storage
    response = storage.upload_file(image_bytes, img.filename)
    print("Upload response:", response)

    # 6. Validate Storage upload
    if not response or "public_url" not in response:
        raise HTTPException(
            status_code=500,
            detail=f"Storage upload failed: {response}"
        )

    public_url = response.get("public_url")

    # 7. Save scan record in DB
    try:
        scan = FoodScan.create(
            user_id=user.user.id,
            image_url=public_url,
            nutrients=result
        )
    except Exception as e:
        print("DB scan create error:", str(e))
        raise HTTPException(status_code=500, detail="Failed to save scan to database")

    # Extract scan ID from supabase data
    try:
        food = scan["data"][0]
        food_id = food.get("id")
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid scan response from database")

    # 8. Save recommendation
    if recommend_result:
        try:
            Recommendation.create(
                user_id=user.user.id,
                food_id=food_id,
                recommendation=recommend_result
            )
        except Exception as e:
            print("Recommendation DB error:", e)

    # 9. Success Response
    return {
        "status": "success",
        "result": json_result,
        "recommendation": json_recommendation,
        "image_url": public_url,
        "food_id": food_id,
    }


#get all scans for a user and url is /scans/scans because of the prefix
@router.get("/scans")
def get_all_scans(user=Depends(auth.get_current_user)):
    scans = FoodScan.get_by_user(user.user.id)
    return {"status": "success", "scans": scans}

#fetch a scan by id use keyword argument scan_id
@router.get("/id")
def get_scan_by_id(scan_id: str, user=Depends(auth.get_current_user)):
    scan = FoodScan.get_by_id(scan_id)
    if scan :
        return {"status": "success", "scan": scan}
    raise HTTPException(status_code=404, detail="Scan not found")

#delete a scan by id make sure to pass scan_id as a query parameter
@router.delete("/delete")
def delete_scan(scan_id: str, user=Depends(auth.get_current_user)):
    scan = FoodScan.get_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found or already deleted")
    deleted = FoodScan.delete(scan_id)
    return {"status": "success", "deleted": deleted}

# Get the latest scan for a user
@router.get("/scans/latest")
def get_latest_scan(user=Depends(auth.get_current_user)):
    try:
        scan = FoodScan.get_latest(user.user.id)
        return {"status": "success", "latest": scan}
    except Exception:
        raise HTTPException(status_code=404, detail="No scans found")
    

@router.delete("/deleteAll")
def delete_All_scans(scan_id : list , user=Depends(auth.get_current_user)):
    try:
        scan = FoodScan.deleteMany(scan_id)
        if scan :
            return { "status": "success" , "message":"Deleted"}
        return {"status": "faild", "message":"failed to delete"}
    except Exception as e:
        return {"status": "error", "message": e}