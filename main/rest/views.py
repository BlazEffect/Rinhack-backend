from rest_framework.views import APIView
from rest_framework.response import Response
import docx


# Create your views here.
class TestApiView(APIView):
    def get(self, request):
        doc = docx.Document('static/data/docs.docx')

        text = []
        headers = []
        textForHeader = []
        for paragraph in doc.paragraphs:
            if paragraph.text[:1] == '#':
                headers.append(paragraph.text[1:])
                if textForHeader:
                    text.append(textForHeader)
                    textForHeader = []
                continue

            textForHeader.append(paragraph.text)

        text.append(textForHeader)

        return Response([headers, text])
