"""
번역 기능을 위한 모듈
Google Translate API, Azure Translator 등을 지원합니다.
"""

import os
import requests
from typing import Optional

class TranslationService:
    """번역 서비스 기본 클래스"""
    
    def translate(self, text: str, target_language: str) -> str:
        raise NotImplementedError

class GoogleTranslateService(TranslationService):
    """Google Translate API를 사용한 번역"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_TRANSLATE_API_KEY not found in environment")
    
    def translate(self, text: str, target_language: str) -> str:
        """Google Translate API를 사용하여 텍스트 번역"""
        try:
            from google.cloud import translate_v2
            
            translate_client = translate_v2.Client()
            source_lang = 'ko' if target_language == 'en' else 'en'
            
            result = translate_client.translate_text(
                source_language_code=source_lang,
                target_language_code=target_language,
                contents=[text]
            )
            
            return result['translations'][0]['translatedText']
        except Exception as e:
            print(f"Translation error: {e}")
            return text

class AzureTranslatorService(TranslationService):
    """Azure Translator를 사용한 번역"""
    
    def __init__(self):
        self.api_key = os.getenv('AZURE_TRANSLATOR_KEY')
        self.endpoint = os.getenv('AZURE_TRANSLATOR_ENDPOINT')
        
        if not self.api_key or not self.endpoint:
            raise ValueError("AZURE_TRANSLATOR_KEY or AZURE_TRANSLATOR_ENDPOINT not found in environment")
    
    def translate(self, text: str, target_language: str) -> str:
        """Azure Translator를 사용하여 텍스트 번역"""
        try:
            import uuid
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
            
            params = {
                'api-version': '3.0',
                'from': 'ko' if target_language == 'en' else 'en',
                'to': target_language
            }
            
            body = [{'text': text}]
            
            response = requests.post(
                self.endpoint + '/translate',
                params=params,
                headers=headers,
                json=body
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result[0]['translations'][0]['text']
        except Exception as e:
            print(f"Translation error: {e}")
            return text

class PapagoTranslatorService(TranslationService):
    """네이버 Papago를 사용한 번역"""
    
    def __init__(self):
        self.client_id = os.getenv('PAPAGO_CLIENT_ID')
        self.client_secret = os.getenv('PAPAGO_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("PAPAGO_CLIENT_ID or PAPAGO_CLIENT_SECRET not found in environment")
    
    def translate(self, text: str, target_language: str) -> str:
        """네이버 Papago를 사용하여 텍스트 번역"""
        try:
            source_lang = 'ko' if target_language == 'en' else 'en'
            target = 'en' if target_language == 'en' else 'ko'
            
            headers = {
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            data = {
                'source': source_lang,
                'target': target,
                'text': text
            }
            
            response = requests.post(
                'https://openapi.naver.com/v1/papago/n2mt',
                headers=headers,
                data=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['message']['result']['translatedText']
        except Exception as e:
            print(f"Translation error: {e}")
            return text

def get_translation_service() -> Optional[TranslationService]:
    """환경 설정에 따라 적절한 번역 서비스 반환"""
    
    translator_type = os.getenv('TRANSLATOR_TYPE', 'none').lower()
    
    try:
        if translator_type == 'google':
            return GoogleTranslateService()
        elif translator_type == 'azure':
            return AzureTranslatorService()
        elif translator_type == 'papago':
            return PapagoTranslatorService()
        else:
            return None
    except Exception as e:
        print(f"Failed to initialize translation service: {e}")
        return None

def translate_text(text: str, target_language: str) -> str:
    """텍스트 번역 (글로벌 함수)"""
    service = get_translation_service()
    
    if service:
        return service.translate(text, target_language)
    else:
        # 번역 서비스가 없으면 원본 반환
        return text
