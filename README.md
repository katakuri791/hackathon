# Med Assurance motor claims starter

A deliberately poor-looking, functional frontend starter for Eagle Day Challenge B. It models a fictional Moroccan motor-claims experience for a stressed motorist and a broker employee. All people, policies, claims, documents and import results are synthetic. It has no backend and makes no application network requests.

## Run

Requires Python 3. No dependency installation is needed.

```bash
npm run dev
# open http://127.0.0.1:8094
```

Run the source checks:

```bash
npm test
```

The demo stores draft and review state in browser `localStorage`. Use **Réinitialiser la démo** to return to the fixtures.

## What works

- motor-accident intake with injury escalation, draft, review, simulated submission and tracking;
- document metadata without uploading files;
- searchable broker CRM with source and freshness, history, tasks and status control;
- deterministic simulated AI communication draft with source labels and human approval;
- deterministic browser-import scenarios for a new record, duplicate, conflict and interruption;
- source-linked Moroccan assistance/contact directory;
- responsive, keyboard-accessible local frontend and print treatment.

## Deliberate defects to investigate

The purple gradient, glass cards, excessive shadows, decorative statistics, oversized hero, emoji navigation, vague hype and crowded information hierarchy are intentional. They reproduce a stereotypical AI-generated interface without disabling core accessibility or hiding the fact that the experience is mocked.

Candidates should still audit the working experience. Examples include the long broker profile, weak prioritisation, mixed customer/broker mental models, minimal validation, incomplete error recovery, simplistic status controls, and a fixed synthetic data set. Do not assume these are the only issues or that a visual restyle alone solves the challenge.

## Safety and data boundary

- No real customer data, credentials, file bodies or provider account data.
- No API integration, analytics, fonts, CDN assets, calls or e-mails.
- AI generation is a fixed local template; it never decides coverage, liability or payout.
- The real-browser bonus is separate and requires an authorised/test account and human control at OTP, CAPTCHA, consent and any write action.
- Contact numbers are references with distinct purposes. General customer service is not labelled emergency assistance.

Read [CHALLENGE.md](CHALLENGE.md) for the participant task, [BONUS.md](BONUS.md) for the browser-agent extension and [SOURCES.md](SOURCES.md) for provenance.
