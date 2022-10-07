import io
import os
from os.path import exists
from subprocess import Popen, PIPE
import logging
# https://www.geeksforgeeks.org/broken-pipe-error-in-python/
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

from elg import FlaskService
from elg.model import TextRequest, TextsResponse, Failure
from elg.model.base import StandardMessages, StatusMessage


logging.basicConfig(level=logging.DEBUG)
MAX_CHAR = 15000
MAX_TOKEN_LENGTH = 100


class LVTagger(FlaskService):

    def convert_outputs(self, outputs, content, endpoint, warnings_msg_lst):
        texts = []
        lines = [x for x in outputs.split("\n") if x != ""]
        groups = []
        group = []
        for line in lines:
            if line.startswith("\t\t"):
                group.append(line[2:]) # this is morpho-feature
            elif group == []:
                group.append(line[1:]) # this is the first tag
            else:
                groups.append(group)
                group = [line[1:]] # this is the next tag 
        groups.append(group)
        for group in groups:
            feature_dict = {}
            for x in group[1:]: # the first element is tag
                [k,v] = x.split(" = ")
                if v != "":
                    feature_dict[k.replace(" ", "_")] = v
            text = {"role":"alternative",
                    "content": group[0], # tag
                    "features": feature_dict}
            texts.append(text)
        if warnings_msg_lst == []:
            return TextsResponse(texts = texts)
        else:
            return TextsResponse(texts = texts, warnings = warnings_msg_lst)

    def process_text(self, request: TextRequest):
        warnings_msg_lst = []
        content = request.content + "\n"
        if content == "\n":
            emptyInput_warning_msg = StatusMessage(
                code='lingsoft.input.empty',
                params=[],
                text='Input text is empty'
            )
            return TextsResponse(texts = [], warnings=[emptyInput_warning_msg])
        
        elif len(content.split()) > 1:
            multipleWordsInput_warning_msg = StatusMessage(
                code='lingsoft.input.not.single',
                params=[],
                text='Input should be one word, rest are ignored'
            )
            warnings_msg_lst.append(multipleWordsInput_warning_msg)
        endpoint = self.url_param('endpoint')
        if endpoint == "word_analysis":
            content = "analysis " + content
        elif endpoint == "wordforms":
            content = "wordforms " + content
        else:
            error = StandardMessages.generate_elg_service_not_found(
                    params=[endpoint])
            return Failure(errors=[error])
        
        if len(content) > MAX_CHAR:
            error = StandardMessages.generate_elg_request_too_large()
            return Failure(errors=[error])

        longest = 0
        if content.strip():
            longest = max(len(token) for token in content.split())
        if longest > MAX_TOKEN_LENGTH:
            error = StatusMessage(
                    code="lingsoft.token.too.long",
                    text="Given text contains too long tokens",
                    params=[])
            return Failure(errors=[error])
        
        if any(ord(ch) > 0xffff for ch in content):
            error = StatusMessage(
                    code="lingsoft.character.invalid",
                    text="Given text contains unsupported characters",
                    params=[])
            return Failure(errors=[error])
            
        try:
            app.logger.debug("Content: %s", content)
            process.stdin.write(content)
            process.stdin.flush()
            lines = []
            previous_empty = False
            while True:
                line = process.stdout.readline().rstrip('\n')
                if line == "" or not line:
                    break
                else:
                    lines.append(line)
            output = "\n".join(lines)
            app.logger.debug("Output: %s", output)
            return self.convert_outputs(output, content, endpoint, warnings_msg_lst)
        except Exception as err:
            if str(err) == "list index out of range":
                notFound_warning_msg = StatusMessage(
                    code='lingsoft.not.found.word',
                    params=[request.content.split()[0]],
                    text='Word not found'
                )
                warnings_msg_lst.append(notFound_warning_msg)
                return TextsResponse(texts = [], warnings = warnings_msg_lst)
            else:
                error = StandardMessages.\
                        generate_elg_service_internalerror(params=[str(err)])
                return Failure(errors=[error])

flask_service = LVTagger(name="LVTagger", path="/process/<endpoint>")
app = flask_service.app
process = None

@app.before_first_request
def setup():
    global process
    java_call = ["/java/bin/java", "-jar", "morphology-2.2.5-SNAPSHOT.jar"]
    process = Popen(java_call, stdin=PIPE, stdout=PIPE, text=True)
