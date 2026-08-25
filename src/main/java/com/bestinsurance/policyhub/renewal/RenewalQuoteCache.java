package com.bestinsurance.policyhub.renewal;

import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;

/**
 * Cache layer for renewal quotes. Quotes are expensive to compute (requires
 * policy_metadata read + risk factor resolution) and stable over the 7-day
 * renewal window, so we cache by policy_id with a 7-day TTL.
 *
 * NOTE (POLICY-10): cache key does not include a hash of policy_metadata fields.
 * If coverage_tier, loss_ratio, or claims_history are updated in policy_metadata
 * after a quote is cached, the cached quote will be served until TTL expires.
 * Tracked for Q1 fix — see POLICY-10.
 */
@Service
public class RenewalQuoteCache {

    private static final Duration QUOTE_TTL = Duration.ofDays(7);

    private final PremiumRecalcEngine recalcEngine;
    private final RenewalQuoteRepository quoteRepository;

    public RenewalQuoteCache(PremiumRecalcEngine recalcEngine,
                             RenewalQuoteRepository quoteRepository) {
        this.recalcEngine = recalcEngine;
        this.quoteRepository = quoteRepository;
    }

    // Cache key: policy_id only. Does not account for policy_metadata changes.
    @Cacheable(value = "renewalQuotes", key = "#policyId")
    public RenewalQuote getOrCompute(Long policyId) {
        return quoteRepository.findActiveQuote(policyId)
                .orElseGet(() -> {
                    PolicyDocument policy = quoteRepository.loadPolicy(policyId);
                    RenewalQuote quote = recalcEngine.calculate(policy);
                    quote.setExpiresAt(Instant.now().plus(QUOTE_TTL));
                    return quoteRepository.save(quote);
                });
    }

    @CacheEvict(value = "renewalQuotes", key = "#policyId")
    public void invalidate(Long policyId) {
        quoteRepository.expireActiveQuote(policyId);
    }
}

