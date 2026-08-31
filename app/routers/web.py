"""Router de páginas web"""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta
from app.database import get_db
from app.services import person_service, mass_service, scale_service
from app.models.person import Person, ServerType
from app.models.mass import Mass, DayOfWeek
from app.models.scale import Scale, ScaleAssignment, AssignmentStatus
from app.utils.security import decode_access_token


router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request):
    """Obtém usuário atual do cookie"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    return payload.get("sub")


def require_auth(request: Request):
    """Exige autenticação"""
    user = get_current_user(request)
    if not user:
        return None
    return user


# ===== PÁGINAS PÚBLICAS =====

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Página inicial"""
    today = date.today()
    end_date = today + timedelta(days=30)
    
    masses = mass_service.get_masses_by_date_range(db, today, end_date)
    
    return templates.TemplateResponse(request=request, name="public/home.html", context={
        "request": request,
        "masses": masses,
        "today": today
    })


@router.get("/escala", response_class=HTMLResponse)
async def public_scale(
    request: Request,
    start_date: date = None,
    end_date: date = None,
    server_type: ServerType = None,
    db: Session = Depends(get_db)
):
    """Página pública de escalas"""
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=7)
    
    scales = scale_service.get_scales_by_date_range(db, start_date, end_date)
    
    # Filtrar por tipo se necessário
    if server_type:
        filtered_scales = []
        for scale in scales:
            filtered_assignments = [
                a for a in scale.assignments 
                if a.person.server_type == server_type
            ]
            if filtered_assignments:
                scale.assignments = filtered_assignments
                filtered_scales.append(scale)
        scales = filtered_scales
    
    persons = person_service.get_persons(db, is_active=True)
    
    return templates.TemplateResponse(request=request, name="public/scale.html", context={
        "request": request,
        "scales": scales,
        "start_date": start_date,
        "end_date": end_date,
        "server_type": server_type,
        "persons": persons,
        "server_types": ServerType
    })


# ===== PÁGINAS ADMINISTRATIVAS =====

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard administrativo"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    today = date.today()
    end_date = today + timedelta(days=30)
    
    masses = mass_service.get_masses_by_date_range(db, today, end_date)
    persons_count = len(person_service.get_persons(db, is_active=True))
    
    return templates.TemplateResponse(request=request, name="admin/dashboard.html", context={
        "request": request,
        "user": user,
        "masses": masses,
        "persons_count": persons_count,
        "today": today
    })


@router.get("/admin/pessoas", response_class=HTMLResponse)
async def admin_persons(request: Request, db: Session = Depends(get_db)):
    """Página de pessoas"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    persons = person_service.get_persons(db)
    return templates.TemplateResponse(request=request, name="admin/persons.html", context={
        "request": request,
        "user": user,
        "persons": persons,
        "server_types": ServerType
    })


@router.get("/admin/horarios", response_class=HTMLResponse)
async def admin_schedules(request: Request, db: Session = Depends(get_db)):
    """Página de horários"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    schedules = mass_service.get_mass_schedules(db)
    
    return templates.TemplateResponse(request=request, name="admin/schedules.html", context={
        "request": request,
        "user": user,
        "schedules": schedules,
        "day_of_week": DayOfWeek
    })


@router.get("/admin/escalas", response_class=HTMLResponse)
async def admin_scales(
    request: Request,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Página de escalas"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=30)
    
    scales = scale_service.get_scales_by_date_range(db, start_date, end_date)
    persons = person_service.get_persons(db, is_active=True)
    
    return templates.TemplateResponse(request=request, name="admin/scales.html", context={
        "request": request,
        "user": user,
        "scales": scales,
        "persons": persons,
        "start_date": start_date,
        "end_date": end_date,
        "server_types": ServerType,
        "assignment_status": AssignmentStatus
    })


@router.post("/admin/escalas/gerar")
async def generate_scales(
    request: Request,
    start_date: date = Form(...),
    end_date: date = Form(...),
    db: Session = Depends(get_db)
):
    """Gera missas para período"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    count = mass_service.generate_masses_for_period(db, start_date, end_date)
    
    return RedirectResponse(
        url=f"/admin/escalas?start_date={start_date}&end_date={end_date}",
        status_code=303
    )


@router.post("/admin/escalas/{scale_id}/atribuir")
async def assign_person(
    request: Request,
    scale_id: int,
    person_id: int = Form(...),
    observations: str = Form(None),
    db: Session = Depends(get_db)
):
    """Atribui pessoa à escala"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        scale_service.add_assignment(db, scale_id, person_id, observations=observations)
    except ValueError as e:
        # Em produção, usar flash messages
        pass
    
    return RedirectResponse(url="/admin/escalas", status_code=303)


@router.post("/admin/escalas/{scale_id}/publicar")
async def publish_scale_route(
    request: Request,
    scale_id: int,
    db: Session = Depends(get_db)
):
    """Publica escala"""
    user = require_auth(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    scale_service.publish_scale(db, scale_id)
    
    return RedirectResponse(url="/admin/escalas", status_code=303)
