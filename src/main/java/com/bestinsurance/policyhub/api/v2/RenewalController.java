package com.bestinsurance.policyhub.api.v2;

import com.bestinsurance.policyhub.renewal.RenewalQuote;
import com.bestinsurance.policyhub.renewal.RenewalQuoteCache;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v2/policies")
public class RenewalController {

    private final RenewalQuoteCache quoteCache;

    public RenewalController(RenewalQuoteCache quoteCache) {
        this.quoteCache = quoteCache;
    }

    /**
     * Returns the risk-adjusted renewal premium quote for the given policy.
     * Quote is cached for up to 7 days. See RenewalQuoteCache for caching behaviour.
     */
    @GetMapping("/{policyId}/renewal-quote")
    public ResponseEntity<RenewalQuoteResponse> getRenewalQuote(@PathVariable Long policyId) {
        RenewalQuote quote = quoteCache.getOrCompute(policyId);
        return ResponseEntity.ok(RenewalQuoteResponse.from(quote));
    }
}

