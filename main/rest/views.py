from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
import docx2txt
import re
import os


def saveFile(file):
    fileName = [i[0] for i in file.FILES]
    test = keys = list(file.FILES.keys())
    file = file.FILES[test[0]]
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    return file.name

# Create your views here.
class documentToMindmap(APIView):
    def post(self, request):
        global text, result
        filename = saveFile(request)
        document_path = 'media/' + filename
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
            docArray = {
                "text": text.replace('\n', '<br>'),
                "nodeData":
                    {
                        'topic': 'Ядро',
                        'text': '',
                        "children": []
                    }
            }
            stack = [(docArray["nodeData"], 0)]

            item = None
            level = None

            for line in strippedText:
                match = re.match(r"^(\d+(\.\d+)*)\.", line)
                if match:
                    title = line[len(match.group(0)):].strip()
                    new_level = len(match.group(1).split('.'))
                    if item is None or new_level > level:
                        item = {"topic": title, "text": "", "children": []}
                        stack[-1][0]["children"].append(item)
                        stack.append((item, new_level))
                    else:
                        item = {"topic": title, "text": "", "children": []}
                        while stack[-1][1] >= new_level:
                            stack.pop()
                        stack[-1][0]["children"].append(item)
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
class refreshMindMap(APIView):
        def post(self, request):
            errorExistence = False
            errorLabel = 0
            text = ''
            for key, value in request.POST.items():
               text = key[4:]
            # text = docx2txt.process('media/2.docx')
            lines = text.split('\n')
            lines = [line.strip() for line in lines]
            text = '\n'.join(lines)
            text = re.sub(r'\n\s*\n', '\n', text)
            text = text.replace('{code-section}', '<per>').replace('{/code-section}', '</per>')
            if text == '':
                errorLabel = 'inputFileIsEmpty'
                errorExistence = True
            # elif text[:2] != '1.':
            #     errorLabel = 'noTreeLikeStructureFound'
            #     errorExistence = True

            def processText(text):
                strippedText = text.strip().split("\n")
                docArray = {
                    "text": text.replace('\n', '<br>'),
                    "nodeData":
                        {
                            'topic': 'Ядро',
                            'text': '',
                            "children": []
                        }
                }
                stack = [(docArray["nodeData"], 0)]

                item = None
                level = None

                for line in strippedText:
                    match = re.match(r"^(\d+(\.\d+)*)\.", line)
                    if match:
                        title = line[len(match.group(0)):].strip()
                        new_level = len(match.group(1).split('.'))
                        if item is None or new_level > level:
                            item = {"topic": title, "text": "", "children": []}
                            stack[-1][0]["children"].append(item)
                            stack.append((item, new_level))
                        else:
                            item = {"topic": title, "text": "", "children": []}
                            while stack[-1][1] >= new_level:
                                stack.pop()
                            stack[-1][0]["children"].append(item)
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
                result = {
                    "Error": errorLabel}  # this line is only for DEBUG purposes/эта строчка написана только для целей отладки на этапе разработки
            return Response(result)
