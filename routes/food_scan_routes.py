from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from db import FoodScan,auth, storage , Recommendation
from services import analyze_image , recommend_food
from helpers import clean_analysis_result_str


router = APIRouter()


@router.post("/analyze")
async def analyze(img: UploadFile = File(...) ,user=Depends(auth.get_current_user)):
    image_bytes = await img.read()
    result = analyze_image(image_bytes)
    json_result = clean_analysis_result_str(result)
    recommend_result = recommend_food(result)
    json_recommendation = clean_analysis_result_str(recommend_result)
    print("Recommendation result:", json_recommendation)
    
    resnopse = storage.upload_file(image_bytes, img.filename)
    
    # Example: Gemini result is a dict with keys: name, calories, protein, etc.
    if result and resnopse and recommend_result:
        scan = FoodScan.create(
            user_id=user.user.id,
            image_url= resnopse['public_url'],
            nutrients=result,
        )
        food = scan['data'][0]
        print(f" data : {food }, and food id {food.get('id')}")
        if scan:
            recommend = Recommendation.create(
                user_id=user.user.id,
                food_id=food.get('id'),
                recommendation=recommend_result
            )
            return {
                "status": "success",
                "result": json_result,
                "image_url": resnopse['public_url'],
            }

        raise HTTPException(status_code=500, detail="Error analyzing image or uploading file")

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