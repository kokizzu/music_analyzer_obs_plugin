#!/usr/bin/env python3
"""Guard the OBS-side Beat This boundary without starting OBS or a model."""
import sys as _makefile_sys
from pathlib import Path as _MakefilePath
_makefile_sys.path.insert(0, str(_MakefilePath(__file__).resolve().parents[1] / 'scripts'))
from makefile_source import read_makefile

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"test_beat_this_obs_sidecar: {message}")


def main() -> None:
    plugin = read_makefile(ROOT / "src" / "plugin.cpp", encoding="utf-8")
    client = read_makefile(ROOT / "src" / "beat_this_sidecar_client.cpp", encoding="utf-8")
    makefile = read_makefile(ROOT / "Makefile", encoding="utf-8")

    require('obs_data_set_default_bool(settings, "enable_beat_this_sidecar", false)' in plugin,
            "sidecar must remain disabled by default")
    capture = plugin.split("void capture_beat_this_sidecar_sample", 1)[1].split("void beat_this_sidecar_worker", 1)[0]
    require("client." not in capture and "fork(" not in capture and ".assign(" not in capture and
            ".resize(" not in capture and "push_back(" not in capture,
            "audio capture may not spawn, request inference, or allocate a packet")
    worker = plugin.split("void beat_this_sidecar_worker", 1)[1].split("void apply_beat_this_sidecar_fallback", 1)[0]
    require("client.warm(config)" in worker and "client.request(" in worker,
            "only the separate sidecar worker may start or request the model")
    fallback = plugin.split("void apply_beat_this_sidecar_fallback", 1)[1].split("void copy_ring_to_pending", 1)[0]
    require("snapshot->bpm_confidence >= mao::kBpmDisplayConfidenceThreshold" in fallback,
            "sidecar must not replace an already displayable normal BPM")
    require("kBeatThisSidecarCandidateLifetime" in fallback,
            "sidecar BPM must expire rather than persist indefinitely")
    require("O_NONBLOCK" in client and "poll(&descriptor, 1" in client,
            "sidecar writes must be bounded when the child is still loading")
    require("test-beat-this-sidecar-client" in makefile,
            "model-free sidecar client test must stay in the Makefile")

    print("test_beat_this_obs_sidecar: ok")


if __name__ == "__main__":
    main()
