import numpy as np

class ProbabilityCalibrator:
    def __init__(self, temperature: float = 1.2):
        self.temperature = temperature

    def calibrate(self, probability: float) -> float:
        """Applies Temperature Scaling to raw probability logits estimates."""
        # Convert probability back to logit
        prob_clipped = np.clip(probability, 1e-7, 1.0 - 1e-7)
        logit = np.log(prob_clipped / (1.0 - prob_clipped))
        
        # Scale logit with temperature parameter
        scaled_logit = logit / self.temperature
        
        # Sigmoid back to probability
        calibrated_prob = 1.0 / (1.0 + np.exp(-scaled_logit))
        return float(calibrated_prob)

calibrator = ProbabilityCalibrator()
