# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    float_or_none,
    int_or_none,
)


class StreamableIE(InfoExtractor):
    _VALID_URL = r'https?://streamable\.com/(?:[es]/)?(?P<id>\w+)'
    _TESTS = [
        {
            'url': 'https://streamable.com/dnd1',
            'md5': '3e3bc5ca088b48c2d436529b64397fef',
            'info_dict': {
                'id': 'dnd1',
                'ext': 'mp4',
                'title': 'Mikel Oiarzabal scores to make it 0-3 for La Real against Espanyol',
                'thumbnail': r're:https?://.*\.jpg$',
                'uploader': 'teabaker',
                'timestamp': 1454964157.35115,
                'upload_date': '20160208',
                'duration': 61.516,
                'view_count': int,
            }
        },
        {
            'url': 'https://streamable.com/moo',
            'md5': '2cf6923639b87fba3279ad0df3a64e73',
            'info_dict': {
                'id': 'moo',
                'ext': 'mp4',
                'title': '"Please don\'t eat me!"',
                'thumbnail': r're:https?://.*\.jpg$',
                'timestamp': 1426115495,
                'upload_date': '20150311',
                'duration': 12,
                'view_count': int,
            }
        },
        {
            'url': 'https://streamable.com/e/dnd1',
            'only_matching': True,
        },
        {
            'url': 'https://streamable.com/s/okkqk/drxjds',
            'only_matching': True,
        }
    ]

    @staticmethod
    def _extract_url(webpage):
        mobj = re.search(
            r'<iframe[^>]+src=(?P<q1>[\'"])(?P<src>(?:https?:)?//streamable\.com/(?:(?!\1).+))(?P=q1)',
            webpage)
        if mobj:
            return mobj.group('src')

    def _real_extract(self, url):
        video_id = self._match_id(url)

        
        video = self._download_json(
            f'https://ajax.streamable.com/videos/{video_id}', video_id)

        
        status = video.get('status')
        if status != 2:
            raise ExtractorError(
                'This video is currently unavailable. It may still be uploading or processing.',
                expected=True)

        title = video.get('reddit_title') or video.get('title')

        
        formats = []
        for key, info in (video.get('files') or {}).items():
            url = info.get('url')
            if not url:
                continue
            formats.append({
                'format_id': key,
                'url': self._proto_relative_url(url),
                'width': int_or_none(info.get('width')),
                'height': int_or_none(info.get('height')),
                'filesize': int_or_none(info.get('size')),
                'fps': int_or_none(info.get('framerate')),
                'vbr': float_or_none(info.get('bitrate'), 1000)
            })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': video.get('description'),
            'thumbnail': self._proto_relative_url(video.get('thumbnail_url')),
            'uploader': video.get('owner', {}).get('user_name'),
            'timestamp': float_or_none(video.get('date_added') or video.get('created_at')),
            'duration': float_or_none(video.get('duration')),
            'view_count': int_or_none(video.get('plays')),
            'formats': formats
        }
