from flask import request, Response
from musixfy import app, apiClient, iterate_data
from musixfy.utils.Encrpyt import decode_data, get_key


@app.route('/api/music')
def get_song_list():
    query = request.args.get('query')
    offset = request.args.get('offset')
    return apiClient.get_songs_list(query, offset)


@app.route('/api/video')
def get_video_list():
    query = request.args.get('query')
    offset = request.args.get('offset')
    return apiClient.get_video_list(query, offset, 1)


@app.route('/api/stream')
def stream_handler():
    encoded_url = request.args.get('encoded_url')
    url = decode_data(get_key(), encoded_url.encode('utf8'))['url']
    mime = 'audio/mpeg'

    if url.find('mime=audio%2Fwebm') > -1:
        mime = 'audio/webm'

    range_header = request.headers.get('Range', None)

    if range_header:
        from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
        if not until_bytes:
            until_bytes = int(from_bytes) + int(1024 * 1024 * 1)
        headers = {'Range': 'bytes=%s-%s' % (from_bytes, until_bytes)}
        r = apiClient.http.get(url, headers=headers)
        data = r.content
        rv = Response(data, 206, mimetype=mime, direct_passthrough=True)
        rv.headers.add('Content-Range', r.headers.get('Content-Range'))
        return rv

    r = apiClient.http.get(url, stream=True)

    return Response(iterate_data(r), mimetype=mime)


@app.route('/api/download')
def download_file():
    try:
        encoded_url = request.args.get('encoded_url')
        data = decode_data(get_key(), encoded_url.encode('utf8'))
        url = data['url']
        filename = f"{data['artist']}-{data['title']}.mp3"
        range_header = request.headers.get('Range', None)
        if range_header:
            from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
            if not until_bytes:
                until_bytes = int(from_bytes) + int(1024 * 1024 * 1)
            headers = {'Range': 'bytes=%s-%s' % (from_bytes, until_bytes)}
            resp = apiClient.http.get(url, headers=headers, stream=True)
            rv = Response(iterate_data(resp), 206, mimetype='audio/mpeg', direct_passthrough=True)
            rv.headers.add('Content-Range', resp.headers.get('Content-Range'))
            rv.headers.add('Content-Disposition', 'attachment; filename="%s"' % filename)
            rv.headers.add('Content-Length', resp.headers['Content-Length'])
            return rv

        resp = apiClient.http.get(url, stream=True)
        response = Response(iterate_data(resp), mimetype='audio/mpeg')
        response.headers.add('Content-Disposition', 'attachment; filename="%s"' % filename)
        response.headers.add('Content-Length', resp.headers['Content-Length'])
        return response

    except Exception as e:
        app.logger.info('Exception', e.with_traceback())


if __name__ == '__main__':
    app.run()
