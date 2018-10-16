__version__ = "0.1"

__all__ = ["MyHTTPRequestHandler"]

import SimpleHTTPServer
import BaseHTTPServer
import os
import posixpath
import urllib
import urlparse
import cgi
import sys
import shutil
import mimetypes
import time
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class MyHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    server_version = "MyHTTP/" + __version__

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: (-os.path.isdir(path+a), a))
        list = ([os.pardir] if path.rstrip('/') != os.getcwd() else []) + [os.curdir] + list
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<head>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<style>th { padding: 0px 10px 0px 10px; } table { font-family: courier new; }</style>\n</head>\n")
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<table>\n")
        f.write("<tr><th>Name</th><th>Size</th><th>Modified</th></tr>")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
                size = ''
            else:
                size = os.stat(fullname).st_size
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            modified = time.ctime(os.stat(fullname).st_mtime)
            f.write('<tr><th align="left"><a href="{}">{}</a></th><th align="right">{}</th><th>{}</th></tr>'.format(urllib.quote(linkname), cgi.escape(displayname), size, modified))
        f.write("</table>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

def test(HandlerClass = MyHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
    test()
