import os
import mimetypes
from flask import Flask, request, Response, render_template

app = Flask(__name__)
DIRECTORY = os.getenv("DIRECTORY", "/app/files")  # Default directory inside container

@app.route('/')
@app.route('/<path:subpath>')
def access_path(subpath=''):

    fullpath = os.path.join(DIRECTORY, subpath)

    if (not os.path.exists(fullpath)):
        return f'The path does not exist', 404

    if (os.path.isdir(fullpath)):

        back_path = None
        if len(subpath) > 0:
            if '/' in subpath:
                back_path = '/'.join(subpath.split('/')[:-1])
            else:
                back_path = '/'

        try:
            files = os.scandir(os.path.join(DIRECTORY, subpath))
            files = sorted(files, key=lambda x: (not x.is_dir(), x.name.lower())) # Sort by type (Directories first) and file name

            return render_template('index.html', files=files, back_path=back_path, subpath=subpath)
        except Exception as e:
            return f"Error accessing directory: {str(e)}", 500

    elif (os.path.isfile(fullpath)):

        file_size = os.path.getsize(fullpath)
        mime_type, _ = mimetypes.guess_type(fullpath)  # Detect file type

        if not mime_type:
            mime_type = "application/octet-stream"  # Default fallback

        range_header = request.headers.get("Range")

        if range_header:
            byte_range = range_header.replace("bytes=", "").split("-")
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if byte_range[1] else file_size - 1

            if start >= file_size or start > end:
                return "Range Not Satisfiable", 416

            def stream():
                with open(fullpath, "rb") as f:
                    f.seek(start)
                    remaining_bytes = end - start + 1
                    while remaining_bytes > 0:
                        chunk_size = min(4096, remaining_bytes)
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                        remaining_bytes -= len(chunk)

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(end - start + 1),
                "Content-Type": mime_type
            }
            return Response(stream(), status=206, headers=headers)  # Partial content

        return Response(open(fullpath, "rb"), content_type=mime_type,
                        headers={"Accept-Ranges": "bytes",
                                 "Content-Length": str(file_size)})

    else:
        return f'The path cannot be accessed', 403


#@app.route('/')
#def list_files():
#    """Lists all files in the directory, sorted by name."""
#    try:
#        files = sorted(os.listdir(DIRECTORY), key=str.lower)  # Sort files alphabetically
#        return render_template('index.html', files=files)
#    except Exception as e:
#        return f"Error accessing directory: {str(e)}", 500

@app.route('/download/<filename>')
def download_file(filename):
    """Streams video/audio files with Range support for seeking."""
    filepath = os.path.join(DIRECTORY, filename)

    if not os.path.isfile(filepath):
        return "File not found", 404

    file_size = os.path.getsize(filepath)
    mime_type, _ = mimetypes.guess_type(filepath)  # Detect file type
    if not mime_type:
        mime_type = "application/octet-stream"  # Default fallback

    range_header = request.headers.get("Range")

    if range_header:
        byte_range = range_header.replace("bytes=", "").split("-")
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if byte_range[1] else file_size - 1

        if start >= file_size or start > end:
            return "Range Not Satisfiable", 416

        def stream():
            with open(filepath, "rb") as f:
                f.seek(start)
                remaining_bytes = end - start + 1
                while remaining_bytes > 0:
                    chunk_size = min(4096, remaining_bytes)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    remaining_bytes -= len(chunk)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": mime_type
        }
        return Response(stream(), status=206, headers=headers)  # Partial content

    return Response(open(filepath, "rb"), content_type=mime_type,
                    headers={"Accept-Ranges": "bytes",
                             "Content-Length": str(file_size)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
