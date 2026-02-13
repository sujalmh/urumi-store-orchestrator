# Tasks

## WooCommerce Preinstall (Post-Install Job)

- [ ] 1. Add Helm post-install Job to install/activate WooCommerce
  - [x] 1.1 Add `woocommerce-install-job.yaml` hook (post-install only)
  - [x] 1.2 Ensure Job is idempotent (check active, then install/activate)
  - [x] 1.3 Wait for `wp core is-installed` before installing
  - [x] 1.4 Mount WordPress PVC at `/var/www/html`
  - [x] 1.5 Set hook delete policy (hook-succeeded, before-hook-creation)
  - [x] 1.6 Add `wordpress.wpCliImage` to values

- [ ] 2. Backend provisioning waits for Job completion
  - [x] 2.1 Poll Kubernetes Job `woocommerce-install`
  - [x] 2.2 Mark store READY only after Job succeeds
  - [x] 2.3 Fail with clear error on Job failure/timeout

- [x] 3. Verify end-to-end
  - [x] 3.1 Helm lint passes
  - [x] 3.2 Provision store and confirm WooCommerce active
