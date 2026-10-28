# Experimental wireless workflow archive

This directory preserves one generic wireless-auditing script recovered from the maintainer's local collection. **Execution is disabled by default.** It is a historical source artifact, separate from the two newly prepared offline utilities in this repository.

## Provenance and licensing

The original header attributes generation to **Grok for a Kali Linux user**. That statement records the header's provenance claim; it does not establish complete human authorship or copyright ownership. This archive does not attribute original authorship to Ema Curk.

The recovered script did not include an explicit license. **The repository's MIT license does not apply to this original script.** Its presence here should not be interpreted as a grant of unspecified redistribution or incorporation rights. The new documentation remains covered by the repository's documented license scope.

## Publication changes

- Added a guard before the original privilege check, installation commands or network actions. Running the script without an explicit opt-in exits with code `2`.
- Added local `--help` output. Help exits successfully without entering the original workflow.
- Added `umask 077` before the original workflow to restrict permissions on newly created files.
- Removed one private example from an original comment.
- Added ignore rules for known logs, result files and wireless captures.

The original audit methods and operational command sequence were preserved. No attempt was made to repair or improve those methods.

## Inspect without activating the workflow

These commands parse or display the archive without activating its wireless operations:

```bash
bash -n historical/wireless/wps_attack.sh
bash historical/wireless/wps_attack.sh --help
```

The `--enable-experimental-wireless-audit` flag is an explicit acknowledgment that enters the original workflow. It is not a permission grant, a sandbox, or evidence that any selected network is authorized. The workflow then requires elevated privileges. Read and understand the source before considering execution, and restrict any assessment to your own networks or an explicitly authorized scope.

## Effects and known limitations

The original workflow installs packages and a third-party tool, changes a hard-coded wireless interface into monitor mode, invokes wireless-auditing tools, and later attempts to restore networking. Its commands can interrupt connectivity and create files containing network identifiers or recovered credentials.

The script depends on human-readable tool output. Its parsing is fragile, variables are not guaranteed to be initialized on every branch, and cleanup is not guaranteed after an error or interruption. Tool versions, the third-party download location and hardware compatibility were not validated for this publication.

Logs and results are written relative to the current working directory. `umask` protects newly created files; it does not tighten the permissions of an existing file. Use a private working directory and review existing permissions. Ignore rules reduce accidental commits but do not remove secrets from files or protect outputs written outside the repository.

## Validation performed

The publication checks were limited to Bash syntax, local help and the default guard inside a sandbox. No opt-in execution, installation, radio operation, credential recovery or hardware testing was performed. This archive is not presented as a validated recovery product or as a fully licensed original work.
