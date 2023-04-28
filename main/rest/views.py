from rest_framework.views import APIView
from rest_framework.response import Response
import json
import docx


# Create your views here.
class documentToMindmap(APIView):
    def get(self, request):
        doc = docx.Document('static/data/example.docx')
        result = {}
        current_header = ''
        current_subheader = ''
        current_text = ''
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text.startswith('##'):
                if current_header:
                    if current_subheader and current_subheader == text.lstrip('#').strip():
                        # Если у нас уже есть subheader с таким же названием, то не добавляем его
                        continue
                    result[current_header].append(
                        {'subheader': current_subheader.strip(), 'text': current_text.strip()})
                    current_text = ''
                current_subheader = text.lstrip('#').strip()
            elif text.startswith('#'):
                if current_header:
                    result[current_header].append(
                        {'subheader': current_subheader.strip(), 'text': current_text.strip()})
                current_header = text.lstrip('#').strip()
                current_subheader = ''
                current_text = ''
                result[current_header] = []
            else:
                current_text += text + ' '

        if current_header:
            result[current_header].append({'subheader': current_subheader.strip(), 'text': current_text.strip()})

        for headers in result.values():
            unique_subheaders = []
            for subheader in headers:
                if subheader['subheader'] not in unique_subheaders:
                    unique_subheaders.append(subheader['subheader'])
                else:
                    headers.remove(subheader)

        return Response(json.dumps(result, indent=4))
