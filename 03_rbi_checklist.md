# 03. RBI digital lending checklist: what a borrower can observe

**Purpose.** For each borrower-facing requirement in the RBI Digital Lending Directions, record whether you **observed it in the
flow you walked**. This is a record of observation, not an audit.

## Reading rules (these protect you in the interview)
- Allowed values for *Observed in app?*: **Yes**, **No**, **Could not observe**. Leave blank until you have checked.
- Say **"not observed in the pre-login flow"**, never anything that states or implies a regulatory failure. A requirement you did
  not see may sit behind the login, in a document sent later, or on the lender's website. `make check` rejects verdict wording.
- Most requirements bind the *regulated entity* (the lender), not the app. Where an item can only be seen after sanction, the honest
  answer is *Could not observe*.
- **Read the source yourself** and update *Verified vs source* (date and initials). The paragraph numbers below were extracted from the
  RBI notice by a tool and **must be confirmed against the text**:
  - Reserve Bank of India (Digital Lending) Directions, 2025, dated 8 May 2025: <https://www.rbi.org.in/scripts/NotificationUser.aspx?Id=12848&Mode=0>
  - Key Facts Statement circular DOR.STR.REC.13/13.03.00/2024-25, 15 April 2024 (defines APR and KFS contents): <https://rbidocs.rbi.org.in/rdocs/notification/PDFs/CIRCULARKFS1504242AE2500BAF494C2A82442B0B642705C1.PDF>

> **Terminology note.** The Directions do not use the term "look-up period". The borrower's exit right is the **cooling-off
> period** (para 10). Use that word, or an interviewer who has read the text will notice.

## Checklist

