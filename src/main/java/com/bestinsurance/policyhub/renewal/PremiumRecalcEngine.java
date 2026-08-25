package com.bestinsurance.policyhub.renewal;

import com.bestinsurance.policyhub.model.PolicyDocument;
import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * Calculates risk-adjusted renewal premiums using policy_metadata fields
 * introduced in CHG0010001. Risk factors: coverage_tier, claims_history,
 * state_code, and loss_ratio from the metadata JSON column.
 */
@Service
public class PremiumRecalcEngine {

    private static final BigDecimal BASE_RATE_MULTIPLIER = new BigDecimal("1.0350"); // 3.5% base renewal increase

    public RenewalQuote calculate(PolicyDocument policy) {
        BigDecimal basePremium = policy.getCurrentPremium()
                .multiply(BASE_RATE_MULTIPLIER)
                .setScale(2, RoundingMode.HALF_UP);

        BigDecimal riskFactor = resolveRiskFactor(policy.getPolicyMetadata());
        BigDecimal finalPremium = basePremium.multiply(riskFactor).setScale(2, RoundingMode.HALF_UP);

        return RenewalQuote.builder()
                .policyId(policy.getId())
                .basePremium(basePremium)
                .riskAdjFactor(riskFactor)
                .finalPremium(finalPremium)
                .stateCode(policy.getStateCode())
                .coverageTier(extractCoverageTier(policy.getPolicyMetadata()))
                .build();
    }

    private BigDecimal resolveRiskFactor(JsonNode metadata) {
        if (metadata == null || metadata.isNull()) return BigDecimal.ONE;

        double lossRatio = metadata.path("loss_ratio").asDouble(0.0);
        String tier = metadata.path("coverage_tier").asText("STANDARD");
        int claimsLast3Yr = metadata.path("claims_last_3yr").asInt(0);

        double factor = 1.0;
        if (lossRatio > 0.75) factor += 0.12;
        else if (lossRatio > 0.55) factor += 0.06;

        factor += switch (tier) {
            case "PREMIUM"   -> -0.03;
            case "PREFERRED" -> -0.01;
            case "HIGH_RISK" ->  0.18;
            default          ->  0.0;
        };

        if (claimsLast3Yr >= 2) factor += 0.08;
        else if (claimsLast3Yr == 1) factor += 0.03;

        return BigDecimal.valueOf(factor).setScale(4, RoundingMode.HALF_UP);
    }

    private String extractCoverageTier(JsonNode metadata) {
        if (metadata == null || metadata.isNull()) return "STANDARD";
        return metadata.path("coverage_tier").asText("STANDARD");
    }
}

