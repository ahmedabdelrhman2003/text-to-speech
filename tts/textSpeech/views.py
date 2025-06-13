from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import asyncio
import edge_tts
import PyPDF2
import uuid
import re
import threading


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES or 'language' not in request.data:
            return Response({"error": "PDF file and language are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        language = request.data['language']

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        pdf_filename = fs.save(uploaded_file.name, uploaded_file)
        pdf_path = fs.path(pdf_filename)

        try:
            text = self.extract_text_from_pdf(pdf_path)

            if not text.strip():
                return Response({"error": "No text found in the PDF."}, status=status.HTTP_400_BAD_REQUEST)

            mp3_filename = f"{uuid.uuid4()}.mp3"
            mp3_path = os.path.join(settings.MEDIA_ROOT,mp3_filename)
            asyncio.run(self.convert_text_to_speech(text, language, mp3_path))

            if not os.path.exists(mp3_path):
                return Response({"error": "MP3 file not created."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            audio_url = os.path.join(settings.MEDIA_URL, mp3_filename)
            full_url = request.build_absolute_uri(audio_url)
            threading.Thread(target=self.delete_file_later, args=(mp3_path,)).start()

            return Response({"audio_path": full_url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    def extract_text_from_pdf(self, pdf_file):
        try:
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                    
            text = text.replace('\n', '')
            text = text.replace('هللا', 'الله')
            text = text.replace('وهللا', 'والله')
            text = text.replace('وهللا', 'والله')

            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

    async def convert_text_to_speech(self, text, language, output_file):
        voices = {
            'en': 'en-US-ChristopherNeural',
            'ar': 'ar-IQ-BasselNeural',
        }
        voice = voices.get(language, 'en-US-ChristopherNeural')  
        communicator = edge_tts.Communicate(text, voice, rate='-10%')
        await communicator.save(output_file)

    def delete_file_later(self, path):
     import time
     time.sleep(10)  
     if os.path.exists(path):
        os.remove(path)