from fastapi import APIRouter
from ..models.bridge import BridgeConfig, BridgeSend

router = APIRouter()

BRIDGE_CFG = BridgeConfig()

@router.post("/config")
def set_config(cfg: BridgeConfig):
    global BRIDGE_CFG
    BRIDGE_CFG = cfg
    return {"ok": True, "cfg": BRIDGE_CFG}

@router.get("/config")
def get_config():
    return BRIDGE_CFG

@router.post("/midi/send")
def midi_send(payload: BridgeSend):
    # TODO: send to virtual MIDI (kick/snare test)
    return {"ok": True, "sent": payload.dict()}

@router.post("/osc/send")
def osc_send(payload: BridgeSend):
    # TODO: send OSC messages (/dawsheet/section, etc.)
    return {"ok": True, "sent": payload.dict()}
