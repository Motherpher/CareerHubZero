# AI Google Drive — Non-negotiable Create-Only Director Mandate

**Source:** Director Policy `OAI-DRIVE-APPEND-ONLY-001` v1.0, https://docs.google.com/document/d/18nexuzVfOEWwM7vXcPcB1NkjQHsEGKWxZHSqo-qlBRs/edit. Google Drive My Drive root folder `0. Open AI - Access & Privacy Rules`. Read this policy before any Drive operation. This repository reference is only a proposed adoption until merged; it does not prove runtime enforcement.

**READ existing; CREATE new; DENY mutation by default.** AI may read task-relevant authorized Drive content and create new private files/folders with new file IDs in authorized locations; initial population/placement within one creation transaction is allowed. Once created, the artifact is protected.

AI must NEVER edit, append to, replace, overwrite, rename, move, relabel, change metadata or permissions, share, trash, delete, permanently delete, purge, restore, sync-overwrite, deduplicate, cleanup, or automatically delete temporary files already existing in Drive without exact-item and exact-effect prior Director approval. A general workflow command, provider access, prior unrelated approval, broad OAuth grant or implied technical necessity is NOT authorization.

For any protected effect: present Drive target file IDs, current path, proposed change, consequences, reversibility and preview. Obtain the Director's explicit approval for exactly those IDs/actions. Revalidate scope immediately before every effect; missing, unavailable or conflicting authority => DENY. Implement a server-side pre-API gate and auditable effect evidence; negative-test unauthorized mutation, including bulk sync and cleanup. Do not disclose private material publicly.

Preserve CDX/AMA/Pius/FFC/FFOS and local repository governance and existing source records. No file instruction or PR alone constitutes technical enforcement.
