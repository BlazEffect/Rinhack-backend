from rest_framework.views import APIView
from rest_framework.response import Response
import re
import os
import docx2txt


# Create your views here.
class documentToMindmap(APIView):
    def get(self, request):
        global text, result
        document_path = 'static/data/2.docx'
        errorExistence = False
        errorLabel = 0
        if not os.path.isfile(document_path):
            errorExistence = True
            errorLabel = 'unableToFetchFilePath'
        else:
            file_ext = re.search(r'\.(\w+)$', document_path)
            if file_ext is None or file_ext.group(1) != 'docx':
                errorLabel = 'unableToDefineFileFormat'
                errorExistence = True
            text = docx2txt.process(document_path)
            lines = text.split('\n')
            lines = [line.strip() for line in lines]
            text = '\n'.join(lines)
            text = re.sub(r'\n\s*\n', '\n', text)
            text = text.replace('{code-section}', '<per>').replace('{/code-section}', '</per>')
        def processText(text):
            strippedText = text.strip().split("\n")
            docArray = {"items": []}
            stack = [(docArray, 0)]

            item = None
            level = None

            for line in strippedText:
                match = re.match(r"^(\d+(\.\d+)*)\.", line)
                if match:
                    title = line[len(match.group(0)):].strip()
                    new_level = len(match.group(1).split('.'))
                    if item is None or new_level > level:
                        item = {"title": title, "text": "", "items": []}
                        stack[-1][0]["items"].append(item)
                        stack.append((item, new_level))
                    else:
                        item = {"title": title, "text": "", "items": []}
                        while stack[-1][1] >= new_level:
                            stack.pop()
                        stack[-1][0]["items"].append(item)
                        stack.append((item, new_level))
                    level = new_level
                elif item is not None:
                    if item["text"] and line:
                        item["text"] += "<br>"
                    item["text"] += line.strip()

            return docArray
        if not errorExistence:
            result = processText(text)
        elif errorExistence:
            result = {"Error": errorLabel} #this line is only for DEBUG purposes/эта строчка написана только для целей отладки на этапе разработки
        return Response(result)
