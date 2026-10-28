# Publication scope

## Included in this release

- Two newly prepared, standard-library Python tools for local metadata inventory and offline response-summary analysis.
- Synthetic CSV fixtures created specifically for this repository.
- Automated checks using temporary local files.
- An anonymized defensive case study based on a static source review.
- Attributed links to identified upstream projects and primary documentation.
- One recovered generic wireless script under `historical/wireless/`, with default execution disabled, documented provenance and an unresolved original license.

The inventory utility adapts the metadata-only review approach used during this publication work. Its public output is intentionally aggregate-only: the private working inventories are not included.

## Material not imported

The wider local research collection was not fully inspected. A later partial recovery made three small candidates available for static review. Their review expanded the attribution notes and selected one generic wireless wrapper for an explicitly documented historical archive. The collection as a whole was not imported.

| Recovered candidate | Static review result | Publication decision |
|---|---|---|
| An older Argus archive | Its README identifies Jasonxtn's upstream project, now hosted at `divinelabio/Argus`. The current upstream has an MIT license; the local archive had no license file and was not mapped to an exact upstream revision. | Add an attributed link in the [reference catalog](UPSTREAM_REFERENCES.md), without copying the archive or claiming its authorship. |
| A wireless automation wrapper | The header attributes generation to Grok; complete human authorship and an original license were not documented. The generic script changes network interfaces with elevated privileges and writes recovered wireless credentials to local text files. | Preserve the source in [an experimental archive](../historical/wireless/README.md), adding a default execution guard and privacy precautions. Do not claim MIT licensing of the original or original authorship by the maintainer. No wireless actions were executed. |
| An automated reporting script | Repeated external submissions used fabricated identifiers and embedded session material. | Exclude the script and session material. No submissions were made. |

These are limited source-review decisions, not a complete security audit of those projects. The remaining original directories and archives have not been imported or represented as fully reviewed.

Real credentials, private account lists, session material, device or account identifiers, real-service impersonation kits and private logs are excluded. Third-party paid material and generated runtime data are not redistributed. The one archived wrapper has a separately documented unresolved license; no other unknown-license code is represented as licensed by this repository.

The operational account-checking prototype considered in the case study is not included. The case study does not name its target or claim that its guessed integration worked.

## Future additions

Each candidate needs a readable source review, provenance and license confirmation, a privacy review and a concrete explanation of its behavior. Published examples should use synthetic inputs. Upstream projects should remain attributed, and any modifications should be described rather than presented as original authorship of the entire project.

This process does not certify that a file is harmless. The inventory reports metadata only, and a lack of filename warnings does not establish that contents are safe or free of secrets.
