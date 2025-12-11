from fastapi import APIRouter , Depends , HTTPException
from db import auth, Recommendation

router = APIRouter()

# Get all recommendations for a user
@router.get("/all")
def get_all_recommendations(user=Depends(auth.get_current_user)):
    recs = Recommendation.get_by_user(user.user.id)
    return {"status": "success", "recommendations": recs}


# Get recommendation by ID
@router.get("/id")
def get_recommendation_by_id(rec_id: str, user=Depends(auth.get_current_user)):
    rec = Recommendation.get_by_id(rec_id)
    if rec:
        return {"status": "success", "recommendation": rec}
    raise HTTPException(status_code=404, detail="Recommendation not found")


# Delete recommendation by ID
@router.delete("/delete")
def delete_recommendation(rec_id: str, user=Depends(auth.get_current_user)):
    rec = Recommendation.get_by_id(rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found or already deleted")
    deleted = Recommendation.delete(rec_id)
    return {"status": "success", "deleted": deleted}


# Get latest recommendation for the user
@router.get("/latest")
def get_latest_recommendation(user=Depends(auth.get_current_user)):
    try:
        rec = Recommendation.get_latest(user.user.id)
        return {"status": "success", "latest": rec}
    except Exception:
        raise HTTPException(status_code=404, detail="No recommendations found")
    

@router.delete("/deleteAll")
def delete_All_scans(recommendation_id : list , user=Depends(auth.get_current_user)):
    try:
        scan = Recommendation.deleteMany(recommendation_id)
        if scan :
            return { "status": "success" , "message":"Deleted"}
        return {"status": "faild", "message":"failed to delete"}
    except Exception as e:
        return {"status": "error", "message": e}