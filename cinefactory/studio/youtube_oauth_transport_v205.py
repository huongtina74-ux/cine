"""Optional production provider transport (never connects or uploads on import).

OAuth token must be supplied by the channel owner at action time. This module
does not initiate OAuth login, claim ownership, or export credentials.
"""
from __future__ import annotations

from datetime import date,timedelta
from pathlib import Path

YT_UPLOAD_SCOPE="https://www.googleapis.com/auth/youtube.upload"
YT_READ_SCOPE="https://www.googleapis.com/auth/youtube.readonly"
YT_ANALYTICS_SCOPE="https://www.googleapis.com/auth/yt-analytics.readonly"


def _credentials(owner_authorized_oauth_file,scopes):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    p=Path(owner_authorized_oauth_file).resolve(strict=True)
    cred=Credentials.from_authorized_user_file(str(p),scopes=scopes)
    if not cred.valid:
        if not cred.expired or not cred.refresh_token:
            raise PermissionError("OWNER_GOOGLE_OAUTH_TOKEN_INVALID_OR_MISSING")
        cred.refresh(Request())
    if not cred.valid:
        raise PermissionError("OWNER_GOOGLE_OAUTH_TOKEN_NOT_ACTIVE")
    if not cred.has_scopes(scopes):
        raise PermissionError("REQUIRED_OWNER_OAUTH_SCOPES_NOT_GRANTED")
    return cred


class GoogleYouTubePrivateTransport:
    """Explicit upload-only provider adapter. Caller enforces trusted signature."""
    def __init__(self, owner_oauth_file):
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        creds=_credentials(owner_oauth_file,[YT_UPLOAD_SCOPE,YT_READ_SCOPE])
        self.service=build("youtube","v3",credentials=creds,cache_discovery=False)
        response=self.service.channels().list(part="id",mine=True,maxResults=2).execute()
        channels=response.get("items",[])
        if len(channels)!=1 or not channels[0].get("id"):
            raise PermissionError("OAUTH_ACCOUNT_CHANNEL_ID_NOT_UNAMBIGUOUS")
        self.owned_channel_id=channels[0]["id"]

    def upload_private(self,master_path,metadata):
        from googleapiclient.http import MediaFileUpload
        if metadata.get("visibility")!="private":
            raise PermissionError("MANDATORY_PRIVATE_UPLOAD")
        movie=Path(master_path).resolve(strict=True)
        media=MediaFileUpload(str(movie),mimetype="video/mp4",
                              chunksize=8*1024*1024,resumable=True)
        body={
            "snippet":{"title":metadata["title"],
                       "description":metadata["description"],
                       "categoryId":str(metadata.get("categoryId") or "24")},
            "status":{"privacyStatus":"private","selfDeclaredMadeForKids":metadata["made_for_kids"]},
        }
        request=self.service.videos().insert(
            part="snippet,status",body=body,media_body=media,notifySubscribers=False)
        finished=None
        while finished is None:
            _,finished=request.next_chunk()
        if not isinstance(finished,dict):
            raise RuntimeError("YOUTUBE_UPLOAD_RECEIPT_MALFORMED")
        return finished.get("id")

    def fetch_video(self,video_id):
        response=self.service.videos().list(
            id=video_id,part="snippet,status").execute()
        entries=response.get("items",[])
        if len(entries)!=1:
            raise RuntimeError("YOUTUBE_VIDEO_NOT_FOUND_AFTER_UPLOAD")
        found=entries[0]
        return {
            "id":found["id"],
            "channel_id":found.get("snippet",{}).get("channelId"),
            "privacy_status":found.get("status",{}).get("privacyStatus"),
        }


class GoogleYouTubeOwnedAnalyticsTransport:
    def __init__(self, owner_oauth_file, verified_channel_id):
        from googleapiclient.discovery import build
        # The Analytics OAuth identity must independently prove ownership
        # through the Data API; a caller-provided channel id is insufficient.
        self.creds=_credentials(owner_oauth_file,[YT_ANALYTICS_SCOPE,YT_READ_SCOPE])
        if not verified_channel_id or not verified_channel_id.startswith("UC"):
            raise ValueError("EXACT_VERIFIED_OWNED_CHANNEL_REQUIRED")
        identity=build("youtube","v3",credentials=self.creds,
                       cache_discovery=False)
        answer=identity.channels().list(
            part="id",mine=True,maxResults=2,
        ).execute()
        channels=answer.get("items",[])
        if len(channels)!=1 or channels[0].get("id")!=verified_channel_id:
            raise PermissionError("ANALYTICS_OAUTH_NOT_OWNED_CHANNEL")
        self.owned_channel_id=verified_channel_id
        self.service=build("youtubeAnalytics","v2",credentials=self.creds,
                           cache_discovery=False)

    def fetch_owned_video_metrics(self,channel_id,video_id,*,days=30):
        if channel_id!=self.owned_channel_id:
            raise PermissionError("OWNED_ANALYTICS_CHANNEL_MISMATCH")
        if days<7 or days>90:
            raise ValueError("ANALYTICS_LOOKBACK_MUST_BE_7_TO_90_DAYS")
        end=date.today()-timedelta(days=1)
        start=end-timedelta(days=days-1)
        # Only stable metrics; do not infer private RPM/CTR unless the API returns them.
        response=self.service.reports().query(
            ids="channel==MINE",startDate=start.isoformat(),
            endDate=end.isoformat(),dimensions="video",
            filters="video=="+video_id,
            metrics="views,estimatedMinutesWatched,averageViewDuration"
        ).execute()
        columns=[c.get("name") for c in response.get("columnHeaders",[])]
        rows=response.get("rows",[])
        if not rows:
            raise RuntimeError("OWNED_ANALYTICS_NO_MATURE_DATA")
        mapping=dict(zip(columns,rows[0]))
        if mapping.get("video")!=video_id:
            raise ValueError("ANALYTICS_NOT_FOR_REQUESTED_OWNED_VIDEO")
        metrics={
            "video_id":video_id,"window_start":start.isoformat(),
            "window_end":end.isoformat(),
            "views":mapping.get("views"),
            "watch_minutes":mapping.get("estimatedMinutesWatched"),
            "average_view_duration_seconds":mapping.get("averageViewDuration"),
        }
        return {
            "metrics":metrics,
            "provenance":{
                "provider":"YOUTUBE_ANALYTICS_API",
                "authenticated_provider_readback":True,
                "channel_id":channel_id,"video_id":video_id,
            },
        }
