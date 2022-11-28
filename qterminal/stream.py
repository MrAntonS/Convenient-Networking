from pyte.streams import ByteStream
import codecs

class QTerminalStream(ByteStream):

    def __init__(self, *args, **kwargs):
        super(QTerminalStream, self).__init__(*args, **kwargs)
        self.utf8_decoder = codecs.getincrementaldecoder("utf-8")("replace")
