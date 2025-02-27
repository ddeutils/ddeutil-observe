# Authentication

For this observe application will implement the RBAC approach for control policy
authorize.

## Policies

A policies will contain `view`, `create`, `update`, and `delete`. These policies
will auto create when the route was created from application provisioning.

### Observe Page

- matrix.view
- matrix.update

- action.view
- action.create
- action.update
- action.delete

### Admin Page

- user.view
- user.create
- user.update
- user.delete

- role.view
- role.create
- role.update
- role.delete
