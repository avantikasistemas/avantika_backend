from Utils.tools import Tools
from fastapi import APIRouter, Request # Depends
from Schemas.Graph.get_emails import GetEmails
from Class.Graph import Graph
from Utils.decorator import http_decorator
# from Middleware.jwt_bearer import JWTBearer

tools = Tools()
graph_router = APIRouter()

@graph_router.post('/get_emails', tags=["Emails"], response_model=dict)
@http_decorator
def get_emails(request: Request, getEmails: GetEmails):
    data = getattr(request.state, "json_data", {})
    response = Graph().get_emails(data)
    return response
