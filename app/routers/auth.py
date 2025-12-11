from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt, JWTError
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.models.cafe_owner import CafeOwnerProfile
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role.value,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if user.role.value == "cafe_owner":
        owner_profile = CafeOwnerProfile(
            user_id=new_user.id,
            total_orders='0',
            total_customers='0',
            total_revenue='0'
        )
        db.add(owner_profile)
        db.commit()
    
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={
        "user_id": user.id,
        "role": user.role
    })

    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/token", response_model=TokenResponse)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login for Swagger UI authorization"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={
        "user_id": user.id,
        "role": user.role
    })

    return TokenResponse(access_token=token, token_type="bearer")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        result = db.execute(
            text('SELECT id, name, email, role FROM users WHERE id = :id'),
            {"id": user_id}
        ).mappings().fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        return result  # <-- dict-like, Pydantic-friendly

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