<!-- RBI:START -->
| # | Requirement (paraphrased) | RBI ref | Observed in app? | Screenshot | Note | Verified vs source |
|---|---|---|---|---|---|---|
| 1 | Key Fact Statement (KFS) is given **before the loan contract is executed** | Directions para 8(i); KFS circular | Could not observe |  | Evidence stops at the mobile-number gate; the KFS is given before contract execution, after it | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 2 | The KFS states the **APR** (annual percentage rate) | Directions para 4(i); KFS circular | Could not observe | 15; 01 | APR is a KFS item (after the gate). The footer APR page lists four documents (15); the calculator output on the product page shows no APR (01). Documents not opened | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 3 | The KFS shows the **nodal grievance officer's** contact details | Directions para 11(ii) | Could not observe |  | KFS not reachable before the gate | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 4 | Borrower has an explicit **cooling-off exit**: repay principal and proportionate APR, no penalty; length set by the lender's Board, at least one day | Directions para 10(i) | Could not observe | 01 | No cooling-off wording seen in the product page text; the page states zero foreclosure charges, which is a different right. Contract terms are post-gate | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 5 | Any one-time processing fee kept on a cooling-off exit is **disclosed upfront in the KFS** | Directions para 10(ii) | Could not observe |  | Depends on the KFS (post-gate) | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 6 | **Penal charges** are disclosed as the separate circular requires | Directions para 8(ii); circular of 18 Aug 2023 | Could not observe | 12; 13 | A Schedule Of Charges page exists (12, 13); the personal-loan document was not opened | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 7 | Data is collected only with **prior, explicit consent**, and the **purpose is disclosed at each stage** | Directions para 12(i), 12(iii) | Could not observe | 07 | First data request has an unticked consent checkbox, with purpose stated as use of KYC details from CERSAI/UIDAI; later stages not seen, so 'at each stage' cannot be assessed | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 8 | Borrower can **deny or withhold** specific data, restrict third-party sharing, revoke consent and request deletion | Directions para 12(ii) | Could not observe |  | Consent controls after the gate not seen | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 9 | App does **not ask for access** to files and media, contact list, call logs or telephony; camera, microphone or location only as a one-time, consented step for onboarding or KYC | Directions para 12(i) | Could not observe |  | Web flow only; the mobile app was not used, so device-permission prompts were not seen | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 10 | **Explicit consent** before personal information is shared with a third party (unless law requires it) | Directions para 12(iv) | Could not observe |  | Third-party sharing consent not seen before the gate | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 11 | A comprehensive **privacy policy** is available and lists permitted third-party collectors | Directions para 14(i)-(ii) | Yes | 10 | Privacy Policy link seen in the footer strip. Availability only: the policy text and its list of third-party collectors were not read | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 12 | Loan is **disbursed to the borrower's own bank account**, not a third party or lending-service-provider account | Directions para 9(i) | Could not observe | 05 | Step 4 says 'Link your bank account where you want to receive the funds' (a stated step); the disbursal itself is post-gate | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 13 | **Repayment goes directly** to the lender's account, with no pass-through or pool account | Directions para 9(ii) | Could not observe |  | Repayment flow is post-gate | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 14 | No fee is **charged to the borrower** on behalf of a lending service provider | Directions para 9(iv) | Could not observe |  | Fee flows are not visible before the gate | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 15 | Signed documents (KFS, sanction letter, terms, privacy policy) **reach the borrower's verified email or SMS** at execution | Directions para 8(iii) | Could not observe |  | Documents are sent at contract execution (post-gate) | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 16 | The **lender is named** and any **lending service provider** involved is disclosed (lender's site lists its products, providers and apps) | Directions para 8(iv) | Yes | 17; 09 | Lender is named throughout; the Digital Lending Partners page lists the partner entities under Personal Loans (17). Each entry's document was not opened | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 17 | Grievance officer details are **prominent** on the website and app | Directions para 11(ii) | Yes | 16; 09 | Officer contact details appear on the Digital Lending Partners page (text, no screenshot kept because it names an individual); the product page footer links to Grievance Redressal (16). Not shown on the product page or at the gate. App not checked | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 18 | A **complaint facility** is available inside the app or website | Directions para 11(iii) | Yes | 03; 04; 16 | 'Raise a complaint' in the page header (03, 04); the Grievance Redressal page lists a Grievance Form (16) | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 19 | Borrower is told how to **escalate to the RBI complaint portal** if a complaint is rejected or unanswered for 30 days | Directions para 11(iv) | Could not observe | 16 | The grievance page lists an 'Integrated Ombudsman Scheme' document (16); the escalation wording on a rejected complaint was not seen | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 20 | **No automatic credit-limit increase** without an explicit, recorded borrower request (credit-line products only) | Directions para 7(ii) | Could not observe |  | Product page says more loans can be obtained on demand; how limits are raised is not observable before login | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 21 | If the app shows **offers from several lenders**: each offer shows lender, amount, tenor, APR, monthly repayment, penal charges and a KFS link (applies from 1 Nov 2025) | Directions para 6 | Could not observe | 17 | Single-lender flow seen; the partner page lists third-party applications that may fall under this item | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
| 22 | Age, occupation and income are **collected before lending** and kept on record | Directions para 7(i) | Could not observe | 14 | The eligibility calculator takes income and obligations (14), but recording of age, occupation and income happens in the application (post-gate) | 2026-10-17 Claude: para exists, opening text quoted from rbi.org.in; author re-read pending |
<!-- RBI:END -->

**About the *Verified vs source* column.** Every paragraph reference was checked on 2026-10-17 against the RBI notice text: each paragraph exists with
the number given and its opening words were quoted. That is a check of the references, **not** a reading of the full requirement, so the cell says
"author re-read pending". Replace it with your date and initials once you have read the paragraph yourself, or run `make verify-rbi INITIALS=XX` after reading all of them (it stamps only unsigned rows and refuses to run without `--i-have-read-the-directions`).

## How to use the result
- Items you could not observe belong in the PRD's *Compliance* section as **things the design must preserve**, not as findings.
- Items observed as **Yes** are evidence that the current flow already carries the disclosure; a fix must not remove it.
- Items observed as **No** in the pre-login flow become questions to ask the compliance team, never claims.
