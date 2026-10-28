# Defensive case study: observations are not account evidence

## Scope of the review

A private prototype was reviewed as source text only. It combined generated identity candidates, mail-server responses and speculative API calls to infer whether an account existed. No external service was tested, and no claimed account result was validated.

The original operational script is not included. This note records general engineering lessons without service names, endpoint lists, credentials, personal data or operational evasion details. The accompanying CSV examples and analyzer were newly created for offline education.

## Findings from static inspection

| Observed design | Why the conclusion was unreliable | Defensive engineering response |
|---|---|---|
| Guessed API routes and authorization values were treated as an integration contract. | A hypothesis about an endpoint is not evidence that the service implements it. | For an application you control, use its documented test interface and controlled fixtures. |
| Mail acceptance was used as a step toward an application-account conclusion. | Mail handling, email ownership and application registration are different facts. | Keep those facts separate. Verify ownership through the application's consent-based verification flow. |
| Many network, parsing and endpoint errors returned the same boolean as an absent account. | Operational failure was silently converted into a negative finding. | Represent observations as success, failure or indeterminate, with an explicit reason. |
| Detailed values could enter diagnostic logs. | A log can retain identifiers or authentication material even when another output is encrypted. | Minimize logs, omit credentials and raw identities, and document retention and access. |

The HTTP `404` status concerns the requested resource; by itself it is not an account-existence verdict. See [RFC 9110, section 15.5.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.5). Email ownership verification is a separate application workflow, as described by [OWASP's email validation and verification guidance](https://cheatsheetseries.owasp.org/cheatsheets/Email_Validation_and_Verification_Cheat_Sheet.html).

## A useful defensive experiment

For a local application with dummy accounts, compare how equivalent authentication failures are represented. Keep only cohort labels, status codes, response sizes and elapsed times in the exported measurements. The included analyzer works entirely on that existing CSV; it has no request generation or account-checking capability.

Differences can motivate a review of your own authentication design. They are not a vulnerability finding by themselves. Headers, redirects, response content, caching, repeated-measurement design and infrastructure noise also matter and are outside this small analyzer's scope.

[OWASP's Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#authentication-and-error-messages) recommends avoiding account-dependent error disclosures, including differences in responses and processing time. Its guidance also covers throttling and monitoring. Treat these as application controls to design and validate together, rather than assuming that a uniform message alone solves the problem.

## Evidence available here

- Static design observations summarized above, without publishing the operational prototype.
- Two reproducible synthetic CSV fixtures.
- An offline analyzer with strict input validation and aggregate-only output.
- Tests for the fixture calculations, invalid inputs and insufficient samples.

No findings against a real organization, account discoveries, penetration-test results or production-security assurances are claimed.
