from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.Inventario import ControleFuncionario
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.header import Header
import base64
import os
import pickle
import json
import tempfile
from google_auth_oauthlib.flow import InstalledAppFlow
#mandar arquivo do comprovante do epi.pdf via email
def MandarComprovanteEpi(email:str,DocPath:str):
    Destinatario = email
    remetente = "email ali"