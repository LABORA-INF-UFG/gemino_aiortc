from collections import OrderedDict
from typing import Dict, List, Optional, Union

from ..rtcrtpparameters import (
    RTCRtcpFeedback,
    RTCRtpCapabilities,
    RTCRtpCodecCapability,
    RTCRtpCodecParameters,
    RTCRtpHeaderExtensionCapability,
    RTCRtpHeaderExtensionParameters,
)
from .base import Decoder, Encoder
from .g711 import PcmaDecoder, PcmaEncoder, PcmuDecoder, PcmuEncoder
from .h264 import H264Decoder, H264Encoder, h264_depayload
from .opus import OpusDecoder, OpusEncoder
from .vpx import Vp8Decoder, Vp8Encoder, vp8_depayload
from .keypointcodec import KeypointsEncoder, KeypointsDecoder
from .keypoints_pb2 import KeypointInfo

PCMU_CODEC = RTCRtpCodecParameters(
    mimeType="audio/PCMU", clockRate=8000, channels=1, payloadType=0
)
PCMA_CODEC = RTCRtpCodecParameters(
    mimeType="audio/PCMA", clockRate=8000, channels=1, payloadType=8
)


KEYPOINTS_CODEC = RTCRtpCodecParameters(
    mimeType="keypoints/dummy", clockRate=8000, channels=1, payloadType=8
)

CODECS: Dict[str, List[RTCRtpCodecParameters]] = {
    "audio": [
        RTCRtpCodecParameters(
            mimeType="audio/opus", clockRate=48000, channels=2, payloadType=96
        ),
        PCMU_CODEC,
        PCMA_CODEC,
    ],
    "video": [],
    "keypoints": [
        KEYPOINTS_CODEC
    ],
    "lr_video": [],
}
HEADER_EXTENSIONS: Dict[str, List[RTCRtpHeaderExtensionParameters]] = {
    "audio": [
        RTCRtpHeaderExtensionParameters(id=1, uri="urn:ietf:params:rtp-hdrext:sdes:mid")
    ],
    "video": [
        RTCRtpHeaderExtensionParameters(
            id=1, uri="urn:ietf:params:rtp-hdrext:sdes:mid"
        ),
        RTCRtpHeaderExtensionParameters(
            id=2, uri="http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time"
        ),
    ],
    "keypoints": [
        RTCRtpHeaderExtensionParameters(id=1, uri="urn:ietf:params:rtp-hdrext:sdes:mid")
    ],
    "lr_video": [
        RTCRtpHeaderExtensionParameters(
            id=1, uri="urn:ietf:params:rtp-hdrext:sdes:mid"
        ),
        RTCRtpHeaderExtensionParameters(
            id=2, uri="http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time"
        ),
    ],
}


def init_codecs() -> None:
    dynamic_pt = 97

    def add_video_codec(
        mimeType: str, parameters: Optional[OrderedDict] = None
    ) -> None:
        nonlocal dynamic_pt

        clockRate = 90000
        CODECS["video"] += [
            RTCRtpCodecParameters(
                mimeType=mimeType,
                clockRate=clockRate,
                payloadType=dynamic_pt,
                rtcpFeedback=[
                    RTCRtcpFeedback(type="nack"),
                    RTCRtcpFeedback(type="nack", parameter="pli"),
                    RTCRtcpFeedback(type="goog-remb"),
                ],
                parameters=parameters or OrderedDict(),
            ),
            RTCRtpCodecParameters(
                mimeType="video/rtx",
                clockRate=clockRate,
                payloadType=dynamic_pt + 1,
                parameters=OrderedDict([("apt", dynamic_pt)]),
            ),
        ]
        dynamic_pt += 2

    add_video_codec("video/VP8")
    add_video_codec(
        "video/H264",
        OrderedDict(
            (
                ("packetization-mode", "1"),
                ("level-asymmetry-allowed", "1"),
                ("profile-level-id", "42001f"),
            )
        ),
    )
    add_video_codec(
        "video/H264",
        OrderedDict(
            (
                ("packetization-mode", "1"),
                ("level-asymmetry-allowed", "1"),
                ("profile-level-id", "42e01f"),
            )
        ),
    )

    CODECS["lr_video"] = CODECS["video"]


def depayload(codec: RTCRtpCodecParameters, payload: bytes) -> bytes:
    if codec.name == "VP8":
        return vp8_depayload(payload)
    elif codec.name == "H264":
        return h264_depayload(payload)
    else:
        return payload


def get_capabilities(kind: str) -> RTCRtpCapabilities:
    if kind not in CODECS:
        raise ValueError(f"cannot get capabilities for unknown media {kind}")

    codecs = []
    rtx_added = False
    for params in CODECS[kind]:
        if not is_rtx(params):
            codecs.append(
                RTCRtpCodecCapability(
                    mimeType=params.mimeType,
                    clockRate=params.clockRate,
                    channels=params.channels,
                    parameters=params.parameters,
                )
            )
        elif not rtx_added:
            # There will only be a single entry in codecs[] for retransmission
            # via RTX, with sdpFmtpLine not present.
            codecs.append(
                RTCRtpCodecCapability(
                    mimeType=params.mimeType, clockRate=params.clockRate
                )
            )
            rtx_added = True

    headerExtensions = []
    for extension in HEADER_EXTENSIONS[kind]:
        headerExtensions.append(RTCRtpHeaderExtensionCapability(uri=extension.uri))
    return RTCRtpCapabilities(codecs=codecs, headerExtensions=headerExtensions)


def get_decoder(codec: RTCRtpCodecParameters) -> Decoder:
    mimeType = codec.mimeType.lower()

    if mimeType == "audio/opus":
        return OpusDecoder()
    elif mimeType == "audio/pcma":
        return PcmaDecoder()
    elif mimeType == "audio/pcmu":
        return PcmuDecoder()
    elif mimeType == "video/h264":
        return H264Decoder()
    elif mimeType == "video/vp8":
        return Vp8Decoder()
    elif mimeType == "keypoints/dummy":
        return KeypointsDecoder()
    else:
        raise ValueError(f"No decoder found for MIME type `{mimeType}`")


def get_encoder(codec: RTCRtpCodecParameters) -> Encoder:
    mimeType = codec.mimeType.lower()

    if mimeType == "audio/opus":
        return OpusEncoder()
    elif mimeType == "audio/pcma":
        return PcmaEncoder()
    elif mimeType == "audio/pcmu":
        return PcmuEncoder()
    elif mimeType == "video/h264":
        return H264Encoder()
    elif mimeType == "video/vp8":
        return Vp8Encoder()
    elif mimeType == "keypoints/dummy":
        return KeypointsEncoder()
    else:
        raise ValueError(f"No encoder found for MIME type `{mimeType}`")


def is_rtx(codec: Union[RTCRtpCodecCapability, RTCRtpCodecParameters]) -> bool:
    return codec.name.lower() == "rtx"


init_codecs()
