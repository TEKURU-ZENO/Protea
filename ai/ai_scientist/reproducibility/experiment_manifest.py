"""
PROTEA AI Scientist - Cryptographic Experiment Manifest
Generates immutable provenance manifests with SHA-256 hashes, seeds, and tool versions.
"""

from typing import Dict, Any, List
import hashlib
import json
import time


class ExperimentManifestBuilder:
    """
    Builds cryptographic manifests guaranteeing full auditability and exact reproducibility.
    """

    PROTEA_TOOL_VERSIONS = {
        "protea_platform": "1.0.0-phase9",
        "python": "3.10+",
        "pytorch": "2.4.0",
        "pytorch_geometric": "2.5.0",
        "scipy": "1.13.0",
        "numpy": "2.0+",
    }

    def generate_manifest(
        self,
        experiment_id: str,
        hypothesis_id: str,
        random_seeds: List[int],
        config: Dict[str, Any],
        raw_outputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Creates an immutable, hashed manifest for an experiment.
        """
        config_serialized = json.dumps(config, sort_keys=True)
        config_hash = hashlib.sha256(config_serialized.encode("utf-8")).hexdigest()

        output_serialized = json.dumps(raw_outputs, sort_keys=True)
        output_hash = hashlib.sha256(output_serialized.encode("utf-8")).hexdigest()

        manifest_payload = {
            "experiment_id": experiment_id,
            "hypothesis_id": hypothesis_id,
            "timestamp": time.time(),
            "config_sha256": config_hash,
            "output_sha256": output_hash,
            "random_seeds": random_seeds,
            "tool_versions": self.PROTEA_TOOL_VERSIONS,
        }

        overall_signature = hashlib.sha256(
            json.dumps(manifest_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

        manifest_payload["manifest_signature"] = overall_signature

        return manifest_payload
