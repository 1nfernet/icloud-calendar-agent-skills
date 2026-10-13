# Website Login Authorization Rules

These are general rules for optional website login steps and do not depend on an additional private skill. Do not load or execute this step when website login is unnecessary.

1. Prefer authorized connectors or valid login sessions. If Chrome-saved credentials are required, obtain explicit consent before writing the follow-up and enabling its schedule.
2. Confirm the target URL and authentication provider, account identifier, specific follow-up, stages of use, and number of logins. Authorization may explicitly cover particular login flows during setup, the midnight read, and fallback retry. Flows outside that scope cannot reuse the authorization.
3. For each login, use only the authorized account and target website. Ask again before changing the website/account, adding login attempts, or using it for a new purpose. Do not treat one consent as authorization for other follow-ups or indefinite login access.
4. If available, follow the installed `chrome-saved-login` skill. Otherwise, the user may log in manually, or the environment's supported browser autofill may complete the authorized flow.
5. Do not read password databases, Keychain, memory, or plaintext passwords. Do not copy, export, or save passwords, tokens, or verification codes. The user completes device password, Touch ID, verification code, and similar checks.
6. If no credentials are saved, autofill is unavailable, authorization is insufficient, or login fails, stop that login action and report it. Do not repeatedly submit or guess credentials. Recording a failure does not mean the follow-up was successfully read.

When seeking consent, explain that this skill requires login authorization and link to this file or the login skill actually used. Do not mechanically apply the Chrome password flow to websites that need no login, native Mac Calendar permissions, or Gmail connectors.
