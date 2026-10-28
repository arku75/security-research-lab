# Security Research Lab

Offline tools and security research archives maintained by **Ema Curk / arku75**.

[Español](README.es.md) · [Defensive case study](docs/ACCOUNT_ENUMERATION_REVIEW.md) · [Upstream references](docs/UPSTREAM_REFERENCES.md) · [Publication scope](docs/PUBLICATION_SCOPE.md)

This release contains two small Python tools, synthetic examples, an anonymized static review and one recovered wireless script archived with execution disabled by default. The new utilities and documentation were prepared with AI assistance while reviewing a broader local research collection. This does not claim that the full collection was reviewed, authored here or uploaded.

## Included tools

| Tool | What it does | Input and output |
|---|---|---|
| `tools/safe_inventory.py` | Counts local file types, sizes, license-name candidates and items needing private review. | Reads filesystem metadata only. JSON output contains aggregate counts and numbered roots, without filenames or paths. |
| `tools/auth_response_audit.py` | Compares response summaries for two synthetic or controlled-test cohorts. | Reads a strict four-column CSV. Reports status-code distributions, median sizes and median latency differences. |

Both tools use the Python standard library. They make no network requests, execute no scanned code and install no dependencies.

## Recovered experimental source

[`historical/wireless/wps_attack.sh`](historical/wireless/wps_attack.sh) preserves a generic wireless-auditing wrapper from the local collection. Its original header attributes generation to Grok. A new guard stops the script before privilege checks, installation or network activity unless execution is explicitly enabled. Local help remains available.

The original workflow can install software, modify wireless interfaces and write recovered credentials to files. It was not tested on hardware. Its original licensing is undocumented and it is excluded from this repository's MIT grant. Read the [archive's provenance, effects and validation notes](historical/wireless/README.md) before considering it.

## Try the synthetic response examples

Python 3.10 or later:

```bash
python3 tools/auth_response_audit.py examples/consistent.csv
python3 tools/auth_response_audit.py examples/discrepant.csv
```

Each file has 20 observations per cohort, generated deterministically for this repository. They contain no accounts, credentials, real traffic or service URLs.

The consistent example has equal distributions and medians. The discrepant example demonstrates a status-distribution distance of `1.0`, a median response-size gap of `600` bytes and a median latency gap of `80` milliseconds. These deliberately obvious differences illustrate the report format; they are not measurements of a real service.

The CSV schema is:

```csv
cohort,status_code,response_bytes,latency_ms
known,200,1200,25
unknown,200,1200,25
```

Only `known` and `unknown` cohort labels are accepted. Use these labels for dummy account fixtures in an application you control. Extra columns and non-finite measurements are rejected. The schema has no fields for identifiers or raw bodies; remove personal data before creating a CSV for this tool.

### Interpreting the response report

The status-distribution distance is half the sum of absolute differences between the two normalized status-code distributions. It ranges from `0` for identical observed proportions to `1` for disjoint observed status codes. Median gaps are absolute differences.

The default minimum of 20 samples per cohort is a reporting convention, not a statistical guarantee. Small samples are marked `insufficient`. A valid input exits successfully even when differences exist: this is a descriptive review aid, not a pass/fail security scanner.

Timing noise, dynamic responses, headers, body text, redirects and test setup can change the interpretation. Equal medians do not prove identical distributions, and this tool does not inspect those omitted response properties. It cannot certify that an application prevents account enumeration.

## Inventory a local directory

```bash
python3 tools/safe_inventory.py ./project-to-review
```

The report omits root names, file names, raw suffixes outside a fixed allowlist, and exception details. It skips symlink entries and common dependency or Git directories. Limits bound traversal to 200,000 files, 500,000 entries and depth 32 per root by default; a stopped or incomplete traversal is marked in the report and exits with code `2`.

The inventory is not a secret detector, malware classifier or license verifier. A filename that resembles `LICENSE` is only a candidate for human review. It does not read file contents or inspect archives. Use it on a stable local directory; it is not a security boundary against an adversarial filesystem. Aggregate counts and sizes may still be confidential, so review reports before sharing them.

## Run the checks

```bash
python3 -m unittest discover -s tests -v
```

The checks exercise privacy of inventory output, symlink and traversal limits, strict CSV validation, rejected personal-data columns, insufficient samples and the two synthetic fixtures. No external services or devices are used.

## Scope and reuse

The broader collection remains subject to individual source, privacy and license review. This repository publishes the files listed here, preserves one explicitly identified experimental archive and links selected upstream projects with attribution. It does not redistribute the entire collection or claim ownership of upstream code.

The new offline tools, fixtures, tests and documentation are provided under the [MIT license and its stated scope](LICENSE). The original archived wireless script is excluded from that grant; external projects retain their own licenses. See [publication scope](docs/PUBLICATION_SCOPE.md) for the exact inclusion rules and [upstream references](docs/UPSTREAM_REFERENCES.md) for source links.
