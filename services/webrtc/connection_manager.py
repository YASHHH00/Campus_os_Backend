import asyncio
import json
import base64
from aiortc import RTCPeerConnection, RTCSessionDescription
from services.webrtc.signaling import signaling_service
from services.webrtc.data_channel_handler import handle_message
from core.logging import get_logger

logger = get_logger(__name__)

# Keep active peer connections in memory
active_connections = {}
incoming_chunks = {}

async def handle_channel_message(channel, message_text: str):
    global incoming_chunks
    try:
        data = json.loads(message_text)
        msg_type = data.get("type")
        
        if msg_type == "_chunk":
            message_id = data["messageId"]
            seq = data["seq"]
            total = data["total"]
            chunk_data = base64.b64decode(data["data"])
            
            if message_id not in incoming_chunks:
                incoming_chunks[message_id] = [None] * total
            
            incoming_chunks[message_id][seq] = chunk_data
            
            if all(c is not None for c in incoming_chunks[message_id]):
                full_bytes = b"".join(incoming_chunks[message_id])
                del incoming_chunks[message_id]
                full_message = json.loads(full_bytes.decode("utf-8"))
                response = await handle_message(full_message)
                channel.send(json.dumps(response))
            return
            
        response = await handle_message(data)
        channel.send(json.dumps(response))
    except Exception as e:
        logger.error(f"Error handling WebRTC message: {e}")

async def setup_peer_connection(session_id: str, offer_sdp: str):
    if session_id in active_connections:
        logger.info(f"Connection for session {session_id} already exists or is being setup.")
        return

    logger.info(f"Setting up WebRTC PeerConnection for session {session_id}...")
    pc = RTCPeerConnection()
    active_connections[session_id] = pc

    @pc.on("datachannel")
    def on_datachannel(channel):
        logger.info(f"WebRTC DataChannel established: {channel.label}")
        
        @channel.on("message")
        def on_message(message):
            asyncio.create_task(handle_channel_message(channel, message))

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logger.info(f"ICE Connection State for session {session_id}: {pc.iceConnectionState}")
        if pc.iceConnectionState in ["failed", "closed", "disconnected"]:
            logger.info(f"Cleaning up WebRTC PeerConnection for session {session_id}")
            await pc.close()
            active_connections.pop(session_id, None)

    try:
        # 1. Set remote offer
        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)

        # 2. Create local answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        # 3. Post answer back to Supabase
        answer_payload = {
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }
        signaling_service.post_answer(session_id, json.dumps(answer_payload))
        logger.info(f"WebRTC Answer posted back for session {session_id}")
    except Exception as e:
        logger.error(f"Failed to setup WebRTC PeerConnection for session {session_id}: {e}")
        await pc.close()
        active_connections.pop(session_id, None)

async def signaling_listener_loop():
    logger.info("Starting WebRTC signaling listener loop...")
    while True:
        if signaling_service.supabase:
            try:
                # Poll signaling table for any 'offer' rows
                res = signaling_service.supabase.table('signaling').select('*').eq('type', 'offer').execute()
                offers = res.data
                
                for row in offers:
                    session_id = row.get("session_id")
                    sdp_json_str = row.get("sdp")
                    
                    if not session_id or not sdp_json_str:
                        continue
                        
                    # Only process if we haven't already handled it
                    if session_id not in active_connections:
                        try:
                            decoded = json.loads(sdp_json_str)
                            offer_sdp = decoded.get("sdp")
                            if offer_sdp:
                                asyncio.create_task(setup_peer_connection(session_id, offer_sdp))
                        except Exception as e:
                            logger.error(f"Error parsing offer SDP for session {session_id}: {e}")
            except Exception as e:
                logger.error(f"Error polling signaling table: {e}")
        else:
            # Sleep longer if Supabase client is not initialized
            await asyncio.sleep(5)
            continue
            
        await asyncio.sleep(2.0)

def start_webrtc_listener():
    asyncio.create_task(signaling_listener_loop())
