from supabase import create_client, Client
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)

class SupabaseSignaling:
    def __init__(self):
        self.supabase: Client | None = None
        if settings.webrtc_enabled and settings.supabase_url and settings.supabase_anon_key:
            try:
                self.supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
                logger.info("Supabase client initialized for WebRTC signaling.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("Supabase credentials missing or WebRTC disabled. WebRTC signaling will not work.")

    def post_answer(self, session_id: str, sdp_data: str):
        """
        Posts the WebRTC answer back to the Supabase signaling channel.
        """
        if not self.supabase:
            return
            
        try:
            self.supabase.table('signaling').insert({
                'session_id': session_id,
                'type': 'answer',
                'sdp': sdp_data
            }).execute()
            logger.info(f"Posted WebRTC answer for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to post WebRTC answer: {e}")

# Global instance
signaling_service = SupabaseSignaling()
