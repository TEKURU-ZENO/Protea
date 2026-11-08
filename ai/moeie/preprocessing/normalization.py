"""
PROTEA Phase 11: Multi-Omics Preprocessing & Normalization
Enforces Scientific Guardrail: Record both raw and normalized/corrected representations.
"""

from __future__ import annotations
import math
from typing import Dict, List, Any, Optional
from ai.moeie.schema import OmicsMeasurement, OmicsModality


class MultiOmicsNormalizer:
    """Modality-specific normalization preserving raw and corrected representations."""

    @classmethod
    def normalize_measurements(
        cls,
        measurements: List[OmicsMeasurement],
        modality: OmicsModality
    ) -> List[OmicsMeasurement]:
        """
        Applies modality-appropriate transformation while preserving raw_value.
        - Transcriptomics: log1p(CP10k)
        - Proteomics: median centering and missing-value imputation
        - Epigenomics: log2(1 + counts)
        """
        normalized_list: List[OmicsMeasurement] = []

        if modality in [OmicsModality.TRANSCRIPTOMICS, OmicsModality.SINGLE_CELL, OmicsModality.SPATIAL]:
            # Calculate total library counts per sample
            sample_totals: Dict[str, float] = {}
            for m in measurements:
                sample_totals[m.sample_id] = sample_totals.get(m.sample_id, 0.0) + m.raw_value

            for m in measurements:
                total = max(1.0, sample_totals.get(m.sample_id, 1.0))
                # Counts per 10,000 + log1p
                cp10k = (m.raw_value / total) * 10000.0
                norm_val = round(math.log1p(cp10k), 4)

                m_norm = OmicsMeasurement(
                    measurement_id=m.measurement_id,
                    sample_id=m.sample_id,
                    feature_id=m.feature_id,
                    modality=m.modality,
                    raw_value=m.raw_value,  # PRESERVE RAW
                    normalized_value=norm_val,
                    unit="log1p_cp10k",
                    is_missing=m.is_missing,
                    quality_flag=m.quality_flag
                )
                normalized_list.append(m_norm)

        elif modality in [OmicsModality.PROTEOMICS, OmicsModality.PHOSPHOPROTEOMICS]:
            # For proteomics, calculate non-missing median for scaling
            non_missing_vals = [m.raw_value for m in measurements if not m.is_missing and m.raw_value > 0.0]
            median_val = sorted(non_missing_vals)[len(non_missing_vals) // 2] if non_missing_vals else 10.0
            # Min-probability surrogate for imputation (mean of bottom 5%)
            impute_val = round(min(non_missing_vals) * 0.5, 2) if non_missing_vals else 1.0

            for m in measurements:
                if m.is_missing or m.raw_value <= 0.0:
                    norm_val = impute_val
                    q_flag = "IMPUTED_MIN_PROB"
                else:
                    norm_val = round(m.raw_value - median_val, 4)
                    q_flag = "PASS"

                m_norm = OmicsMeasurement(
                    measurement_id=m.measurement_id,
                    sample_id=m.sample_id,
                    feature_id=m.feature_id,
                    modality=m.modality,
                    raw_value=m.raw_value,  # PRESERVE RAW
                    normalized_value=norm_val,
                    unit="median_centered_log2",
                    is_missing=m.is_missing,
                    quality_flag=q_flag
                )
                normalized_list.append(m_norm)

        else:
            # Default fallback: log2(1 + x)
            for m in measurements:
                norm_val = round(math.log2(max(0.0, m.raw_value) + 1.0), 4)
                m_norm = OmicsMeasurement(
                    measurement_id=m.measurement_id,
                    sample_id=m.sample_id,
                    feature_id=m.feature_id,
                    modality=m.modality,
                    raw_value=m.raw_value,
                    normalized_value=norm_val,
                    unit="log2_transformed",
                    is_missing=m.is_missing,
                    quality_flag=m.quality_flag
                )
                normalized_list.append(m_norm)

        return normalized_list
