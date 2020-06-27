from fastapi import Request, Response, APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from app import main
from app.utils.ApiClient import ApiClient
from app.utils.StreamHandler import StreamHandler
from app.utils.Encrpyt import decode_data, get_key

router = APIRouter()

apiClient = ApiClient()

streamHandler = StreamHandler()


@router.get('/music')
def get_song_list(query: str, offset: str):
    return apiClient.get_songs_list(query, offset)


@router.get('/video')
def get_video_list(query: str, offset: str):
    return apiClient.get_video_list(query, offset, 1)


@router.get('/stream/music')
def stream_handler(encoded_url: str, cache: str, request: Request, download_task: BackgroundTasks):
    payload = decode_data(get_key(), encoded_url.encode('utf8'))
    if cache == 'true':
        download_task.add_task(streamHandler.download_file, payload)
    url = payload['url']
    mime = 'audio/mpeg'

    range_header = request.headers.get('Range', None)

    if range_header:
        from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
        data = streamHandler.get_range_bytes(from_bytes, until_bytes, payload)
        response = Response(data['content'], 206, media_type=mime)
        response.headers['Content-Range'] = data['content-range']
        return response

    r = apiClient.http.get(url, stream=True)

    return StreamingResponse(iterate_data(r), media_type=mime)


@router.get('/download/music')
def download_file(encoded_url: str, cache: str, request: Request,download_task: BackgroundTasks):
    try:
        payload = decode_data(get_key(), encoded_url.encode('utf8'))
        if cache == 'true':
            download_task.add_task(streamHandler.download_file, payload)
        url = payload['url']
        filename = f"{payload['artist']}-{payload['title']}.mp3"
        range_header = request.headers.get('Range', None)
        if range_header:
            from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
            data = streamHandler.get_range_bytes(from_bytes, until_bytes, payload)
            response = Response(data['content'], 206, media_type='audio/mpeg')
            response.headers['Content-Range'] = data['content-range']
            response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
            response.headers['Content-Length'] = data['content-length']
            return response

        r = apiClient.http.get(url, stream=True)
        response = StreamingResponse(iterate_data(r), media_type='audio/mpeg')
        response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.headers['Content-Length'] = r.headers['Content-Length']
        return response

    except Exception as e:
        print("")


@router.get('/stream/video')
def stream_handler(url: str, request: Request):
    media_type = 'video/mp4'

    range_header = request.headers.get('Range', None)

    if range_header:
        from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
        if not until_bytes:
            until_bytes = int(from_bytes) + int(1024 * 1024 * 1)
        headers = {'Range': 'bytes=%s-%s' % (from_bytes, until_bytes)}
        r = apiClient.http.get(url, headers=headers)
        data = r.content
        response = Response(data, 206, media_type=media_type)
        response.headers['Content-Range'] = r.headers.get('Content-Range')
        return response

    r = apiClient.http.get(url, stream=True)

    return StreamingResponse(iterate_data(r), media_type=media_type)


@router.get('/download/video')
def download_file(url: str, request: Request):
    try:
        data = decode_data(get_key(), encoded_url.encode('utf8'))
        url = data['url']
        filename = f"{data['artist']}-{data['title']}.mp3"
        range_header = request.headers.get('Range', None)
        if range_header:
            from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
            if not until_bytes:
                until_bytes = int(from_bytes) + int(1024 * 1024 * 1)
            headers = {'Range': 'bytes=%s-%s' % (from_bytes, until_bytes)}
            r = apiClient.http.get(url, headers=headers)
            response = Response(iterate_data(r), 206, media_type='audio/mpeg')
            response.headers['Content-Range'] = r.headers.get('Content-Range')
            response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
            response.headers['Content-Length'] = r.headers['Content-Length']
            return response

        r = apiClient.http.get(url, stream=True)
        response = StreamingResponse(iterate_data(r), media_type='audio/mpeg')
        response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.headers['Content-Length'] = r.headers['Content-Length']
        return response

    except Exception as e:
        main.app.logger.info('Exception', e.with_traceback())


async def iterate_data(resp, chunk=2048):
    for data_chunk in resp.iter_content(chunk_size=chunk):
        yield data_chunk
